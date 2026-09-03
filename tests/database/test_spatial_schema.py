import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from geoalchemy2 import Geometry, Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.admin.dialects import sqlite as geoalchemy_sqlite
from app.models.base import Base
from app.models.user import User, AdminUser, EmergencyContact, EmergencyCirclePreference
from app.models.village import Village, Infrastructure
from app.models.road import Road, RoadCondition
from app.models.safe_zone import SafeZone
from app.models.environmental import EnvironmentalObservation
from app.models.flood import FloodEvent, FloodRisk, RiskFactor
from app.models.report import CitizenReport
from app.models.alert import Alert, NotificationHistory
from app.services.spatial_queries import (
    find_nearest_safe_zones,
    find_nearby_citizen_reports,
    find_infrastructure_in_village,
    calculate_haversine_distance
)

# Mock PostGIS DDL compilation & disable Spatialite listener for SQLite unit testing
@compiles(Geography, "sqlite")
@compiles(Geometry, "sqlite")
def compile_spatial_sqlite(type_, compiler, **kw):
    return "TEXT"

# A valid WKB binary payload representing POINT(0 0) for SQLite result processors
DUMMY_WKB_POINT = b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

@pytest.fixture(autouse=True)
def disable_geoalchemy_sqlite_events():
    orig_after_create = geoalchemy_sqlite.after_create
    geoalchemy_sqlite.after_create = lambda *args, **kwargs: None
    yield
    geoalchemy_sqlite.after_create = orig_after_create

@pytest.fixture
def db_session():
    """In-memory SQLite database session for unit testing ORM models and queries."""
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def register_sqlite_spatial_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function("ST_GeogFromText", 1, lambda val: val)
        dbapi_connection.create_function("ST_GeomFromText", 1, lambda val: val)
        dbapi_connection.create_function("ST_GeomFromText", 2, lambda val, srid: val)
        dbapi_connection.create_function("GeomFromEWKT", 1, lambda val: val)
        dbapi_connection.create_function("ST_GeomFromEWKT", 1, lambda val: val)
        dbapi_connection.create_function("ST_GeogFromEWKT", 1, lambda val: val)
        dbapi_connection.create_function("AsBinary", 1, lambda val: DUMMY_WKB_POINT)
        dbapi_connection.create_function("ST_AsBinary", 1, lambda val: DUMMY_WKB_POINT)
        dbapi_connection.create_function("AsEWKB", 1, lambda val: DUMMY_WKB_POINT)
        dbapi_connection.create_function("ST_AsEWKB", 1, lambda val: DUMMY_WKB_POINT)
        dbapi_connection.create_function("ST_AsGeoJSON", 1, lambda val: val)

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_models_exist():
    """Verify all 17 entities are registered in SQLAlchemy metadata."""
    tables = Base.metadata.tables.keys()
    expected_tables = [
        "users", "admin_users", "emergency_contacts", "emergency_circle_preferences",
        "locations", "villages", "infrastructure", "roads", "road_conditions",
        "safe_zones", "environmental_observations", "flood_events", "flood_risks",
        "risk_factors", "citizen_reports", "alerts", "notification_history"
    ]
    for tbl in expected_tables:
        assert tbl in tables, f"Table '{tbl}' missing from SQLAlchemy metadata"


def test_user_and_emergency_circle_relationships(db_session):
    """Test user creation and emergency circle cascade relationships."""
    user = User(
        phone_number="+919876543210",
        full_name="Aayan Sharma",
        preferred_language="mr"
    )
    db_session.add(user)
    db_session.commit()

    contact = EmergencyContact(
        user_id=user.id,
        contact_name="Father",
        contact_phone="+919811122233",
        relationship="Father",
        is_verified=True
    )
    db_session.add(contact)
    db_session.commit()

    pref = EmergencyCirclePreference(
        contact_id=contact.id,
        notify_on_prepare=False,
        notify_on_critical=True,
        notify_on_distress=True
    )
    db_session.add(pref)
    db_session.commit()

    fetched_user = db_session.query(User).filter_by(phone_number="+919876543210").first()
    assert fetched_user is not None
    assert len(fetched_user.emergency_contacts) == 1
    assert fetched_user.emergency_contacts[0].contact_name == "Father"
    assert fetched_user.emergency_contacts[0].preferences.notify_on_critical is True


