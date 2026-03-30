import asyncio
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace


class _HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class _APIRouter:
    def post(self, *_args, **_kwargs):
        def _decorator(func):
            return func

        return _decorator


def _depends(value):
    return value


class _FakeDocIn:
    def __init__(self, title: str, template_id: int, case_facts: dict):
        self.title = title
        self.template_id = template_id
        self.case_facts = case_facts


class _FakeDocumentCreate:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content


class _FakeGeneratedDocumentResponse:
    pass


class _FakeGhostSuggestRequest:
    pass


class _FakeGhostSuggestResponse:
    def __init__(self, suggestion: str):
        self.suggestion = suggestion


def _load_documents_endpoint_module():
    module_path = Path(__file__).resolve().parents[1] / "app" / "api" / "v1" / "endpoints" / "documents.py"

    # third-party stubs
    fastapi_mod = ModuleType("fastapi")
    fastapi_mod.APIRouter = _APIRouter
    fastapi_mod.Depends = _depends
    fastapi_mod.HTTPException = _HTTPException

    sqlalchemy_mod = ModuleType("sqlalchemy")
    sqlalchemy_orm_mod = ModuleType("sqlalchemy.orm")
    sqlalchemy_orm_mod.Session = object

    # app package stubs
    app_mod = ModuleType("app")
    crud_mod = ModuleType("app.crud")
    models_mod = ModuleType("app.models")
    models_models_mod = ModuleType("app.models.models")
    models_models_mod.User = object

    schemas_pkg_mod = ModuleType("app.schemas")
    schemas_document_mod = ModuleType("app.schemas.document")
    schemas_document_mod.DocumentGenerate = _FakeDocIn
    schemas_document_mod.GhostSuggestRequest = _FakeGhostSuggestRequest
    schemas_document_mod.GhostSuggestResponse = _FakeGhostSuggestResponse
    schemas_document_mod.GeneratedDocumentResponse = _FakeGeneratedDocumentResponse
    schemas_document_mod.DocumentCreate = _FakeDocumentCreate
    schemas_pkg_mod.document = schemas_document_mod

    api_mod = ModuleType("app.api")
    deps_mod = ModuleType("app.api.deps")
    deps_mod.get_db = lambda: None
    deps_mod.get_current_active_user = lambda: None
    api_mod.deps = deps_mod

    doc_gen_pkg = ModuleType("app.agents.document_generator")
    assembly_mod = ModuleType("app.agents.document_generator.assembly_engine")
    ghost_typing_mod = ModuleType("app.agents.document_generator.ghost_typing")
    agentic_policy_mod = ModuleType("app.agents.document_generator.agentic_policy")
    legal_validation_mod = ModuleType("app.agents.document_generator.legal_validation")

    async def _assemble_document(template, case_facts, title):
        return f"generated::{title}::{template}::{bool(case_facts.get('retrieved_legal_context'))}"

    async def _suggest_next_sentence(current_content, case_facts, doc_type):
        return "stub"

    assembly_mod.assembly_engine = SimpleNamespace(assemble_document=_assemble_document)
    ghost_typing_mod.ghost_typing_engine = SimpleNamespace(suggest_next_sentence=_suggest_next_sentence)
    agentic_policy_mod.should_escalate_agentic = lambda **kwargs: {"escalate": False, "reasons": [], "step_budget": 1}
    legal_validation_mod.build_clause_traceability = lambda content, sources: [{"clause_id": "C1", "text": content}]
    legal_validation_mod.build_citation_checks = lambda content: {"total_clauses": 1, "clauses_with_citations": 1}
    legal_validation_mod.build_validation_report = lambda content, sources: {"passed": True, "issue_count": 0, "issues": []}
    legal_validation_mod.compute_confidence_score = lambda report, checks: 0.95

    integrations_pkg = ModuleType("app.integrations")
    ik_pkg = ModuleType("app.integrations.indiankanoon")
    processor_mod = ModuleType("app.integrations.indiankanoon.data_processor")

    class _FakeProcessor:
        def __init__(self, db):
            self.db = db

        async def process_document(self, _doc_id):
            return None

        async def close(self):
            return None

    processor_mod.IndianKanoonDataProcessor = _FakeProcessor

    services_pkg = ModuleType("app.services")
    retrieval_service_mod = ModuleType("app.services.retrieval_service")

    class _FakeRetriever:
        def invoke(self, _query):
            return []

    class _FakeRetrievalService:
        def get_persistent_retriever(self, k=5):
            return _FakeRetriever()

    retrieval_service_mod.RetrievalService = _FakeRetrievalService

    # attach required attributes
    crud_mod.template = SimpleNamespace(get=lambda db, id: SimpleNamespace(content="TEMPLATE", title="Template"))
    crud_mod.document = SimpleNamespace(
        create_with_owner=lambda db, obj_in, owner_id: SimpleNamespace(
            id=99,
            title=obj_in.title,
            content=obj_in.content,
            owner_id=owner_id,
            created_at="now",
            updated_at="now",
        )
    )

    app_mod.crud = crud_mod

    modules = {
        "fastapi": fastapi_mod,
        "sqlalchemy": sqlalchemy_mod,
        "sqlalchemy.orm": sqlalchemy_orm_mod,
        "app": app_mod,
        "app.crud": crud_mod,
        "app.models": models_mod,
        "app.models.models": models_models_mod,
        "app.schemas": schemas_pkg_mod,
        "app.schemas.document": schemas_document_mod,
        "app.api": api_mod,
        "app.api.deps": deps_mod,
        "app.agents": ModuleType("app.agents"),
        "app.agents.document_generator": doc_gen_pkg,
        "app.agents.document_generator.assembly_engine": assembly_mod,
        "app.agents.document_generator.ghost_typing": ghost_typing_mod,
        "app.agents.document_generator.agentic_policy": agentic_policy_mod,
        "app.agents.document_generator.legal_validation": legal_validation_mod,
        "app.integrations": integrations_pkg,
        "app.integrations.indiankanoon": ik_pkg,
        "app.integrations.indiankanoon.data_processor": processor_mod,
        "app.services": services_pkg,
        "app.services.retrieval_service": retrieval_service_mod,
    }

    old = {name: sys.modules.get(name) for name in modules}
    try:
        sys.modules.update(modules)
        spec = importlib.util.spec_from_file_location("documents_endpoint_under_test", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module
    finally:
        for name, previous in old.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def test_generate_document_returns_retrieval_sources_when_context_available():
    module = _load_documents_endpoint_module()

    captured = {}

    async def _assemble_document(template, case_facts, title):
        captured["case_facts"] = case_facts
        return "generated-body"

    module.assembly_engine.assemble_document = _assemble_document
    module._fetch_grounded_legal_context = lambda query, k=5: (
        "Context block",
        [{"title": "Case A", "source": "SCC", "url": "https://example.test", "id": "1"}],
    )

    result = asyncio.run(
        module.generate_document(
            db=object(),
            doc_in=_FakeDocIn(title="My Draft", template_id=1, case_facts={"query": "s 138 ni act"}),
            current_user=SimpleNamespace(id=7),
        )
    )

    assert isinstance(result["retrieval_sources"], list)
    assert result["retrieval_sources"][0]["title"] == "Case A"
    assert captured["case_facts"]["retrieved_legal_context"] == "Context block"
    assert result["validation_report"]["passed"] is True
    assert result["confidence_score"] == 0.95
    assert result["agentic_decision"]["escalate"] is False


def test_generate_document_returns_empty_retrieval_sources_when_query_empty():
    module = _load_documents_endpoint_module()

    async def _assemble_document(template, case_facts, title):
        return "generated-body"

    module.assembly_engine.assemble_document = _assemble_document
    module._fetch_grounded_legal_context = lambda query, k=5: (
        "Context block should be ignored",
        [{"title": "Case A"}],
    )

    result = asyncio.run(
        module.generate_document(
            db=object(),
            doc_in=_FakeDocIn(title="My Draft", template_id=1, case_facts={}),
            current_user=SimpleNamespace(id=7),
        )
    )

    assert result["retrieval_sources"] == []
    assert "citation_checks" in result
    assert "agentic_decision" in result
