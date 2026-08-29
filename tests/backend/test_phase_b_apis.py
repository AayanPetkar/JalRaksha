"""Phase B: minimal FastAPI demo API tests.

Uses FastAPI's TestClient against the real `app` object with the `get_db`
dependency overridden to point at a throwaway, per-test SQLite file (never
the real `jalraksha_demo.db`). Each test's database is seeded via the exact
same `init_demo_database` / `seed_demo_data` code path the live server uses,
so these tests exercise real endpoint <-> service <-> DB wiring, not mocks.
"""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.core.spatial_compat import install_sqlite_spatial_support
from app.core.demo_seed import init_demo_database


@pytest.fixture()
def client():
    """A TestClient wired to a fresh, seeded, throwaway SQLite database."""
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test_phase_b.db")
    db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    install_sqlite_spatial_support(engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    init_demo_database(engine, session_factory)

    def _override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db

    # Not used as a context manager on purpose: this avoids triggering the
    # app's own DEMO_MODE startup event (which seeds the *real*
    # jalraksha_demo.db on the backend's configured EFFECTIVE_DATABASE_URL).
    # Seeding for these tests is handled explicitly above, against the
    # isolated temp file.
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.pop(get_db, None)
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)


def _demo_token(client: TestClient) -> str:
    resp = client.post("/api/v1/demo/login")
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _auth_headers(client: TestClient) -> dict:
    return {"Authorization": f"Bearer {_demo_token(client)}"}


# 1. Demo login -------------------------------------------------------------

def test_demo_login(client):
    resp = client.post("/api/v1/demo/login")
    assert resp.status_code == 200
    body = resp.json()
    assert body["phone_number"] == "0000000000"
    assert body["full_name"] == "Demo Citizen"
    assert body["access_token"]

    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["full_name"] == "Demo Citizen"


# 2. Current LOW risk ---------------------------------------------------------

def test_current_risk_is_low_baseline(client):
    resp = client.get("/api/v1/flood-risk/current")
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] == "LOW"
    assert 15.0 <= body["risk_score"] <= 25.0
    assert body["source_tag"] == "SIMULATED_DEMO_DATA"
    assert body["is_demo_data"] is True
    assert "not an official government warning" in body["disclaimer"]
    assert len(body["main_risk_factors"]) == 4


# 3. Why explanation ----------------------------------------------------------

def test_why_explanation_matches_current_state(client):
    resp = client.get("/api/v1/flood-risk/current/why")
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] == "LOW"
    factor_keys = {f["factor_key"] for f in body["contributing_factors"]}
    assert factor_keys == {"HEAVY_RAINFALL", "RIVER_LEVEL", "SOIL_SATURATION", "LOW_ELEVATION"}
    # Every factor has a human-readable explanation; rainfall/river/soil have value+unit.
    rainfall = next(f for f in body["contributing_factors"] if f["factor_key"] == "HEAVY_RAINFALL")
    assert rainfall["value"] == 18.0
    assert rainfall["unit"] == "mm"
    assert rainfall["description_en"]
    assert rainfall["description_mr"]
    assert rainfall["description_hi"]


# 4. Simulate flood -----------------------------------------------------------

def test_simulate_flood_returns_critical_state(client):
    resp = client.post("/api/v1/admin/simulate-flood")
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] == "CRITICAL"
    assert body["risk_score"] == pytest.approx(87.0)


# 5. Risk becomes CRITICAL (persisted, visible on subsequent GET) ------------

def test_risk_becomes_critical_after_simulate_flood(client):
    client.post("/api/v1/admin/simulate-flood")
    resp = client.get("/api/v1/flood-risk/current")
    body = resp.json()
    assert body["risk_level"] == "CRITICAL"
    assert body["risk_score"] == pytest.approx(87.0)

    why = client.get("/api/v1/flood-risk/current/why").json()
    assert why["risk_level"] == "CRITICAL"
    rainfall = next(f for f in why["contributing_factors"] if f["factor_key"] == "HEAVY_RAINFALL")
    assert rainfall["value"] == 125.0


# 6. Critical alert exists ------------------------------------------------------

