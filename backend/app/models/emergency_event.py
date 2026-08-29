import uuid
from typing import Optional
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class SafetyStatusEvent(Base, TimestampMixin):
    """A citizen's 'I'm Safe' or 'Need Help' action.

    Deliberately minimal: plain lat/lng floats (no PostGIS geometry) since
    these are simple point-in-time check-ins, not spatially queried.
    `created_at` (from TimestampMixin) doubles as the event timestamp.
    """
    __tablename__ = "safety_status_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'SAFE' or 'NEED_HELP'
    distress_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    custom_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_tag: Mapped[str] = mapped_column(String(30), default="CITIZEN_ACTION", nullable=False)

    user: Mapped["User"] = relationship("User")
