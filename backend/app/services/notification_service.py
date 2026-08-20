import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.alert import NotificationHistory

class NotificationProvider(ABC):
    @abstractmethod
    def send_notification(self, db: Session, alert_id: uuid.UUID, recipient_phone: str, channel: str) -> NotificationHistory:
        pass

class MockNotificationProvider(NotificationProvider):
    """Phase 3 Mock Notification Provider recording events into notification_history table."""

    def send_notification(self, db: Session, alert_id: uuid.UUID, recipient_phone: str, channel: str) -> NotificationHistory:
        record = NotificationHistory(
            id=uuid.uuid4(),
            alert_id=alert_id,
            recipient_phone=recipient_phone,
            channel=channel, # 'APP_PUSH', 'USER_SMS', 'EMERGENCY_CONTACT_SMS'
            status="SENT",
            sent_at=datetime.now(timezone.utc)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

notification_provider = MockNotificationProvider()
