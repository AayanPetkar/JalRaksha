import uuid
from typing import Optional, List
from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry, Geography
from app.models.base import Base, TimestampMixin

class Village(Base, TimestampMixin):
    __tablename__ = "villages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    village_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_mr: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name_hi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), default="Maharashtra", nullable=False)
    population: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    boundary: Mapped[bytes] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    centroid: Mapped[bytes] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    source_tag: Mapped[str] = mapped_column(String(30), default="OFFICIAL_DATA", nullable=False)

    infrastructures: Mapped[List["Infrastructure"]] = relationship("Infrastructure", back_populates="village", cascade="all, delete-orphan")
    flood_risks: Mapped[List["FloodRisk"]] = relationship("FloodRisk", back_populates="village", cascade="all, delete-orphan")
    environmental_observations: Mapped[List["EnvironmentalObservation"]] = relationship("EnvironmentalObservation", back_populates="village", cascade="all, delete-orphan")


class Infrastructure(Base, TimestampMixin):
    __tablename__ = "infrastructure"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    village_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False) # 'HOUSE', 'FARM', 'SCHOOL', 'HOSPITAL', 'BRIDGE', 'CRITICAL_INFRASTRUCTURE'
    location: Mapped[bytes] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    elevation_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="OPERATIONAL", nullable=False)
    source_tag: Mapped[str] = mapped_column(String(30), default="OFFICIAL_DATA", nullable=False)

    village: Mapped["Village"] = relationship("Village", back_populates="infrastructures")