def test_village_polygon_and_infrastructure(db_session):
    """Test creation of village boundary polygon and infrastructure relationships."""
    village = Village(
        village_code="VIL-KURLA-01",
        name_en="Kurla Rural",
        district="Kurla",
        state="Maharashtra",
        boundary=WKTElement("POLYGON((72.870 19.070, 72.890 19.070, 72.890 19.090, 72.870 19.090, 72.870 19.070))", srid=4326),
        centroid=WKTElement("POINT(72.880 19.080)", srid=4326),
        source_tag="SIMULATED_DEMO_DATA"
    )
    db_session.add(village)
    db_session.commit()

    infra = Infrastructure(
        village_id=village.id,
        name="Kurla ZP High School",
        type="SCHOOL",
        location=WKTElement("POINT(72.875 19.075)", srid=4326),
        elevation_meters=14.5,
        source_tag="SIMULATED_DEMO_DATA"
    )
    db_session.add(infra)
    db_session.commit()

    infra_items = find_infrastructure_in_village(db_session, str(village.id))
    assert len(infra_items) == 1
    assert infra_items[0]["name"] == "Kurla ZP High School"
    assert infra_items[0]["type"] == "SCHOOL"


def test_nearest_verified_safe_zone_query(db_session):
    """Mandatory Test: Given user coordinates, find nearest VERIFIED & OPERATIONAL safe zone."""
    sz_verified = SafeZone(
        name="Kurla Community Hall",
        type="OFFICIAL_SHELTER",
        location=WKTElement("POINT(72.8850 19.0850)", srid=4326),
        capacity=500,
        current_occupancy=50,
        is_active=True,
        is_verified=True,
        district="Kurla",
        source_tag="SIMULATED_DEMO_DATA"
    )
    sz_unverified = SafeZone(
        name="Unverified School Ground",
        type="COMMUNITY_HALL",
        location=WKTElement("POINT(72.8800 19.0800)", srid=4326),
        capacity=200,
        is_active=True,
        is_verified=False,
        district="Kurla",
        source_tag="SIMULATED_DEMO_DATA"
    )
    db_session.add_all([sz_verified, sz_unverified])
    db_session.commit()

    # Query nearest verified operational safe zones
    results = find_nearest_safe_zones(
        db=db_session,
        latitude=19.0760,
        longitude=72.8777,
        limit=5,
        verified_only=True
    )
    assert len(results) >= 1
    assert results[0]["name"] == "Kurla Community Hall"
    assert results[0]["is_verified"] is True
    assert results[0]["is_active"] is True
    assert results[0]["source_tag"] == "SIMULATED_DEMO_DATA"


def test_haversine_distance_calculation():
    """Verify distance calculation between two latitude/longitude points."""
    dist = calculate_haversine_distance(19.0760, 72.8777, 19.0850, 72.8850)
    assert 1200.0 <= dist <= 1400.0


def test_citizen_report_source_tag(db_session):
    """Verify ground citizen reports carry correct source tagging."""
    user = User(phone_number="+919999988888", full_name="Test Citizen")
    db_session.add(user)
    db_session.commit()

    report = CitizenReport(
        user_id=user.id,
        latitude=19.078,
        longitude=72.879,
        location=WKTElement("POINT(72.879 19.078)", srid=4326),
        description="Water log near bridge",
        disaster_category="ROAD_BLOCKED",
        verification_status="UNVERIFIED",
        source_tag="CITIZEN_REPORT"
    )
    db_session.add(report)
    db_session.commit()

    fetched = db_session.query(CitizenReport).filter_by(user_id=user.id).first()
    assert fetched.source_tag == "CITIZEN_REPORT"
    assert fetched.verification_status == "UNVERIFIED"
