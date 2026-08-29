from typing import List
from sqlalchemy.orm import Session
from app.core.demo_seed import FLOOD_RISK_ID
from app.models.flood import FloodRisk
from app.models.alert import Alert
from app.models.report import CitizenReport
from app.models.road import RoadCondition
from app.models.safe_zone import SafeZone
from app.models.user import User
from app.models.emergency_event import SafetyStatusEvent
from app.schemas.admin import AdminOverviewOut, DistressEventOut


def get_admin_overview(db: Session) -> AdminOverviewOut:
    risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()

    active_alerts_count = db.query(Alert).count()
    citizen_reports_count = db.query(CitizenReport).count()
    unverified_reports_count = (
        db.query(CitizenReport).filter(CitizenReport.verification_status == "UNVERIFIED").count()
    )
    distress_signals_count = (
        db.query(SafetyStatusEvent).filter(SafetyStatusEvent.status_type == "NEED_HELP").count()
    )
    affected_roads_count = db.query(RoadCondition).filter(RoadCondition.status != "OPEN").count()
    operational_safe_zones_count = (
        db.query(SafeZone)
        .filter(SafeZone.is_active == True, SafeZone.is_verified == True)  # noqa: E712
        .count()
    )

    return AdminOverviewOut(
        current_risk_level=risk.risk_level if risk else "LOW",
        current_risk_score=risk.risk_score if risk else 20.0,
        active_alerts_count=active_alerts_count,
        citizen_reports_count=citizen_reports_count,
        unverified_reports_count=unverified_reports_count,
        distress_signals_count=distress_signals_count,
        affected_roads_count=affected_roads_count,
        operational_safe_zones_count=operational_safe_zones_count,
        source_tag=(risk.source_tag if risk else "SIMULATED_DEMO_DATA"),
    )


def list_distress_signals(db: Session, limit: int = 20) -> List[DistressEventOut]:
    events = (
        db.query(SafetyStatusEvent)
        .filter(SafetyStatusEvent.status_type == "NEED_HELP")
        .order_by(SafetyStatusEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    output = []
    for e in events:
        user = db.query(User).filter(User.id == e.user_id).first()
        output.append(DistressEventOut(
            user_id=e.user_id,
            user_name=user.full_name if user else "Unknown",
            user_phone=user.phone_number if user else "",
            latitude=e.latitude if e.latitude is not None else 0.0,
            longitude=e.longitude if e.longitude is not None else 0.0,
            distress_type=e.distress_type or "UNKNOWN",
            created_at=e.created_at,
        ))
    return output
