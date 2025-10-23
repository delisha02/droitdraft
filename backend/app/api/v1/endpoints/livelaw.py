
from fastapi import APIRouter
from app.integrations.livelaw.scheduler import scrape_livelaw_task

router = APIRouter()


@router.post("/scrape", status_code=202)
async def scrape_livelaw():
    """
    Trigger the LiveLaw scraping task.
    """
    scrape_livelaw_task.delay()
    return {"message": "LiveLaw scraping task triggered."}