def test_critical_alert_exists_after_simulate_flood(client):
    client.post("/api/v1/admin/simulate-flood")
    resp = client.get("/api/v1/alerts")
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) == 1
    assert alerts[0]["alert_level"] == "CRITICAL"
    assert alerts[0]["source_tag"] == "SIMULATED_DEMO_DATA"
    assert "not an official government warning" in alerts[0]["message_en"] or \
           "not an official" in alerts[0]["message_en"]


def test_no_alerts_at_baseline(client):
    resp = client.get("/api/v1/alerts")
    assert resp.status_code == 200
    assert resp.json() == []


# 7. Safe-zone endpoint ----------------------------------------------------------

def test_safe_zone_endpoint(client):
    resp = client.get("/api/v1/safe-zones/nearby?latitude=19.078&longitude=72.879")
    assert resp.status_code == 200
    zones = resp.json()
    assert len(zones) >= 2
    for zone in zones:
        assert zone["is_active"] is True
        assert zone["is_verified"] is True
        assert zone["latitude"] is not None
        assert zone["longitude"] is not None
        assert zone["source_tag"] == "SIMULATED_DEMO_DATA"
    # Nearer zone (Community Hall) should sort before the farther Relief Center.
    assert zones[0]["distance_meters"] <= zones[1]["distance_meters"]


# 8. Initial safest route -----------------------------------------------------

def test_initial_safest_route_is_route_a(client):
    resp = client.get("/api/v1/routes/safest")
    assert resp.status_code == 200
    body = resp.json()
    assert body["disclaimer"] == "Safest Available Route based on currently available data."
    assert "100% safe" not in body["disclaimer"]
    routes = body["routes"]
    assert len(routes) == 3
    recommended = [r for r in routes if r["recommended"]]
    assert len(recommended) == 1
    assert recommended[0]["route_name"].startswith("Route A")
    assert all(r["road_status"] == "OPEN" for r in routes)


# 9. Block road ----------------------------------------------------------------

def test_block_road(client):
    resp = client.post("/api/v1/admin/simulate-blocked-road")
    assert resp.status_code == 200
    body = resp.json()
    assert body["previous_status"] == "OPEN"
    assert body["new_status"] == "BLOCKED"
    assert body["source_tag"] == "SIMULATED_DEMO_DATA"
    assert "Route A" in body["road_name"] or "Main Road" in body["road_name"]


# 10. Safest route changes after block ------------------------------------------

def test_safest_route_changes_after_block(client):
    client.post("/api/v1/admin/simulate-blocked-road")
    resp = client.get("/api/v1/routes/safest")
    routes = resp.json()["routes"]

    route_a = next(r for r in routes if r["route_name"].startswith("Route A"))
    assert route_a["road_status"] == "BLOCKED"
    assert route_a["recommended"] is False

    recommended = [r for r in routes if r["recommended"]]
    assert len(recommended) == 1
    assert not recommended[0]["route_name"].startswith("Route A")


# 11. Restore normal -------------------------------------------------------------

def test_restore_normal(client):
    client.post("/api/v1/admin/simulate-flood")
    client.post("/api/v1/admin/simulate-blocked-road")

    resp = client.post("/api/v1/admin/simulate-normal")
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] == "LOW"
    assert body["risk_score"] == pytest.approx(20.0)

    routes = client.get("/api/v1/routes/safest").json()["routes"]
    assert all(r["road_status"] == "OPEN" for r in routes)
    recommended = [r for r in routes if r["recommended"]]
    assert recommended[0]["route_name"].startswith("Route A")

    alerts = client.get("/api/v1/alerts").json()
    assert alerts == []

    # Idempotent / no duplicate seed rows after a second restore.
    client.post("/api/v1/admin/simulate-normal")
    overview = client.get("/api/v1/admin/overview").json()
    assert overview["operational_safe_zones_count"] == 2


# 12. I'm Safe --------------------------------------------------------------------

