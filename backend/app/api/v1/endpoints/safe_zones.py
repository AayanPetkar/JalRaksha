from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.spatial_queries import find_nearest_safe_zones
from app.schemas.safe_zone import SafeZoneOut

router = APIRouter()


@router.get("/safe-zones/nearby", response_model=List[SafeZoneOut], tags=["Safe Zones"])
async def nearby_safe_zones(
    latitude: float = Query(19.078, description="Citizen latitude"),
    longitude: float = Query(72.879, description="Citizen longitude"),
    db: Session = Depends(get_db),
):
    """Nearest verified + operational safe zones to the given coordinates."""
    results = find_nearest_safe_zones(db, latitude=latitude, longitude=longitude, verified_only=True)
    return [SafeZoneOut(**r) for r in results]
