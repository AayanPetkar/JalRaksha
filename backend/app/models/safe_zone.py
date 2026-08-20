import uuid
from typing import Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography
from app.models.base import Base, TimestampMixin

class SafeZone(Base, TimestampMixin):
    __tablename__ = "safe_zones"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="OFFICIAL_SHELTER", nullable=False) # 'OFFICIAL_SHELTER', 'RELIEF_CENTER', 'COMMUNITY_HALL', 'EVACUATION_CENTER'
    location: Mapped[bytes] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_occupancy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    source_tag: Mapped[str] = mapped_column(String(30), default="OFFICIAL_DATA", nullable=False)
