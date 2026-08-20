from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationOut

def record_user_location(db: Session, user: User, data: LocationCreate) -> LocationOut:
    point_wkt = f"POINT({data.longitude} {data.latitude})"
    loc = Location(
        user_id=user.id,
        latitude=data.latitude,
        longitude=data.longitude,
        accuracy_meters=data.accuracy_meters,
        geom=WKTElement(point_wkt, srid=4326)
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return LocationOut.model_validate(loc)


def get_latest_user_location(db: Session, user: User) -> LocationOut:
    loc = db.query(Location).filter(Location.user_id == user.id).order_by(Location.created_at.desc()).first()
    if not loc:
        # Fallback default location if none recorded yet
        return LocationOut(
            id=user.id,
            user_id=user.id,
            latitude=19.0760,
            longitude=72.8777,
            accuracy_meters=10.0,
            created_at=user.created_at
        )
    return LocationOut.model_validate(loc)
