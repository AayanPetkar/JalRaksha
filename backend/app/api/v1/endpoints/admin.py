import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import admin_simulation_service, admin_overview_service, report_service
from app.services.risk_service import get_current_flood_risk
from app.schemas.flood import FloodRiskOut
from app.schemas.admin import AdminOverviewOut, DistressEventOut
from app.schemas.report import CitizenReportOut

router = APIRouter()


@router.post("/admin/simulate-flood", response_model=FloodRiskOut, tags=["Admin - Demo Simulation"])
async def simulate_flood(db: Session = Depends(get_db)):
    """LOW -> CRITICAL. Escalates the seeded demo flood risk, environmental
    readings, road conditions, and issues a clearly-labeled simulated alert.
    """
    admin_simulation_service.simulate_flood(db)
    return get_current_flood_risk(db)


@router.post("/admin/simulate-normal", response_model=FloodRiskOut, tags=["Admin - Demo Simulation"])
async def simulate_normal(db: Session = Depends(get_db)):
    """Restores the exact Phase A baseline (LOW risk, score 20, all roads open,
    no active flood/alert)."""
    admin_simulation_service.simulate_normal(db)
    return get_current_flood_risk(db)


@router.post("/admin/simulate-blocked-road", tags=["Admin - Demo Simulation"])
async def simulate_blocked_road(db: Session = Depends(get_db)):
    """Blocks the primary demo route (Route A)."""
    return admin_simulation_service.simulate_blocked_road(db)


@router.get("/admin/overview", response_model=AdminOverviewOut, tags=["Admin"])
async def admin_overview(db: Session = Depends(get_db)):
    return admin_overview_service.get_admin_overview(db)


@router.get("/admin/distress-signals", response_model=List[DistressEventOut], tags=["Admin"])
async def admin_distress_signals(db: Session = Depends(get_db)):
    return admin_overview_service.list_distress_signals(db)


@router.get("/admin/reports", response_model=List[CitizenReportOut], tags=["Admin"])
async def admin_reports(db: Session = Depends(get_db)):
    return report_service.list_reports(db)


@router.post("/admin/reports/{report_id}/verify", response_model=CitizenReportOut, tags=["Admin"])
async def verify_report(report_id: uuid.UUID, db: Session = Depends(get_db)):
    return report_service.verify_citizen_report(db, report_id)
