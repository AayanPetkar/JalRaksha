import sys
import uuid
from datetime import datetime, timezone
from geoalchemy2.elements import WKTElement

# Add backend to path for SQLAlchemy models import
sys.path.append("backend")

from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.user import User, AdminUser, EmergencyContact, EmergencyCirclePreference
from app.models.village import Village, Infrastructure
from app.models.road import Road, RoadCondition
from app.models.safe_zone import SafeZone
from app.models.environmental import EnvironmentalObservation
from app.models.flood import FloodEvent, FloodRisk, RiskFactor
from app.models.report import CitizenReport

DEMO_SOURCE_TAG = "SIMULATED_DEMO_DATA"

def seed_database():
    """Seeds synthetic demo dataset for Sangli District, Maharashtra."""
    print("Starting JalRaksha Synthetic Database Seeding...")
    db = SessionLocal()

    try:
        # 1. Seed Village
        village = Village(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            village_code="VIL-SANGLI-01",
            name_en="Sangli Rural",
            name_mr="सांगली ग्रामीण",
            name_hi="सांगली ग्रामीण",
            district="Sangli",
            state="Maharashtra",
            population=14200,
            boundary=WKTElement("POLYGON((72.870 19.070, 72.890 19.070, 72.890 19.090, 72.870 19.090, 72.870 19.070))", srid=4326),
            centroid=WKTElement("POINT(72.880 19.080)", srid=4326),
            source_tag=DEMO_SOURCE_TAG
        )
        db.merge(village)

        # 2. Seed Infrastructure
        infra_items = [
            Infrastructure(
                id=uuid.UUID("22222222-2222-2222-2222-222222222201"),
                village_id=village.id,
                name="Sangli ZP High School",
                type="SCHOOL",
                location=WKTElement("POINT(72.875 19.075)", srid=4326),
                elevation_meters=14.5,
                status="WATCH",
                source_tag=DEMO_SOURCE_TAG
            ),
            Infrastructure(
                id=uuid.UUID("22222222-2222-2222-2222-222222222202"),
                village_id=village.id,
                name="Krishna River Bridge",
                type="BRIDGE",
                location=WKTElement("POINT(72.878 19.078)", srid=4326),
                elevation_meters=10.2,
                status="HIGH_RISK",
                source_tag=DEMO_SOURCE_TAG
            ),
            Infrastructure(
                id=uuid.UUID("22222222-2222-2222-2222-222222222203"),
                village_id=village.id,
                name="Primary Health Center",
                type="HOSPITAL",
                location=WKTElement("POINT(72.882 19.082)", srid=4326),
                elevation_meters=18.0,
                status="OPERATIONAL",
                source_tag=DEMO_SOURCE_TAG
            )
        ]
        for item in infra_items:
            db.merge(item)

        # 3. Seed Roads
        road_a = Road(
            id=uuid.UUID("33333333-3333-3333-3333-333333333301"),
            road_name="Main Road A",
            road_type="HIGHWAY",
            path=WKTElement("LINESTRING(72.870 19.070, 72.880 19.080, 72.890 19.090)", srid=4326),
            base_cost_meters=2400.0,
            district="Sangli",
            source_tag=DEMO_SOURCE_TAG
        )
        db.merge(road_a)

        road_cond_a = RoadCondition(
            id=uuid.UUID("33333333-3333-3333-3333-333333333302"),
            road_id=road_a.id,
            status="OPEN",
            hazard_penalty_multiplier=1.0,
            water_depth_cm=0.0,
            source_tag=DEMO_SOURCE_TAG
        )
        db.merge(road_cond_a)

        # 4. Seed Safe Zones
        sz1 = SafeZone(
            id=uuid.UUID("44444444-4444-4444-4444-444444444401"),
            name="Sangli Community Hall",
            type="OFFICIAL_SHELTER",
            location=WKTElement("POINT(72.8850 19.0850)", srid=4326),
            capacity=500,
            current_occupancy=42,
            is_active=True,
            is_verified=True,
            contact_phone="+919876500111",
            district="Sangli",
            source_tag=DEMO_SOURCE_TAG
        )
        sz2 = SafeZone(
            id=uuid.UUID("44444444-4444-4444-4444-444444444402"),
            name="Sangli Relief Center",
            type="RELIEF_CENTER",
            location=WKTElement("POINT(72.8900 19.0890)", srid=4326),
            capacity=300,
            current_occupancy=10,
            is_active=True,
            is_verified=True,
            contact_phone="+919876500222",
            district="Sangli",
            source_tag=DEMO_SOURCE_TAG
        )
        db.merge(sz1)
        db.merge(sz2)

        # 5. Seed Environmental Observation
        obs = EnvironmentalObservation(
            id=uuid.UUID("55555555-5555-5555-5555-555555555501"),
            station_id="STN-SANGLI-01",
            village_id=village.id,
            rainfall_mm=125.0,
            river_water_level_m=4.2,
            soil_moisture_percentage=88.5,
            temperature_celsius=26.5,
            observed_at=datetime.now(timezone.utc),
            source_tag=DEMO_SOURCE_TAG
        )
        db.merge(obs)

        # 6. Seed Flood Event & Risk
        flood_event = FloodEvent(
            id=uuid.UUID("66666666-6666-6666-6666-666666666601"),
            event_title="Sangli Monsoon Surge 2026",
            affected_district="Sangli",
            severity="CRITICAL",
            started_at=datetime.now(timezone.utc),
            source_tag=DEMO_SOURCE_TAG
        )
        db.merge(flood_event)

        flood_risk = FloodRisk(
            id=uuid.UUID("66666666-6666-6666-6666-666666666602"),
            village_id=village.id,
            flood_event_id=flood_event.id,
            risk_score=84.0,
            risk_level="CRITICAL",
            confidence_score=0.92,
            data_freshness_minutes=7,
            affected_houses_count=320,
            affected_farmland_acres=185.0,
            affected_schools_count=1,
            affected_hospitals_count=0,
            source_tag=DEMO_SOURCE_TAG,
            evaluated_at=datetime.now(timezone.utc)
        )
        db.merge(flood_risk)

        # 7. Seed Demo User & Emergency Circle
        user = User(
            id=uuid.UUID("77777777-7777-7777-7777-777777777701"),
            phone_number="+919876543210",
            full_name="Aayan Sharma",
            preferred_language="mr"
        )
        db.merge(user)

        contact = EmergencyContact(
            id=uuid.UUID("77777777-7777-7777-7777-777777777702"),
            user_id=user.id,
            contact_name="Father",
            contact_phone="+919811122233",
            relationship="Father",
            is_verified=True
        )
        db.merge(contact)

        pref = EmergencyCirclePreference(
            id=uuid.UUID("77777777-7777-7777-7777-777777777703"),
            contact_id=contact.id,
            notify_on_prepare=False,
            notify_on_critical=True,
            notify_on_distress=True
        )
        db_session.merge(pref)

        # 8. Seed Citizen Report
        report = CitizenReport(
            id=uuid.UUID("88888888-8888-8888-8888-888888888801"),
            user_id=user.id,
            latitude=19.078,
            longitude=72.879,
            location=WKTElement("POINT(72.879 19.078)", srid=4326),
            description="Water level reaching road surface near bridge.",
            disaster_category="ROAD_BLOCKED",
            verification_status="UNVERIFIED",
            source_tag="CITIZEN_REPORT"
        )
        db.merge(report)

        db.commit()
        print("JalRaksha Synthetic Database Seeding COMPLETED SUCCESSFULLY!")

    except Exception as e:
        db.rollback()
        print("Seeding encountered exception (expected if DB container not running):", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
