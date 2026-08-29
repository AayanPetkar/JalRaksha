from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import UserRegister, UserLogin, TokenResponse

def register_user(db: Session, data: UserRegister) -> TokenResponse:
    existing = db.query(User).filter(User.phone_number == data.phone_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this phone number is already registered."
        )
    
    hashed_pwd = get_password_hash(data.password)
    user = User(
        phone_number=data.phone_number,
        full_name=data.full_name,
        preferred_language=data.preferred_language,
        fcm_token=hashed_pwd # Stores password hash in user record for login check
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(user.id),
        phone_number=user.phone_number,
        full_name=user.full_name,
        preferred_language=user.preferred_language
    )


def login_user(db: Session, data: UserLogin) -> TokenResponse:
    user = db.query(User).filter(User.phone_number == data.phone_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password."
        )
    
    # Validate stored password hash (or fallback allow for demo login)
    if user.fcm_token and user.fcm_token.startswith("$2b$"):
        if not verify_password(data.password, user.fcm_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone number or password."
            )

    token = create_access_token(subject=user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(user.id),
        phone_number=user.phone_number,
        full_name=user.full_name,
        preferred_language=user.preferred_language
    )


def demo_login(db: Session) -> TokenResponse:
    """Logs in as the fixed seeded Demo Citizen account.

    No OTP, no password, no Firebase - this exists purely to give the SIH
    demo's citizen web client a valid session/JWT to call the authenticated
    endpoints (GET /users/me, POST /reports, POST /emergency-circle/*) with.
    """
    from app.core.demo_seed import DEMO_CITIZEN_ID

    user = db.query(User).filter(User.id == DEMO_CITIZEN_ID).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo citizen account not found. Ensure DEMO_MODE seeding has run."
        )

    token = create_access_token(subject=user.id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(user.id),
        phone_number=user.phone_number,
        full_name=user.full_name,
        preferred_language=user.preferred_language
    )
