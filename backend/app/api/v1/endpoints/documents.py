import logging
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.models.models import User  # Import User explicitly
from app.schemas import document as schemas_document
from app.schemas.document import DocumentGenerate, GhostSuggestRequest, GhostSuggestResponse
from app.api import deps
from app.agents.document_generator.assembly_engine import assembly_engine
from app.agents.document_generator.agentic_policy import should_escalate_agentic
from app.agents.document_generator.legal_validation import (
    build_citation_checks,
    build_clause_traceability,
    build_validation_report,
    compute_confidence_score,
)
from app.agents.document_generator.ghost_typing import ghost_typing_engine
from app.integrations.indiankanoon.data_processor import IndianKanoonDataProcessor
from app.services.retrieval_service import RetrievalService

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_retrieval_query(case_facts: dict) -> str:
    """
    Build a compact legal-retrieval query from available user and extracted facts.
    """
    query_parts = [
        case_facts.get("prompt"),
        case_facts.get("query"),
        case_facts.get("instructions"),
        case_facts.get("issue"),
        case_facts.get("statute"),
        case_facts.get("location"),
    ]
    return " ".join([str(p).strip() for p in query_parts if p]).strip()


def _select_retrieval_strategy(query: str, case_facts: dict) -> dict:
    """
    Route retrieval mode based on query/facts complexity.
    """
    if not query:
        return {"strategy": "dense", "k": 0, "reason": "empty_query"}

    token_count = len(query.split())
    has_multiple_files = len(case_facts.get("file_ids", []) or []) > 1
    citation_like = bool(
        re.search(r"\b(section|article)\s+\d+", query, re.IGNORECASE)
        or re.search(r"\bact,\s*\d{4}\b", query, re.IGNORECASE)
    )

    if citation_like or has_multiple_files or token_count > 18:
        return {"strategy": "hybrid", "k": 8, "reason": "complex_or_citation_heavy_query"}

    return {"strategy": "dense", "k": 5, "reason": "default_dense_path"}


def _fetch_grounded_legal_context(query: str, strategy: str = "dense", k: int = 5) -> tuple[str, list[dict]]:
    """
    Retrieve supporting legal snippets and source metadata for generation grounding.
    Compatible with both RetrievalService APIs:
    - retrieve_documents(query, strategy, k)
    - get_persistent_retriever(k).invoke(query)
    """
    if not query:
        return "", []

    try:
        retrieval_service = RetrievalService()

        # Prefer richer API if present
        if hasattr(retrieval_service, "retrieve_documents"):
            docs = retrieval_service.retrieve_documents(query=query, strategy=strategy, k=k)
        else:
            retriever = retrieval_service.get_persistent_retriever(k=k)
            docs = retriever.invoke(query)
    except Exception as e:
        logger.warning("Retrieval failed (strategy=%s, k=%s): %s", strategy, k, e)
        return "", []

    context_blocks = []
    sources = []
    for idx, doc in enumerate(docs or []):
        content = (getattr(doc, "page_content", "") or "").strip()
        if not content:
            continue

        snippet = content[:1200]
        metadata = getattr(doc, "metadata", {}) or {}
        title = metadata.get("title") or "Unknown Title"
        source = metadata.get("source") or "Unknown Source"
        url = metadata.get("url")

        header = f"Source {idx + 1}: {title} ({source})"
        if url:
            header += f" - {url}"

        context_blocks.append(f"{header}\n{snippet}")
        sources.append(
            {
                "title": title,
                "source": source,
                "url": url,
                "id": metadata.get("doc_id") or metadata.get("tid"),
            }
        )

    return "\n\n".join(context_blocks), sources


