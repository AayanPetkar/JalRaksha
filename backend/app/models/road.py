import uuid
from typing import Optional, List
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.models.base import Base, TimestampMixin

class Road(Base, TimestampMixin):
    __tablename__ = "roads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    road_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    road_type: Mapped[str] = mapped_column(String(50), default="VILLAGE_ROAD", nullable=False) # 'HIGHWAY', 'VILLAGE_ROAD', 'BRIDGE'
    path: Mapped[bytes] = mapped_column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    base_cost_meters: Mapped[float] = mapped_column(Float, nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_tag: Mapped[str] = mapped_column(String(30), default="OFFICIAL_DATA", nullable=False)

    conditions: Mapped[List["RoadCondition"]] = relationship("RoadCondition", back_populates="road", cascade="all, delete-orphan")


class RoadCondition(Base, TimestampMixin):
    __tablename__ = "road_conditions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    road_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roads.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False) # 'OPEN', 'WATCH', 'HIGH_RISK', 'BLOCKED', 'SUBMERGED'
    hazard_penalty_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    water_depth_cm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source_tag: Mapped[str] = mapped_column(String(30), default="AI_PREDICTION", nullable=False)

    road: Mapped["Road"] = relationship("Road", back_populates="conditions")
