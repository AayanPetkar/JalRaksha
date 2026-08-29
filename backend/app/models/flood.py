import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class FloodEvent(Base, TimestampMixin):
    __tablename__ = "flood_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_title: Mapped[str] = mapped_column(String(150), nullable=False)
    affected_district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), default="WATCH", nullable=False) # 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_tag: Mapped[str] = mapped_column(String(30), default="OFFICIAL_DATA", nullable=False)

    flood_risks: Mapped[List["FloodRisk"]] = relationship("FloodRisk", back_populates="flood_event")


class FloodRisk(Base, TimestampMixin):
    __tablename__ = "flood_risks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    village_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    flood_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("flood_events.id", ondelete="SET NULL"), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False) # 0.0 to 100.0
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False) # 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    data_freshness_minutes: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    affected_houses_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    affected_farmland_acres: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    affected_schools_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    affected_hospitals_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_tag: Mapped[str] = mapped_column(String(30), default="AI_PREDICTION", nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    village: Mapped["Village"] = relationship("Village", back_populates="flood_risks")
    flood_event: Mapped[Optional["FloodEvent"]] = relationship("FloodEvent", back_populates="flood_risks")
    factors: Mapped[List["RiskFactor"]] = relationship("RiskFactor", back_populates="flood_risk", cascade="all, delete-orphan")


class RiskFactor(Base, TimestampMixin):
    __tablename__ = "risk_factors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    flood_risk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("flood_risks.id", ondelete="CASCADE"), nullable=False, index=True)
    factor_key: Mapped[str] = mapped_column(String(50), nullable=False)
    contribution_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description_en: Mapped[str] = mapped_column(String, nullable=False)
    description_mr: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description_hi: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    flood_risk: Mapped["FloodRisk"] = relationship("FloodRisk", back_populates="factors")
