from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import demo_login
from app.schemas.auth import TokenResponse
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter()


@router.post("/demo/login", response_model=TokenResponse, tags=["Demo Auth"])
async def demo_login_endpoint(db: Session = Depends(get_db)):
    """Logs in as the fixed seeded Demo Citizen account. No OTP, no password."""
    return demo_login(db)


@router.get("/users/me", response_model=UserOut, tags=["Users"])
async def read_current_user(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
