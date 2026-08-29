"""Admin-triggered demo state transitions: simulate-flood, simulate-normal,
simulate-blocked-road.

All writes here are confined to the fixed set of seeded demo rows (Phase A's
`app.core.demo_seed` IDs) using upsert-by-fixed-ID, so repeated
flood/normal/block cycles never accumulate duplicate rows.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.flood import FloodEvent, FloodRisk, RiskFactor
from app.models.environmental import EnvironmentalObservation
from app.models.road import RoadCondition
from app.models.alert import Alert
from app.core.demo_seed import (
    seed_demo_data,
    VILLAGE_ID,
    FLOOD_RISK_ID,
    ENV_OBSERVATION_ID,
    RISK_FACTOR_RAINFALL_ID,
    RISK_FACTOR_RIVER_ID,
    RISK_FACTOR_SOIL_ID,
    RISK_FACTOR_ELEVATION_ID,
    ROAD_A_COND_ID,
    ROAD_B_COND_ID,
    DEMO_CITIZEN_PHONE,
    DEMO_SOURCE_TAG,
)

# Fixed demo IDs for the flood event / alert created by "Simulate Flood".
# Upserted by ID so toggling flood <-> normal never creates duplicates.
DEMO_FLOOD_EVENT_ID = uuid.UUID("99999999-9999-9999-9999-999999999901")
DEMO_ALERT_ID = uuid.UUID("99999999-9999-9999-9999-999999999902")

CRITICAL_RISK_SCORE = 87.0

_FLOOD_FACTOR_UPDATES = {
    RISK_FACTOR_RAINFALL_ID: dict(
        contribution_percentage=42.0, value=125.0, unit="mm",
        description_en="Heavy rainfall recorded (125mm in 24h)",
        description_mr="मुसळधार पाऊस नोंदवला गेला (24 तासात 125 मिमी)",
        description_hi="भारी बारिश दर्ज की गई (24 घंटे में 125 मिमी)",
    ),
    RISK_FACTOR_RIVER_ID: dict(
        contribution_percentage=30.0, value=4.2, unit="m",
        description_en="Rising river water level near Krishna basin (4.2m)",
        description_mr="कृष्णा पात्राजवळ नदीची वाढती पातळी (4.2 मी)",
        description_hi="कृष्णा बेसिन के पास नदी का बढ़ता जलस्तर (4.2 मी)",
    ),
    RISK_FACTOR_SOIL_ID: dict(
        contribution_percentage=18.0, value=88.5, unit="%",
        description_en="High soil moisture saturation (88.5%)",
        description_mr="जमिनीची जास्त पाझर क्षमता (88.5%)",
        description_hi="उच्च मृदा नमी संतृप्ति (88.5%)",
    ),
    RISK_FACTOR_ELEVATION_ID: dict(
        contribution_percentage=10.0, value=None, unit=None,
        description_en="Location in low-lying river basin terrain",
        description_mr="सखल भौगोलिक नदीपात्र स्थान",
        description_hi="निचले नदी बेसिन क्षेत्र में स्थिति",
    ),
}


def simulate_flood(db: Session) -> FloodRisk:
    """LOW -> CRITICAL. Escalates the seeded flood-risk record, updates
    environmental readings and risk factors, elevates risk on the riverside
    demo route, creates a simulated flood event, and issues a simulated
    (clearly-labeled, non-official) alert + mock notification.
    """
    now = datetime.now(timezone.utc)

    flood_event = db.query(FloodEvent).filter(FloodEvent.id == DEMO_FLOOD_EVENT_ID).first()
    if not flood_event:
        flood_event = FloodEvent(id=DEMO_FLOOD_EVENT_ID)
        db.add(flood_event)
    flood_event.event_title = "[DEMO] Simulated Flood Event - Sangli Rural"
    flood_event.affected_district = "Sangli"
    flood_event.severity = "CRITICAL"
    flood_event.started_at = now
    flood_event.ended_at = None
    flood_event.source_tag = DEMO_SOURCE_TAG

    risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()
    risk.risk_score = CRITICAL_RISK_SCORE
    risk.risk_level = "CRITICAL"
    risk.confidence_score = 0.93
    risk.data_freshness_minutes = 2
    risk.flood_event_id = DEMO_FLOOD_EVENT_ID
    risk.affected_houses_count = 320
    risk.affected_farmland_acres = 185.0
    risk.affected_schools_count = 1
    risk.affected_hospitals_count = 0
    risk.source_tag = DEMO_SOURCE_TAG
    risk.evaluated_at = now

    obs = db.query(EnvironmentalObservation).filter(EnvironmentalObservation.id == ENV_OBSERVATION_ID).first()
    if obs:
        obs.rainfall_mm = 125.0
        obs.river_water_level_m = 4.2
        obs.soil_moisture_percentage = 88.5
        obs.observed_at = now
        obs.source_tag = DEMO_SOURCE_TAG

    for factor_id, values in _FLOOD_FACTOR_UPDATES.items():
        factor = db.query(RiskFactor).filter(RiskFactor.id == factor_id).first()
        if factor:
            for key, value in values.items():
                setattr(factor, key, value)

    # Elevate risk on the riverside route (most exposed); leave the main
    # route and highway bypass open so the routing demo still has an
    # available "safest route" until the admin explicitly blocks a road.
    riverside_condition = db.query(RoadCondition).filter(RoadCondition.id == ROAD_B_COND_ID).first()
    if riverside_condition:
        riverside_condition.status = "HIGH_RISK"
        riverside_condition.hazard_penalty_multiplier = 2.5
        riverside_condition.water_depth_cm = 35.0
        riverside_condition.source_tag = DEMO_SOURCE_TAG

    alert = db.query(Alert).filter(Alert.id == DEMO_ALERT_ID).first()
    if not alert:
        alert = Alert(id=DEMO_ALERT_ID, village_id=VILLAGE_ID)
        db.add(alert)
    alert.village_id = VILLAGE_ID
    alert.alert_level = "CRITICAL"
    alert.title = "[DEMO] Simulated Flood Alert"
    alert.message_en = (
        "SIMULATED DEMO ALERT: Flood risk in Sangli Rural has been simulated as "
        "CRITICAL for this demonstration. This is not an official government warning."
    )
    alert.message_mr = (
        "सिम्युलेटेड डेमो सूचना: सांगली ग्रामीण मधील पुराचा धोका या प्रात्यक्षिकासाठी गंभीर "
        "(CRITICAL) म्हणून सिम्युलेट केला आहे. हा अधिकृत सरकारी इशारा नाही."
    )
    alert.message_hi = (
        "सिम्युलेटेड डेमो चेतावनी: सांगली ग्रामीण में बाढ़ का खतरा इस प्रदर्शन के लिए गंभीर "
        "(CRITICAL) के रूप में सिम्युलेट किया गया है। यह कोई आधिकारिक सरकारी चेतावनी नहीं है।"
    )
    alert.issued_at = now
    alert.expires_at = None
    alert.source_tag = DEMO_SOURCE_TAG

    db.commit()

    # Mock notification only (no real SMS/FCM/Firebase).
    from app.services.notification_service import notification_provider
    notification_provider.send_notification(
        db, alert_id=alert.id, recipient_phone=DEMO_CITIZEN_PHONE, channel="APP_PUSH"
    )

    db.refresh(risk)
    return risk


def simulate_normal(db: Session) -> FloodRisk:
    """Restores the exact Phase A baseline: LOW risk (score 20), no active
    simulated flood, all roads OPEN, critical alert removed. Reuses the
    Phase A idempotent seeder so this is guaranteed equivalent to the
    original startup state, and never creates duplicate rows.
    """
    db.query(Alert).filter(Alert.id == DEMO_ALERT_ID).delete()
    db.query(FloodEvent).filter(FloodEvent.id == DEMO_FLOOD_EVENT_ID).delete()
    db.commit()

    seed_demo_data(db)  # merges FloodRisk/RiskFactor/EnvironmentalObservation/RoadConditions back to baseline

    risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()
    return risk


def simulate_blocked_road(db: Session) -> dict:
    """Blocks the primary demo route (Route A). Independent of flood state:
    can be called at LOW or CRITICAL risk to demonstrate route recalculation.
    """
    condition = db.query(RoadCondition).filter(RoadCondition.id == ROAD_A_COND_ID).first()
    previous_status = condition.status
    road_name = condition.road.road_name if condition.road else "Route A"

    condition.status = "BLOCKED"
    condition.hazard_penalty_multiplier = 5.0
    condition.water_depth_cm = 80.0
    condition.source_tag = DEMO_SOURCE_TAG
    db.commit()
    db.refresh(condition)

    return {
        "road_name": road_name,
        "previous_status": previous_status,
        "new_status": condition.status,
        "source_tag": condition.source_tag,
    }
