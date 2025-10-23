
import json
from langgraph.graph import StateGraph, END
from app.agents.orchestrator.state_manager import DroitAgentState
from app.agents.orchestrator.agent_nodes import (
    get_template_node,
    document_generator_node,
    legal_research_node,
)
from app.schemas.workflow import WorkflowDefinition
from app.agents.orchestrator.execution_monitor import execution_monitor

class WorkflowEngine:
    def __init__(self, workflow_definition: WorkflowDefinition):
        self.workflow_definition = workflow_definition
        self.graph = self._build_graph()

    def _get_node_by_name(self, name: str):
        # This is a simple mapping. In a real application, you would have a more robust way to resolve nodes.
        if name == "get_template":
            return get_template_node
        elif name == "document_generator":
            return document_generator_node
        elif name == "legal_research":
            return legal_research_node
        else:
            raise ValueError(f"Node {name} not found")

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(DroitAgentState)

        # Add nodes
        for node_def in self.workflow_definition.nodes:
            workflow.add_node(node_def.name, self._get_node_by_name(node_def.name))
            if node_def.entry:
                workflow.set_entry_point(node_def.name)

        # Add edges
        for edge_def in self.workflow_definition.edges:
            if edge_def.condition:
                workflow.add_conditional_edges(
                    edge_def.from_node,
                    lambda state: edge_def.to_node if state.get(edge_def.condition) else END,
                    {edge_def.to_node: edge_def.to_node, END: END}
                )
            else:
                workflow.add_edge(edge_def.from_node, edge_def.to_node)
        
        return workflow.compile()

    def run(self, input_data: dict) -> dict:
        execution_id = execution_monitor.start_execution(self.workflow_definition.name)
        
        try:
            result = self.graph.invoke(input_data)
            execution_monitor.end_execution(execution_id, "completed")
            return result
        except Exception as e:
            execution_monitor.end_execution(execution_id, "failed")
            raise e
