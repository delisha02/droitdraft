
from langgraph.graph import StateGraph, END
from app.agents.orchestrator.state_manager import DroitAgentState
from app.agents.orchestrator.agent_nodes import (
    get_template_node,
    document_generator_node,
    legal_research_node,
)

def build_workflow():
    """Builds the LangGraph workflow for DroitDraft."""
    workflow = StateGraph(DroitAgentState)

    # Add nodes
    workflow.add_node("get_template", get_template_node)
    workflow.add_node("document_generator", document_generator_node)
    workflow.add_node("legal_research", legal_research_node)

    # Set entry point
    workflow.set_entry_point("get_template")

    # Add edges
    workflow.add_edge("get_template", "document_generator")
    workflow.add_conditional_edges(
        "document_generator",
        lambda state: "legal_research" if state.get("research_query") else END,
        {
            "legal_research": "legal_research",
            END: END
        }
    )
    workflow.add_edge("legal_research", END)

    return workflow.compile()
