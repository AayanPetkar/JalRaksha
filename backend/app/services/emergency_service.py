from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.alert import Alert
from app.models.emergency_event import SafetyStatusEvent
from app.schemas.emergency_circle import ImSafeRequest, NeedHelpRequest

RECORDED_MESSAGE = "Emergency request recorded."


def _log_mock_notification(db: Session, user: User, channel: str) -> None:
    """Best-effort mock notification (no real SMS/FCM).

    NotificationHistory rows must reference an existing Alert (schema
    constraint), so this only logs a notification when there is a current
    demo alert to attach it to (e.g. after "Simulate Flood"); otherwise it
    is silently skipped. Either way the safety event itself is always
    recorded and visible to the admin.
    """
    alert = db.query(Alert).order_by(Alert.issued_at.desc()).first()
    if not alert:
        return
    from app.services.notification_service import notification_provider
    notification_provider.send_notification(
        db, alert_id=alert.id, recipient_phone=user.phone_number, channel=channel
    )


def record_im_safe(db: Session, user: User, data: ImSafeRequest) -> dict:
    event = SafetyStatusEvent(
        user_id=user.id,
        status_type="SAFE",
        latitude=data.latitude,
        longitude=data.longitude,
        custom_message=data.custom_message,
        source_tag="CITIZEN_ACTION",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    _log_mock_notification(db, user, channel="APP_PUSH")

    return {
        "status": "recorded",
        "message": RECORDED_MESSAGE,
        "event_id": str(event.id),
        "status_type": "SAFE",
        "latitude": event.latitude,
        "longitude": event.longitude,
        "recorded_at": event.created_at.isoformat(),
    }


def record_need_help(db: Session, user: User, data: NeedHelpRequest) -> dict:
    event = SafetyStatusEvent(
        user_id=user.id,
        status_type="NEED_HELP",
        distress_type=data.distress_type,
        latitude=data.latitude,
        longitude=data.longitude,
        source_tag="CITIZEN_ACTION",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    _log_mock_notification(db, user, channel="EMERGENCY_CONTACT_SMS")

    return {
        "status": "recorded",
        "message": RECORDED_MESSAGE,
        "event_id": str(event.id),
        "status_type": "NEED_HELP",
        "distress_type": event.distress_type,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "recorded_at": event.created_at.isoformat(),
    }
