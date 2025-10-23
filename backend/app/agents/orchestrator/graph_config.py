
from app.agents.orchestrator.workflow_builder import build_workflow

# Build the workflow
app = build_workflow()

def run_workflow(input_data: dict):
    """Runs the DroitDraft workflow with the given input data."""
    return app.invoke(input_data)
