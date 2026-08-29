from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.schemas.alert import AlertOut


def list_active_alerts(db: Session) -> List[AlertOut]:
    """Active alerts (not expired). Compares in Python rather than SQL
    since SQLite does not preserve timezone-awareness on stored
    DateTime(timezone=True) values.
    """
    now = datetime.now(timezone.utc)
    all_alerts = db.query(Alert).order_by(Alert.issued_at.desc()).all()

    def _is_active(alert: Alert) -> bool:
        if alert.expires_at is None:
            return True
        expires_at = alert.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > now

    return [AlertOut.model_validate(a) for a in all_alerts if _is_active(a)]
