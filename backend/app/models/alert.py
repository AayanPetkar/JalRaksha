import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    village_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_level: Mapped[str] = mapped_column(String(20), nullable=False) # 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message_en: Mapped[str] = mapped_column(String, nullable=False)
    message_mr: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    message_hi: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_tag: Mapped[str] = mapped_column(String(30), default="OFFICIAL_DATA", nullable=False)

    notifications: Mapped[List["NotificationHistory"]] = relationship("NotificationHistory", back_populates="alert", cascade="all, delete-orphan")


class NotificationHistory(Base, TimestampMixin):
    __tablename__ = "notification_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False) # 'APP_PUSH', 'USER_SMS', 'EMERGENCY_CONTACT_SMS'
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False) # 'PENDING', 'SENT', 'DELIVERED', 'FAILED'
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    alert: Mapped["Alert"] = relationship("Alert", back_populates="notifications")
