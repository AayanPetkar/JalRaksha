import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class EnvironmentalObservation(Base, TimestampMixin):
    __tablename__ = "environmental_observations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    village_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    rainfall_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    river_water_level_m: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    soil_moisture_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    source_tag: Mapped[str] = mapped_column(String(30), default="OFFICIAL_DATA", nullable=False)

    village: Mapped["Village"] = relationship("Village", back_populates="environmental_observations")
