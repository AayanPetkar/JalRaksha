"""Verifies Phase A: SQLite demo runtime + clean, deterministic seeding.

Uses a throwaway temporary SQLite file per test (never the real
`jalraksha_demo.db`), exercising the exact same code path
(`app.core.demo_seed.init_demo_database` / `seed_demo_data`) the FastAPI
startup event and `scripts/reset_demo.py` use.
"""
import os
import tempfile

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.spatial_compat import install_sqlite_spatial_support
from app.core.demo_seed import (
    init_demo_database,
    seed_demo_data,
    DEMO_SOURCE_TAG,
    VILLAGE_ID,
    FLOOD_RISK_ID,
    DEMO_CITIZEN_ID,
    DEMO_CITIZEN_PHONE,
    DEMO_ADMIN_ID,
    DEMO_ADMIN_USERNAME,
    ROAD_A_ID,
    ROAD_B_ID,
    ROAD_C_ID,
    ROAD_A_COND_ID,
    ROAD_B_COND_ID,
    ROAD_C_COND_ID,
    SAFE_ZONE_1_ID,
    SAFE_ZONE_2_ID,
)
from app.models.base import Base
import app.models  # noqa: F401  (registers all models on Base.metadata)
from app.models.user import User, AdminUser
from app.models.road import Road, RoadCondition
from app.models.safe_zone import SafeZone
from app.models.flood import FloodRisk
from app.models.report import CitizenReport


@pytest.fixture()
def demo_engine_session():
    """A fresh, file-backed SQLite engine/session pair per test."""
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test_jalraksha_demo.db")
    db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    install_sqlite_spatial_support(engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield engine, session_factory, db_path

    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)


# 1. Backend / settings default to DEMO_MODE=true with a SQLite URL ---------

def test_demo_mode_defaults_to_sqlite():
    assert settings.DEMO_MODE is True
    assert settings.EFFECTIVE_DATABASE_URL.startswith("sqlite")
    # PostgreSQL configuration must remain intact/available, untouched.
    assert settings.DATABASE_URL.startswith("postgresql")


# 2 & 3. SQLite database + tables are created --------------------------------

def test_sqlite_database_and_tables_are_created(demo_engine_session):
    engine, session_factory, db_path = demo_engine_session
    assert not os.path.exists(db_path)  # not created until init runs

    init_demo_database(engine, session_factory)

    assert os.path.exists(db_path)
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = {
        "users", "admin_users", "villages", "infrastructure",
        "roads", "road_conditions", "safe_zones",
        "environmental_observations", "flood_risks", "risk_factors",
        "citizen_reports", "locations",
    }
    assert expected_tables.issubset(existing_tables)


# 4 & 5. Demo citizen + demo admin exist -------------------------------------

def test_demo_citizen_and_admin_exist(demo_engine_session):
    engine, session_factory, _ = demo_engine_session
    init_demo_database(engine, session_factory)

    db = session_factory()
    try:
        citizen = db.query(User).filter(User.id == DEMO_CITIZEN_ID).first()
        assert citizen is not None
        assert citizen.phone_number == DEMO_CITIZEN_PHONE
        assert citizen.full_name == "Demo Citizen"

        admin = db.query(AdminUser).filter(AdminUser.id == DEMO_ADMIN_ID).first()
        assert admin is not None
        assert admin.username == DEMO_ADMIN_USERNAME
    finally:
        db.close()


# 6. Demo flood risk exists, LOW, ~15-25, no active flood event -------------

def test_demo_flood_risk_is_low_baseline(demo_engine_session):
    engine, session_factory, _ = demo_engine_session
    init_demo_database(engine, session_factory)

    db = session_factory()
    try:
        risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()
        assert risk is not None
        assert risk.village_id == VILLAGE_ID
        assert risk.risk_level == "LOW"
        assert 15.0 <= risk.risk_score <= 25.0
        assert risk.flood_event_id is None
        assert risk.source_tag == DEMO_SOURCE_TAG
    finally:
        db.close()


# 7. Demo safe zones exist, verified + operational ---------------------------