def test_im_safe(client):
    headers = _auth_headers(client)
    resp = client.post(
        "/api/v1/emergency-circle/im-safe",
        headers=headers,
        json={"latitude": 19.085, "longitude": 72.885, "custom_message": "Reached shelter"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status_type"] == "SAFE"
    assert body["message"] == "Emergency request recorded."
    assert "dispatched" not in body["message"].lower()


# 13. Need Help --------------------------------------------------------------------

def test_need_help(client):
    headers = _auth_headers(client)
    resp = client.post(
        "/api/v1/emergency-circle/need-help",
        headers=headers,
        json={"latitude": 19.078, "longitude": 72.879, "distress_type": "TRAPPED_WATER"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status_type"] == "NEED_HELP"
    assert body["distress_type"] == "TRAPPED_WATER"
    assert body["message"] == "Emergency request recorded."


def test_emergency_circle_requires_auth(client):
    resp = client.post(
        "/api/v1/emergency-circle/need-help",
        json={"latitude": 19.078, "longitude": 72.879, "distress_type": "TRAPPED_WATER"},
    )
    assert resp.status_code == 401


# 14. Distress appears in admin -----------------------------------------------------

def test_distress_appears_in_admin(client):
    headers = _auth_headers(client)
    client.post(
        "/api/v1/emergency-circle/need-help",
        headers=headers,
        json={"latitude": 19.078, "longitude": 72.879, "distress_type": "TRAPPED_WATER"},
    )
    resp = client.get("/api/v1/admin/distress-signals")
    assert resp.status_code == 200
    signals = resp.json()
    assert len(signals) == 1
    assert signals[0]["user_name"] == "Demo Citizen"
    assert signals[0]["distress_type"] == "TRAPPED_WATER"


# 15. Submit citizen report -----------------------------------------------------------

def test_submit_citizen_report(client):
    headers = _auth_headers(client)
    resp = client.post(
        "/api/v1/reports",
        headers=headers,
        json={
            "latitude": 19.079,
            "longitude": 72.880,
            "description": "Water rising near main road",
            "disaster_category": "WATER_LOGGING",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["verification_status"] == "UNVERIFIED"
    assert body["source_tag"] == "CITIZEN_REPORT"


def test_submit_report_requires_auth(client):
    resp = client.post(
        "/api/v1/reports",
        json={"latitude": 19.079, "longitude": 72.880, "disaster_category": "WATER_LOGGING"},
    )
    assert resp.status_code == 401


# 16. Admin sees report -----------------------------------------------------------------

def test_admin_sees_report(client):
    headers = _auth_headers(client)
    submitted = client.post(
        "/api/v1/reports",
        headers=headers,
        json={
            "latitude": 19.079,
            "longitude": 72.880,
            "description": "Water rising near main road",
            "disaster_category": "WATER_LOGGING",
        },
    ).json()

    resp = client.get("/api/v1/admin/reports")
    assert resp.status_code == 200
    report_ids = [r["id"] for r in resp.json()]
    assert submitted["id"] in report_ids


# 17. Verify report -----------------------------------------------------------------------

def test_verify_report(client):
    headers = _auth_headers(client)
    submitted = client.post(
        "/api/v1/reports",
        headers=headers,
        json={"latitude": 19.079, "longitude": 72.880, "disaster_category": "ROAD_BLOCKED"},
    ).json()

    resp = client.post(f"/api/v1/admin/reports/{submitted['id']}/verify")
    assert resp.status_code == 200
    assert resp.json()["verification_status"] == "VERIFIED"


def test_verify_nonexistent_report_returns_404(client):
    resp = client.post("/api/v1/admin/reports/00000000-0000-0000-0000-000000000000/verify")
    assert resp.status_code == 404
    assert "detail" in resp.json()


# 18. Admin overview -----------------------------------------------------------------------

def test_admin_overview(client):
    resp = client.get("/api/v1/admin/overview")
    assert resp.status_code == 200
    body = resp.json()
    assert body["current_risk_level"] == "LOW"
    assert body["current_risk_score"] == pytest.approx(20.0)
    assert body["operational_safe_zones_count"] == 2
    assert body["citizen_reports_count"] == 2  # the two seeded demo reports
    assert body["distress_signals_count"] == 0
    assert body["affected_roads_count"] == 0


# ---------------------------------------------------------------------------
# Full integration test: LOW -> flood -> CRITICAL -> block road -> route
# changes -> need help -> report -> admin sees report -> verify -> restore
# normal -> LOW.
# ---------------------------------------------------------------------------

def test_full_demo_flow_integration(client):
    headers = _auth_headers(client)

    # LOW baseline
    risk = client.get("/api/v1/flood-risk/current").json()
    assert risk["risk_level"] == "LOW"

    # Admin triggers simulated flood -> CRITICAL
    flood_resp = client.post("/api/v1/admin/simulate-flood").json()
    assert flood_resp["risk_level"] == "CRITICAL"
    assert flood_resp["risk_score"] == pytest.approx(87.0)

    # Citizen "receives" the simulated alert
    alerts = client.get("/api/v1/alerts").json()
    assert len(alerts) == 1
    assert alerts[0]["source_tag"] == "SIMULATED_DEMO_DATA"

    # Citizen checks why they're at risk
    why = client.get("/api/v1/flood-risk/current/why").json()
    assert why["risk_level"] == "CRITICAL"
    assert len(why["contributing_factors"]) == 4

    # Citizen checks nearby safe zone
    zones = client.get("/api/v1/safe-zones/nearby?latitude=19.078&longitude=72.879").json()
    assert len(zones) >= 1

    # Citizen checks safest route -> Route A recommended (not yet blocked)
    routes_before = client.get("/api/v1/routes/safest").json()["routes"]
    recommended_before = next(r for r in routes_before if r["recommended"])
    assert recommended_before["route_name"].startswith("Route A")

    # Admin blocks Route A
    block_resp = client.post("/api/v1/admin/simulate-blocked-road").json()
    assert block_resp["new_status"] == "BLOCKED"

    # Route recommendation changes
    routes_after = client.get("/api/v1/routes/safest").json()["routes"]
    recommended_after = next(r for r in routes_after if r["recommended"])
    assert not recommended_after["route_name"].startswith("Route A")

    # Citizen presses Need Help
    help_resp = client.post(
        "/api/v1/emergency-circle/need-help",
        headers=headers,
        json={"latitude": 19.078, "longitude": 72.879, "distress_type": "TRAPPED_WATER"},
    )
    assert help_resp.status_code == 200

    # Emergency event visible to admin
    distress = client.get("/api/v1/admin/distress-signals").json()
    assert len(distress) == 1

    # Citizen submits a flood report
    report = client.post(
        "/api/v1/reports",
        headers=headers,
        json={
            "latitude": 19.079,
            "longitude": 72.880,
            "description": "Road impassable near main bridge",
            "disaster_category": "ROAD_BLOCKED",
        },
    ).json()
    assert report["verification_status"] == "UNVERIFIED"

    # Admin sees the report
    admin_reports = client.get("/api/v1/admin/reports").json()
    assert report["id"] in [r["id"] for r in admin_reports]

    # Admin verifies the report
    verify_resp = client.post(f"/api/v1/admin/reports/{report['id']}/verify").json()
    assert verify_resp["verification_status"] == "VERIFIED"

    # Admin overview reflects the escalated state
    overview = client.get("/api/v1/admin/overview").json()
    assert overview["current_risk_level"] == "CRITICAL"
    assert overview["distress_signals_count"] == 1
    assert overview["affected_roads_count"] >= 1

    # Admin restores normal -> LOW, roads open, no alert
    restore_resp = client.post("/api/v1/admin/simulate-normal").json()
    assert restore_resp["risk_level"] == "LOW"
    assert restore_resp["risk_score"] == pytest.approx(20.0)

    final_routes = client.get("/api/v1/routes/safest").json()["routes"]
    assert all(r["road_status"] == "OPEN" for r in final_routes)
    final_recommended = next(r for r in final_routes if r["recommended"])
    assert final_recommended["route_name"].startswith("Route A")

    final_alerts = client.get("/api/v1/alerts").json()
    assert final_alerts == []

    final_risk = client.get("/api/v1/flood-risk/current").json()
    assert final_risk["risk_level"] == "LOW"
    assert final_risk["risk_score"] == pytest.approx(20.0)
