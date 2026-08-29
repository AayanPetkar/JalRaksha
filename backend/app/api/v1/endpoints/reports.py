from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.report import CitizenReportCreate, CitizenReportOut
from app.services import report_service

router = APIRouter()


@router.post("/reports", response_model=CitizenReportOut, tags=["Citizen Reports"])
async def submit_report(
    data: CitizenReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return report_service.create_citizen_report(db, current_user, data)
