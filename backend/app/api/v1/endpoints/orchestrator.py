
from fastapi import APIRouter, Body, HTTPException
from app.agents.orchestrator.workflow_engine import WorkflowEngine
from app.agents.orchestrator.execution_monitor import execution_monitor
from app.schemas.workflow import WorkflowDefinition
import json

router = APIRouter()


@router.post("/run/{workflow_name}")
async def run_orchestrator(workflow_name: str, payload: dict = Body(...)):
    """
    Run a specific DroitDraft workflow.
    """
    try:
        with open(f"app/agents/orchestrator/workflow_definitions/{workflow_name}.json") as f:
            workflow_def_dict = json.load(f)
        
        workflow_def = WorkflowDefinition(**workflow_def_dict)
        engine = WorkflowEngine(workflow_def)
        result = engine.run(payload)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        return {"error": str(e)}


@router.get("/history/{execution_id}")
async def get_execution_history(execution_id: str):
    """
    Get the execution history of a workflow.
    """
    history = execution_monitor.get_execution_history(execution_id)
    if not history:
        raise HTTPException(status_code=404, detail="Execution not found")
    return history
