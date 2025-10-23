
from app.api import deps
from app import crud
from app.agents.orchestrator.state_manager import DroitAgentState
from app.agents.document_generator.assembly_engine import assembly_engine
from app.integrations.indiankanoon.client import IndianKanoonClient
from app.integrations.indiankanoon.query_builder import IndianKanoonQueryBuilder

async def get_template_node(state: DroitAgentState) -> DroitAgentState:
    """Gets the template content from the database."""
    db = next(deps.get_db())
    template = crud.template.get(db, id=state["template_id"])
    if not template:
        state["error"] = "Template not found"
    else:
        state["template_content"] = template.content
        state["document_title"] = template.title
    return state

async def document_generator_node(state: DroitAgentState) -> DroitAgentState:
    """Generates the document using the assembly engine."""
    if state.get("error"):
        return state
        
    try:
        generated_document = await assembly_engine.assemble_document(
            template=state["template_content"],
            case_facts=state["case_facts"],
            title=state["document_title"]
        )
        state["generated_document"] = generated_document
    except Exception as e:
        state["error"] = f"Error in document generation: {e}"
    return state

async def legal_research_node(state: DroitAgentState) -> DroitAgentState:
    """Performs legal research based on the research query."""
    if state.get("error") or not state.get("research_query"):
        return state

    try:
        client = IndianKanoonClient()
        query_builder = IndianKanoonQueryBuilder(state["research_query"])
        search_results = await client.search(query_builder)
        state["research_results"] = search_results
        await client.close()
    except Exception as e:
        state["error"] = f"Error in legal research: {e}"
    return state
