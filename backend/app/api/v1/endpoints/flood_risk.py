from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.risk_service import get_current_flood_risk, get_risk_why_explanation, DEMO_RISK_ID
from app.schemas.flood import FloodRiskOut, FloodRiskWhyOut

router = APIRouter()


@router.get("/flood-risk/current", response_model=FloodRiskOut, tags=["Flood Risk"])
async def current_flood_risk(db: Session = Depends(get_db)):
    return get_current_flood_risk(db)


@router.get("/flood-risk/current/why", response_model=FloodRiskWhyOut, tags=["Flood Risk"])
async def flood_risk_why(db: Session = Depends(get_db)):
    return get_risk_why_explanation(db, DEMO_RISK_ID)
