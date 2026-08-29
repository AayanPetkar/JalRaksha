from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.alert_service import list_active_alerts
from app.schemas.alert import AlertOut

router = APIRouter()


@router.get("/alerts", response_model=List[AlertOut], tags=["Alerts"])
async def get_alerts(db: Session = Depends(get_db)):
    """Active alerts relevant to the demo user. Simulated alerts are
    clearly tagged via source_tag and are never presented as official
    government warnings."""
    return list_active_alerts(db)