@router.post("/generate", response_model=schemas_document.GeneratedDocumentResponse)
async def generate_document(
    *,
    db: Session = Depends(deps.get_db),
    doc_in: DocumentGenerate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Generate a new document.
    """
    template = crud.template.get(db, id=doc_in.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 1) Start with user facts
    file_ids = doc_in.case_facts.get("file_ids", [])
    merged_facts = doc_in.case_facts.copy()

    # 2) Inject current date for automatic placeholder filling
    from datetime import datetime
    today_str = datetime.now().strftime("%B %d, %Y")
    merged_facts["today's_date"] = today_str
    merged_facts["drafting_date"] = today_str
    merged_facts["current_date"] = today_str

    # 3) Optional evidence extraction
    if file_ids:
        from app.agents.document_processor.text_extractor import TextExtractor
        from app.agents.document_processor.llm_extractor import llm_extractor
        from app.services import storage

        extractor = TextExtractor()
        all_extracted_text = ""

        for fid in file_ids:
            local_path = None
            try:
                local_path = storage.download_file(fid)
                text = extractor.extract_text(local_path)
                if text:
                    all_extracted_text += f"\n--- Evidence from {fid} ---\n{text}\n"
            except Exception as e:
                logger.warning("Failed to process evidence file %s: %s", fid, e)
            finally:
                if local_path:
                    storage.delete_local_file(local_path)

        if all_extracted_text:
            merged_facts["evidence_text"] = all_extracted_text
            evidence_facts = await llm_extractor.extract(all_extracted_text)
            for kf, vf in evidence_facts.items():
                if kf not in merged_facts or not merged_facts[kf]:
                    merged_facts[kf] = vf

    # 4) Retrieve supporting legal context
    retrieval_query = _build_retrieval_query(merged_facts)
    retrieval_strategy = _select_retrieval_strategy(retrieval_query, merged_facts)
    legal_context, legal_sources = _fetch_grounded_legal_context(
        retrieval_query,
        strategy=retrieval_strategy["strategy"],
        k=retrieval_strategy["k"],
    )

    if legal_context:
        merged_facts["retrieved_legal_context"] = legal_context
        merged_facts["retrieved_legal_sources"] = legal_sources

    # 5) Deterministic generation pass
    try:
        generated_content = await assembly_engine.assemble_document(
            template=template.content,
            case_facts=merged_facts,
            title=doc_in.title,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    retrieval_sources = legal_sources if retrieval_query else []
    clause_traceability = build_clause_traceability(generated_content, retrieval_sources)
    citation_checks = build_citation_checks(generated_content)
    validation_report = build_validation_report(generated_content, retrieval_sources)
    confidence_score = compute_confidence_score(validation_report, citation_checks)

    agentic_decision = should_escalate_agentic(
        case_facts=merged_facts,
        retrieval_sources=retrieval_sources,
        validation_report=validation_report,
        confidence_score=confidence_score,
    )
    agentic_decision["retrieval_strategy"] = retrieval_strategy
    agentic_decision["executed"] = False
    agentic_decision["attempts"] = 0
    agentic_decision["fallback_to_deterministic"] = False

    # 6) Optional bounded remediation pass
    if agentic_decision.get("escalate"):
        max_attempts = int(agentic_decision.get("step_budget", 1))
        remediation_facts = merged_facts.copy()
        remediation_facts["agentic_repair_instructions"] = (
            "Prioritize legal citations and resolve validation issues from prior draft."
        )

        for _ in range(max_attempts):
            agentic_decision["executed"] = True
            agentic_decision["attempts"] += 1
            try:
                regenerated_content = await assembly_engine.assemble_document(
                    template=template.content,
                    case_facts=remediation_facts,
                    title=doc_in.title,
                )

                regenerated_citation_checks = build_citation_checks(regenerated_content)
                regenerated_validation_report = build_validation_report(regenerated_content, retrieval_sources)
                regenerated_confidence_score = compute_confidence_score(
                    regenerated_validation_report, regenerated_citation_checks
                )

                is_improved = (
                    regenerated_confidence_score > confidence_score
                    or (
                        regenerated_validation_report.get("passed")
                        and not validation_report.get("passed")
                    )
                )

                if is_improved:
                    generated_content = regenerated_content
                    citation_checks = regenerated_citation_checks
                    validation_report = regenerated_validation_report
                    confidence_score = regenerated_confidence_score
                    clause_traceability = build_clause_traceability(generated_content, retrieval_sources)

            except Exception as e:
                logger.warning("Agentic remediation failed; falling back to deterministic: %s", e)
                agentic_decision["fallback_to_deterministic"] = True
                break

    # 7) Persist final content (after any remediation)
    doc_create = schemas_document.DocumentCreate(title=doc_in.title, content=generated_content)
    document = crud.document.create_with_owner(db, obj_in=doc_create, owner_id=current_user.id)

    # 8) Response
    return {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "owner_id": document.owner_id,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "retrieval_sources": retrieval_sources,
        "clause_traceability": clause_traceability,
        "validation_report": validation_report,
        "confidence_score": confidence_score,
        "citation_checks": citation_checks,
        "agentic_decision": agentic_decision,
    }


@router.post("/ghost-suggest", response_model=GhostSuggestResponse)
async def ghost_suggest(
    *,
    request: GhostSuggestRequest,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Predict the next sentence for the document.
    """
    suggestion = await ghost_typing_engine.suggest_next_sentence(
        current_content=request.current_content,
        case_facts=request.case_facts,
        doc_type=request.doc_type,
    )
    return GhostSuggestResponse(suggestion=suggestion)


@router.post("/indiankanoon/process/{doc_id}", response_model=dict)
async def process_indian_kanoon_document(
    *,
    db: Session = Depends(deps.get_db),
    doc_id: str,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Fetch, process, and store a document from Indian Kanoon.
    """
    processor = IndianKanoonDataProcessor(db)
    try:
        await processor.process_document(doc_id)
        return {"message": f"Document {doc_id} processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await processor.close()
