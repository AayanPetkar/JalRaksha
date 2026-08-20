import uuid
from typing import Optional
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from app.models.base import Base, TimestampMixin

class Location(Base, TimestampMixin):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geom: Mapped[bytes] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="locations")
