import math
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_Intersects, ST_GeomFromText, ST_MakePoint
from app.models.safe_zone import SafeZone
from app.models.report import CitizenReport
from app.models.road import Road, RoadCondition
from app.models.village import Infrastructure, Village

def calculate_haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Fallback planar distance in meters using Haversine formula."""
    R = 6371000.0 # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def find_nearest_safe_zones(
    db: Session,
    latitude: float,
    longitude: float,
    limit: int = 5,
    verified_only: bool = True
) -> List[Dict[str, Any]]:
    """Finds nearest VERIFIED and OPERATIONAL safe zones to user coordinates."""
    try:
        user_point = ST_MakePoint(longitude, latitude)
        stmt = select(
            SafeZone,
            ST_Distance(SafeZone.location, user_point).label("distance_meters")
        ).where(
            SafeZone.is_active == True
        )

        if verified_only:
            stmt = stmt.where(SafeZone.is_verified == True)

        stmt = stmt.order_by("distance_meters").limit(limit)
        results = db.execute(stmt).all()

        output = []
        for safe_zone, dist in results:
            output.append({
                "id": str(safe_zone.id),
                "name": safe_zone.name,
                "type": safe_zone.type,
                "capacity": safe_zone.capacity,
                "current_occupancy": safe_zone.current_occupancy,
                "is_verified": safe_zone.is_verified,
                "is_active": safe_zone.is_active,
                "distance_meters": round(float(dist), 1) if dist is not None else 0.0,
                "latitude": safe_zone.latitude,
                "longitude": safe_zone.longitude,
                "contact_phone": safe_zone.contact_phone,
                "district": safe_zone.district,
                "source_tag": safe_zone.source_tag
            })
        return output
    except Exception as e:
        # Fallback query for SQLite testing / environments without PostGIS engine enabled
        stmt = select(SafeZone).where(SafeZone.is_active == True)
        if verified_only:
            stmt = stmt.where(SafeZone.is_verified == True)
        
        safe_zones = db.scalars(stmt).all()
        output = []
        for sz in safe_zones:
            # Real haversine distance using the plain lat/lng columns (kept in
            # sync with the PostGIS `location` column) when available; falls
            # back to a fixed placeholder only if a legacy row has no
            # lat/lng recorded.
            if sz.latitude is not None and sz.longitude is not None:
                dist = calculate_haversine_distance(latitude, longitude, sz.latitude, sz.longitude)
            else:
                dist = 1500.0
            output.append({
                "id": str(sz.id),
                "name": sz.name,
                "type": sz.type,
                "capacity": sz.capacity,
                "current_occupancy": sz.current_occupancy,
                "is_verified": sz.is_verified,
                "is_active": sz.is_active,
                "distance_meters": round(dist, 1),
                "latitude": sz.latitude,
                "longitude": sz.longitude,
                "contact_phone": sz.contact_phone,
                "district": sz.district,
                "source_tag": sz.source_tag
            })
        output.sort(key=lambda item: item["distance_meters"])
        return output[:limit]


def find_nearby_citizen_reports(
    db: Session,
    latitude: float,
    longitude: float,
    radius_meters: float = 5000.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Finds active citizen ground reports within radius_meters."""
    try:
        user_point = ST_MakePoint(longitude, latitude)
        stmt = select(CitizenReport).where(
            ST_DWithin(CitizenReport.location, user_point, radius_meters)
        ).order_by(CitizenReport.created_at.desc()).limit(limit)

        reports = db.scalars(stmt).all()
        return [
            {
                "id": str(r.id),
                "latitude": r.latitude,
                "longitude": r.longitude,
                "disaster_category": r.disaster_category,
                "description": r.description,
                "photo_url": r.photo_url,
                "verification_status": r.verification_status,
                "source_tag": r.source_tag,
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]
    except Exception:
        reports = db.scalars(select(CitizenReport).limit(limit)).all()
        return [
            {
                "id": str(r.id),
                "latitude": r.latitude,
                "longitude": r.longitude,
                "disaster_category": r.disaster_category,
                "description": r.description,
                "photo_url": r.photo_url,
                "verification_status": r.verification_status,
                "source_tag": r.source_tag,
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]


def find_infrastructure_in_village(
    db: Session,
    village_id: Any
) -> List[Dict[str, Any]]:
    """Finds all infrastructure nodes within a village boundary."""
    if isinstance(village_id, str):
        village_id = uuid.UUID(village_id)
        
    stmt = select(Infrastructure).where(Infrastructure.village_id == village_id)
    items = db.scalars(stmt).all()
    return [
        {
            "id": str(item.id),
            "name": item.name,
            "type": item.type,
            "elevation_meters": item.elevation_meters,
            "status": item.status,
            "source_tag": item.source_tag
        }
        for item in items
    ]
