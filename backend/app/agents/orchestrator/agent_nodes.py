
from app.api import deps
from app import crud
from app.agents.orchestrator.state_manager import DroitAgentState
from app.agents.document_generator.assembly_engine import assembly_engine
from app.integrations.indiankanoon.client import IndianKanoonClient
from app.integrations.indiankanoon.query_builder import IndianKanoonQueryBuilder
from app.agents.document_processor.ner_engine import extract_entities
from app.agents.document_processor.fact_structurer import FactStructurer
from app.schemas.case_facts import CaseFact # Import CaseFact

async def document_processor_node(state: DroitAgentState) -> DroitAgentState:
    """
    Processes the initial query to extract entities and structure facts.
    """
    if not state.get("query"):
        # Explicitly raise a ValueError if query is missing
        raise ValueError("Input query is missing.")

    # Simulate entity extraction
    extracted_entities = extract_entities(state["query"])
    
    # Simulate fact structuring
    fact_structurer = FactStructurer()
    # Using a dummy document_id and type for now, as they are not extracted from query
    structured_facts: CaseFact = fact_structurer.structure_facts(
        extracted_entities, 
        document_id="query_document", 
        document_type="natural_language_query"
    )
    
    state["case_facts"] = structured_facts
    state["template_id"] = 1 # Template ID for the test
    state["research_query"] = "Maharashtra Rent Control Act" # Example research query
        
    return state

async def get_template_node(state: DroitAgentState) -> DroitAgentState:
    """Gets the template content from the database."""
    template_id = state["template_id"] # Access directly, let KeyError propagate if not set
    
    db = next(deps.get_db())
    template = crud.template.get(db, id=template_id) 
    if not template:
        # If template not found, raise an exception, let WorkflowEngine handle
        raise ValueError(f"Template with ID {template_id} not found")
    else:
        state["template_content"] = template.content
        state["document_title"] = template.title
    return state
async def document_generator_node(state: DroitAgentState) -> DroitAgentState:
    """Generates the document using the assembly engine."""
    # Ensure necessary keys are present
    if not state.get("template_content"):
        raise ValueError("Template content is missing for document generation.")
    if not state.get("case_facts"):
        raise ValueError("Case facts are missing for document generation.")
    if not state.get("document_title"):
        raise ValueError("Document title is missing for document generation.")
        
    generated_document = await assembly_engine.assemble_document(
        template=state["template_content"],
        case_facts=state["case_facts"],
        title=state["document_title"],
        research_results=state.get("research_results", []) # Pass research results if available
    )
    state["generated_document"] = generated_document
    return state

async def legal_research_node(state: DroitAgentState) -> DroitAgentState:
    """Performs legal research based on the research query."""
    if not state.get("research_query"):
        raise ValueError("Research query is missing from state.")

    client = IndianKanoonClient()
    query_builder = IndianKanoonQueryBuilder(state["research_query"])
    search_results = await client.search(query_builder)
    state["research_results"] = search_results
    await client.close()
    return state

