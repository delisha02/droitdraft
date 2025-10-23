
from fastapi import APIRouter, Body
from app.agents.orchestrator.graph_config import run_workflow

router = APIRouter()


@router.post("/run")
async def run_orchestrator(payload: dict = Body(...)):
    """
    Run the DroitDraft agent orchestrator.
    """
    try:
        result = run_workflow(payload)
        return result
    except Exception as e:
        return {"error": str(e)}
