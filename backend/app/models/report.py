import uuid
from typing import Optional
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from app.models.base import Base, TimestampMixin

class CitizenReport(Base, TimestampMixin):
    __tablename__ = "citizen_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[bytes] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    voice_note_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    disaster_category: Mapped[str] = mapped_column(String(50), default="WATER_LOGGING", nullable=False)
    verification_status: Mapped[str] = mapped_column(String(30), default="UNVERIFIED", nullable=False) # 'UNVERIFIED', 'VERIFIED', 'REJECTED'
    source_tag: Mapped[str] = mapped_column(String(30), default="CITIZEN_REPORT", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="citizen_reports")