def test_demo_safe_zones_are_verified_and_operational(demo_engine_session):
    engine, session_factory, _ = demo_engine_session
    init_demo_database(engine, session_factory)

    db = session_factory()
    try:
        zones = db.query(SafeZone).all()
        assert len(zones) >= 2
        seeded_ids = {z.id for z in zones}
        assert SAFE_ZONE_1_ID in seeded_ids
        assert SAFE_ZONE_2_ID in seeded_ids
        for zone in zones:
            assert zone.is_active is True
            assert zone.is_verified is True
            assert zone.source_tag == DEMO_SOURCE_TAG
    finally:
        db.close()


# 8. Demo roads/routes A, B, C exist and are open ----------------------------

def test_demo_routes_exist_and_are_open(demo_engine_session):
    engine, session_factory, _ = demo_engine_session
    init_demo_database(engine, session_factory)

    db = session_factory()
    try:
        for road_id, cond_id in [
            (ROAD_A_ID, ROAD_A_COND_ID),
            (ROAD_B_ID, ROAD_B_COND_ID),
            (ROAD_C_ID, ROAD_C_COND_ID),
        ]:
            road = db.query(Road).filter(Road.id == road_id).first()
            condition = db.query(RoadCondition).filter(RoadCondition.id == cond_id).first()
            assert road is not None
            assert condition is not None
            assert condition.road_id == road_id
            assert condition.status == "OPEN"
            assert road.base_cost_meters > 0
    finally:
        db.close()


# 9. Demo data is labelled SIMULATED_DEMO_DATA -------------------------------

def test_seeded_data_is_labelled_simulated_demo_data(demo_engine_session):
    engine, session_factory, _ = demo_engine_session
    init_demo_database(engine, session_factory)

    db = session_factory()
    try:
        risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()
        zones = db.query(SafeZone).all()
        roads = db.query(Road).all()
        reports = db.query(CitizenReport).all()

        assert risk.source_tag == DEMO_SOURCE_TAG
        assert all(z.source_tag == DEMO_SOURCE_TAG for z in zones)
        assert all(r.source_tag == DEMO_SOURCE_TAG for r in roads)
        assert len(reports) > 0
        assert all(r.source_tag == DEMO_SOURCE_TAG for r in reports)
    finally:
        db.close()


# 10. Re-running initialization does not create duplicate records -----------

def test_reseeding_does_not_duplicate_records(demo_engine_session):
    engine, session_factory, _ = demo_engine_session
    init_demo_database(engine, session_factory)
    init_demo_database(engine, session_factory)
    init_demo_database(engine, session_factory)

    db = session_factory()
    try:
        assert db.query(User).filter(User.id == DEMO_CITIZEN_ID).count() == 1
        assert db.query(AdminUser).filter(AdminUser.id == DEMO_ADMIN_ID).count() == 1
        assert db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).count() == 1
        assert db.query(SafeZone).count() == 2
        assert db.query(Road).count() == 3
        assert db.query(CitizenReport).count() == 2
    finally:
        db.close()


# 11. Resetting the demo returns it to the original LOW-risk state ----------

def test_reseeding_restores_low_risk_baseline_after_mutation(demo_engine_session):
    engine, session_factory, _ = demo_engine_session
    init_demo_database(engine, session_factory)

    # Simulate what a future "Simulate Flood" / "Block Road" endpoint would
    # do to the seeded rows during a live demo.
    db = session_factory()
    try:
        risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()
        risk.risk_score = 91.0
        risk.risk_level = "CRITICAL"

        road_condition = db.query(RoadCondition).filter(RoadCondition.id == ROAD_A_COND_ID).first()
        road_condition.status = "BLOCKED"
        road_condition.water_depth_cm = 45.0
        db.commit()
    finally:
        db.close()

    # Verify the mutation actually took effect before reset.
    db = session_factory()
    try:
        mutated_risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()
        assert mutated_risk.risk_level == "CRITICAL"
    finally:
        db.close()

    # Reseed (same call the app makes on every startup / reset script uses).
    db = session_factory()
    try:
        seed_demo_data(db)
    finally:
        db.close()

    db = session_factory()
    try:
        risk = db.query(FloodRisk).filter(FloodRisk.id == FLOOD_RISK_ID).first()
        assert risk.risk_level == "LOW"
        assert 15.0 <= risk.risk_score <= 25.0

        road_condition = db.query(RoadCondition).filter(RoadCondition.id == ROAD_A_COND_ID).first()
        assert road_condition.status == "OPEN"
        assert road_condition.water_depth_cm == 0.0
    finally:
        db.close()
