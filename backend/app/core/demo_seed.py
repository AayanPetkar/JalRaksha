"""SIH demo dataset seeding for the SQLite demo runtime.

This is DELIBERATELY SEPARATE from `database/seed_data.py` (the original
PostgreSQL/PostGIS-oriented seed, which seeds a mid-flood CRITICAL scenario
for Kurla Rural). That file is left untouched for future production/Docker
use.

This module seeds a **baseline LOW-risk** starting state for the live SIH
demo, using the same village/geography and the same `SIMULATED_DEMO_DATA`
source-tag convention already established in the project. The later
"Simulate Flood" / "Block Road" demo endpoints (Phase B) are expected to
escalate this baseline state at runtime; they are NOT implemented here.

Seeding is idempotent: every row is written with `Session.merge()` against a
fixed, well-known UUID, so re-running `seed_demo_data()` (e.g. on every
backend startup) updates existing rows back to their baseline values instead
of creating duplicates. This also means restarting the backend naturally
restores the seeded entities to their baseline demo values.

For a guaranteed full reset (including any ad-hoc rows created live during a
demo, e.g. future distress events), use `scripts/reset_demo.py`, which drops
and recreates the SQLite file before reseeding.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from app.core.security import get_password_hash
from app.models.user import User, AdminUser
from app.models.location import Location
from app.models.village import Village, Infrastructure
from app.models.road import Road, RoadCondition
from app.models.safe_zone import SafeZone
from app.models.environmental import EnvironmentalObservation
from app.models.flood import FloodRisk, RiskFactor
from app.models.report import CitizenReport

DEMO_SOURCE_TAG = "SIMULATED_DEMO_DATA"

# ---------------------------------------------------------------------------
# Fixed, well-known demo IDs.
#
# The village / infrastructure / safe-zone IDs intentionally match
# `database/seed_data.py` and `app/services/risk_service.py` so the same
# "Kurla Rural" scenario and the same DEMO_RISK_ID the risk service already
# looks up resolve consistently across the whole demo build.
# ---------------------------------------------------------------------------
VILLAGE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

INFRA_SCHOOL_ID = uuid.UUID("22222222-2222-2222-2222-222222222201")
INFRA_BRIDGE_ID = uuid.UUID("22222222-2222-2222-2222-222222222202")
INFRA_HOSPITAL_ID = uuid.UUID("22222222-2222-2222-2222-222222222203")

ROAD_A_ID = uuid.UUID("33333333-3333-3333-3333-33333333A001")
ROAD_A_COND_ID = uuid.UUID("33333333-3333-3333-3333-33333333A002")
ROAD_B_ID = uuid.UUID("33333333-3333-3333-3333-33333333B001")
ROAD_B_COND_ID = uuid.UUID("33333333-3333-3333-3333-33333333B002")
ROAD_C_ID = uuid.UUID("33333333-3333-3333-3333-33333333C001")
ROAD_C_COND_ID = uuid.UUID("33333333-3333-3333-3333-33333333C002")

SAFE_ZONE_1_ID = uuid.UUID("44444444-4444-4444-4444-444444444401")
SAFE_ZONE_2_ID = uuid.UUID("44444444-4444-4444-4444-444444444402")

ENV_OBSERVATION_ID = uuid.UUID("55555555-5555-5555-5555-555555555510")

# Matches risk_service.DEMO_RISK_ID exactly, so the existing risk service
# picks up this seeded baseline row instead of falling back to its
# hardcoded CRITICAL example.
FLOOD_RISK_ID = uuid.UUID("66666666-6666-6666-6666-666666666602")

RISK_FACTOR_RAINFALL_ID = uuid.UUID("66666666-6666-6666-6666-666666666611")
RISK_FACTOR_RIVER_ID = uuid.UUID("66666666-6666-6666-6666-666666666612")
RISK_FACTOR_SOIL_ID = uuid.UUID("66666666-6666-6666-6666-666666666613")
RISK_FACTOR_ELEVATION_ID = uuid.UUID("66666666-6666-6666-6666-666666666614")

DEMO_CITIZEN_ID = uuid.UUID("77777777-7777-7777-7777-777777777701")
DEMO_CITIZEN_LOCATION_ID = uuid.UUID("77777777-7777-7777-7777-777777777705")
DEMO_ADMIN_ID = uuid.UUID("77777777-7777-7777-7777-777777777710")

DEMO_REPORT_1_ID = uuid.UUID("88888888-8888-8888-8888-888888888810")
DEMO_REPORT_2_ID = uuid.UUID("88888888-8888-8888-8888-888888888811")

# Fixed demo credentials. Clearly fake, not real personal information.
DEMO_CITIZEN_PHONE = "0000000000"
DEMO_ADMIN_USERNAME = "demo_admin"
DEMO_ADMIN_EMAIL = "demo_admin@jalraksha.demo"
DEMO_ADMIN_PASSWORD = "demo1234"  # NOT for production use; demo-only login.


def seed_demo_data(db: Session) -> None:
    """Seed (or reset-to-baseline) the SIH demo dataset.

    Safe to call on every backend startup. Uses merge() throughout so
    re-running this does not create duplicate rows, and instead restores the
    seeded entities to their original baseline values.
    """
    # 1. Village -----------------------------------------------------------
    village = Village(
        id=VILLAGE_ID,
        village_code="VIL-KURLA-01",
        name_en="Kurla Rural",
        name_mr="कुर्ला ग्रामीण",
        name_hi="कुर्ला ग्रामीण",
        district="Kurla",
        state="Maharashtra",
        population=14200,
        boundary=WKTElement(
            "POLYGON((72.870 19.070, 72.890 19.070, 72.890 19.090, 72.870 19.090, 72.870 19.070))",
            srid=4326,
        ),
        centroid=WKTElement("POINT(72.880 19.080)", srid=4326),
        source_tag=DEMO_SOURCE_TAG,
    )
    db.merge(village)

    # 2. Infrastructure ------------------------------------------------------
    infra_items = [
        Infrastructure(
            id=INFRA_SCHOOL_ID,
            village_id=VILLAGE_ID,
            name="Kurla ZP High School",
            type="SCHOOL",
            location=WKTElement("POINT(72.875 19.075)", srid=4326),
            elevation_meters=14.5,
            status="OPERATIONAL",
            source_tag=DEMO_SOURCE_TAG,
        ),
        Infrastructure(
            id=INFRA_BRIDGE_ID,
            village_id=VILLAGE_ID,
            name="Krishna River Bridge",
            type="BRIDGE",
            location=WKTElement("POINT(72.878 19.078)", srid=4326),
            elevation_meters=10.2,
            status="OPERATIONAL",
            source_tag=DEMO_SOURCE_TAG,
        ),
        Infrastructure(
            id=INFRA_HOSPITAL_ID,
            village_id=VILLAGE_ID,
            name="Primary Health Center",
            type="HOSPITAL",
            location=WKTElement("POINT(72.882 19.082)", srid=4326),
            elevation_meters=18.0,
            status="OPERATIONAL",
            source_tag=DEMO_SOURCE_TAG,
        ),
    ]
    for item in infra_items:
        db.merge(item)

    # 3. Roads / demo routes (Route A / B / C) -------------------------------
    # No routing algorithm is implemented yet (Phase B). These three named,
    # independent road segments give a future route-selection service enough
    # to determine per-route availability, risk, and distance:
    #   - available:  RoadCondition.status == "OPEN"
    #   - blocked:    RoadCondition.status in ("BLOCKED", "SUBMERGED")
    #   - risk:       RoadCondition.hazard_penalty_multiplier / water_depth_cm
    #   - distance:   Road.base_cost_meters
    roads = [
        (
            Road(
                id=ROAD_A_ID,
                road_name="Route A - Main Road via Krishna Bridge",
                road_type="VILLAGE_ROAD",
                path=WKTElement("LINESTRING(72.879 19.078, 72.882 19.082, 72.885 19.085)", srid=4326),
                base_cost_meters=2400.0,
                district="Kurla",
                source_tag=DEMO_SOURCE_TAG,
            ),
            RoadCondition(
                id=ROAD_A_COND_ID,
                road_id=ROAD_A_ID,
                status="OPEN",
                hazard_penalty_multiplier=1.0,
                water_depth_cm=0.0,
                source_tag=DEMO_SOURCE_TAG,
            ),
        ),
        (
            Road(
                id=ROAD_B_ID,
                road_name="Route B - Riverside Lane",
                road_type="VILLAGE_ROAD",
                path=WKTElement("LINESTRING(72.879 19.078, 72.884 19.083, 72.890 19.089)", srid=4326),
                base_cost_meters=3100.0,
                district="Kurla",
                source_tag=DEMO_SOURCE_TAG,
            ),
            RoadCondition(
                id=ROAD_B_COND_ID,
                road_id=ROAD_B_ID,
                status="OPEN",
                hazard_penalty_multiplier=1.0,
                water_depth_cm=0.0,
                source_tag=DEMO_SOURCE_TAG,
            ),
        ),
        (
            Road(
                id=ROAD_C_ID,
                road_name="Route C - Highway Bypass",
                road_type="HIGHWAY",
                path=WKTElement("LINESTRING(72.879 19.078, 72.883 19.086, 72.888 19.090)", srid=4326),
                base_cost_meters=4200.0,
                district="Kurla",
                source_tag=DEMO_SOURCE_TAG,
            ),
            RoadCondition(
                id=ROAD_C_COND_ID,
                road_id=ROAD_C_ID,
                status="OPEN",
                hazard_penalty_multiplier=1.0,
                water_depth_cm=0.0,
                source_tag=DEMO_SOURCE_TAG,
            ),
        ),
    ]
    for road, condition in roads:
        db.merge(road)
        db.merge(condition)

    # 4. Safe zones (verified + operational) --------------------------------
    safe_zones = [
        SafeZone(
            id=SAFE_ZONE_1_ID,
            name="Kurla Community Hall",
            type="OFFICIAL_SHELTER",
            location=WKTElement("POINT(72.8850 19.0850)", srid=4326),
            latitude=19.0850,
            longitude=72.8850,
            capacity=500,
            current_occupancy=42,
            is_active=True,
            is_verified=True,
            contact_phone="+919876500111",
            district="Kurla",
            source_tag=DEMO_SOURCE_TAG,
        ),
        SafeZone(
            id=SAFE_ZONE_2_ID,
            name="Kurla Relief Center",
            type="RELIEF_CENTER",
            location=WKTElement("POINT(72.8900 19.0890)", srid=4326),
            latitude=19.0890,
            longitude=72.8900,
            capacity=300,
            current_occupancy=10,
            is_active=True,
            is_verified=True,
            contact_phone="+919876500222",
            district="Kurla",
            source_tag=DEMO_SOURCE_TAG,
        ),
    ]
    for sz in safe_zones:
        db.merge(sz)

    # 5. Environmental observation — LOW-risk baseline values ----------------
    observation = EnvironmentalObservation(
        id=ENV_OBSERVATION_ID,
        station_id="STN-KURLA-DEMO-01",
        village_id=VILLAGE_ID,
        rainfall_mm=18.0,
        river_water_level_m=1.2,
        soil_moisture_percentage=32.0,
        temperature_celsius=27.0,
        observed_at=datetime.now(timezone.utc),
        source_tag=DEMO_SOURCE_TAG,
    )
    db.merge(observation)

    # 6. Flood risk — LOW baseline, no active flood event --------------------
    # flood_event_id is intentionally left unset: there is no active flood at
    # baseline. The future "Simulate Flood" endpoint (Phase B) is expected to
    # create a FloodEvent and escalate this same row.
    flood_risk = FloodRisk(
        id=FLOOD_RISK_ID,
        village_id=VILLAGE_ID,
        flood_event_id=None,
        risk_score=20.0,
        risk_level="LOW",
        confidence_score=0.80,
        data_freshness_minutes=5,
        affected_houses_count=0,
        affected_farmland_acres=0.0,
        affected_schools_count=0,
        affected_hospitals_count=0,
        source_tag=DEMO_SOURCE_TAG,
        evaluated_at=datetime.now(timezone.utc),
    )
    db.merge(flood_risk)

    risk_factors = [
        RiskFactor(
            id=RISK_FACTOR_RAINFALL_ID,
            flood_risk_id=FLOOD_RISK_ID,
            factor_key="HEAVY_RAINFALL",
            contribution_percentage=8.0,
            value=18.0,
            unit="mm",
            description_en="Light rainfall in past 24h (18mm)",
            description_mr="गेल्या 24 तासात हलका पाऊस (18 मिमी)",
            description_hi="पिछले 24 घंटे में हल्की बारिश (18 मिमी)",
        ),
        RiskFactor(
            id=RISK_FACTOR_RIVER_ID,
            flood_risk_id=FLOOD_RISK_ID,
            factor_key="RIVER_LEVEL",
            contribution_percentage=5.0,
            value=1.2,
            unit="m",
            description_en="River water level within normal range (1.2m)",
            description_mr="नदीची पाणी पातळी सामान्य मर्यादेत (1.2 मी)",
            description_hi="नदी का जलस्तर सामान्य सीमा में (1.2 मी)",
        ),
        RiskFactor(
            id=RISK_FACTOR_SOIL_ID,
            flood_risk_id=FLOOD_RISK_ID,
            factor_key="SOIL_SATURATION",
            contribution_percentage=4.0,
            value=32.0,
            unit="%",
            description_en="Low soil moisture saturation (32%)",
            description_mr="जमिनीतील कमी ओलावा (32%)",
            description_hi="मृदा में कम नमी (32%)",
        ),
        RiskFactor(
            id=RISK_FACTOR_ELEVATION_ID,
            flood_risk_id=FLOOD_RISK_ID,
            factor_key="LOW_ELEVATION",
            contribution_percentage=3.0,
            value=None,
            unit=None,
            description_en="Location at moderate elevation in river basin terrain",
            description_mr="नदीपात्र क्षेत्रात मध्यम उंचीचे स्थान",
            description_hi="नदी बेसिन क्षेत्र में मध्यम ऊंचाई पर स्थिति",
        ),
    ]
    for factor in risk_factors:
        db.merge(factor)

    # 7. Demo citizen + demo admin --------------------------------------------
    demo_citizen = User(
        id=DEMO_CITIZEN_ID,
        phone_number=DEMO_CITIZEN_PHONE,
        full_name="Demo Citizen",
        preferred_language="en",
        fcm_token=None,
    )
    db.merge(demo_citizen)

    demo_citizen_location = Location(
        id=DEMO_CITIZEN_LOCATION_ID,
        user_id=DEMO_CITIZEN_ID,
        latitude=19.078,
        longitude=72.879,
        accuracy_meters=10.0,
        geom=WKTElement("POINT(72.879 19.078)", srid=4326),
    )
    db.merge(demo_citizen_location)

    demo_admin = AdminUser(
        id=DEMO_ADMIN_ID,
        username=DEMO_ADMIN_USERNAME,
        email=DEMO_ADMIN_EMAIL,
        password_hash=get_password_hash(DEMO_ADMIN_PASSWORD),
        role="DISASTER_OFFICIAL",
        jurisdiction_district="Kurla",
    )
    db.merge(demo_admin)

    # 8. Demo citizen reports (clearly labeled, not real citizen submissions) -
    demo_reports = [
        CitizenReport(
            id=DEMO_REPORT_1_ID,
            user_id=DEMO_CITIZEN_ID,
            latitude=19.078,
            longitude=72.879,
            location=WKTElement("POINT(72.879 19.078)", srid=4326),
            description="[DEMO] Minor water logging observed near Krishna River Bridge.",
            disaster_category="WATER_LOGGING",
            photo_url=None,
            voice_note_url=None,
            verification_status="UNVERIFIED",
            source_tag=DEMO_SOURCE_TAG,
        ),
        CitizenReport(
            id=DEMO_REPORT_2_ID,
            user_id=DEMO_CITIZEN_ID,
            latitude=19.081,
            longitude=72.883,
            location=WKTElement("POINT(72.883 19.081)", srid=4326),
            description="[DEMO] Road surface near school currently clear and passable.",
            disaster_category="OTHER",
            photo_url=None,
            voice_note_url=None,
            verification_status="UNVERIFIED",
            source_tag=DEMO_SOURCE_TAG,
        ),
    ]
    for report in demo_reports:
        db.merge(report)

    db.commit()


def init_demo_database(engine, session_factory) -> None:
    """Create tables (if needed) and seed the baseline demo dataset.

    Intended to run once at FastAPI startup when DEMO_MODE is enabled. Safe
    to call on every restart: table creation is a no-op if tables already
    exist, and seeding is idempotent (see `seed_demo_data`).
    """
    from app.models.base import Base
    # Import the models package so every model class is registered on
    # Base.metadata before create_all() runs.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    db = session_factory()
    try:
        seed_demo_data(db)
    finally:
        db.close()
