from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate, UserOut

def update_user_profile(db: Session, user: User, data: UserUpdate) -> UserOut:
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.preferred_language is not None:
        user.preferred_language = data.preferred_language
    if data.fcm_token is not None:
        user.fcm_token = data.fcm_token
    
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
