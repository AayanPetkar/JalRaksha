from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.emergency_circle import ImSafeRequest, NeedHelpRequest
from app.services import emergency_service

router = APIRouter()


@router.post("/emergency-circle/im-safe", tags=["Emergency Circle"])
async def im_safe(
    data: ImSafeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return emergency_service.record_im_safe(db, current_user, data)


@router.post("/emergency-circle/need-help", tags=["Emergency Circle"])
async def need_help(
    data: NeedHelpRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return emergency_service.record_need_help(db, current_user, data)
