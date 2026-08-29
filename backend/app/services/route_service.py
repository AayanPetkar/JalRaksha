"""Demo 'safest route' selection.

No real routing engine (OSRM/pgRouting) is used. Instead, three predefined,
independent named demo routes are seeded in Phase A (`app.core.demo_seed`);
this module scores each by its current `RoadCondition` and applies a simple,
explicit selection rule:

    1. Exclude blocked/unavailable routes.
    2. Compare remaining route risk.
    3. Select the route with the lowest risk.
    4. If risk is equal, prefer the shorter route.
"""
from typing import List
from sqlalchemy.orm import Session
from app.models.road import Road, RoadCondition
from app.schemas.route import RouteOut, SafestRouteResponseOut
from app.core.demo_seed import ROAD_A_ID, ROAD_B_ID, ROAD_C_ID, DEMO_SOURCE_TAG

ROUTE_DEFINITIONS = [
    {"name": "Route A - Main Road via Krishna Bridge", "road_id": ROAD_A_ID},
    {"name": "Route B - Riverside Lane", "road_id": ROAD_B_ID},
    {"name": "Route C - Highway Bypass", "road_id": ROAD_C_ID},
]

# Average human evacuation walking pace (~5 km/h), used only to give the
# demo a plausible "estimated time" figure alongside distance.
WALKING_SPEED_M_PER_MIN = 83.3

STATUS_BASE_RISK = {
    "OPEN": 5.0,
    "WATCH": 30.0,
    "HIGH_RISK": 65.0,
    "BLOCKED": 100.0,
    "SUBMERGED": 100.0,
}
UNAVAILABLE_STATUSES = {"BLOCKED", "SUBMERGED"}


def _risk_level_for_score(score: float) -> str:
    if score < 20:
        return "LOW"
    if score < 50:
        return "MEDIUM"
    return "HIGH"


def get_safest_routes(db: Session) -> SafestRouteResponseOut:
    candidates = []
    for definition in ROUTE_DEFINITIONS:
        road = db.query(Road).filter(Road.id == definition["road_id"]).first()
        condition = db.query(RoadCondition).filter(RoadCondition.road_id == definition["road_id"]).first()
        if not road or not condition:
            continue

        base_risk = STATUS_BASE_RISK.get(condition.status, 50.0)
        risk_score = min(100.0, base_risk + condition.water_depth_cm * 0.5)
        available = condition.status not in UNAVAILABLE_STATUSES

        candidates.append({
            "route_name": definition["name"],
            "distance_meters": road.base_cost_meters,
            "estimated_time_minutes": max(1, round(road.base_cost_meters / WALKING_SPEED_M_PER_MIN)),
            "risk_level": _risk_level_for_score(risk_score),
            "risk_score": round(risk_score, 1),
            "road_status": condition.status,
            "available": available,
            "source_tag": condition.source_tag or road.source_tag or DEMO_SOURCE_TAG,
        })

    # 1. Exclude blocked/unavailable routes.
    available_routes = [c for c in candidates if c["available"]]

    # 2 & 3 & 4: lowest risk wins; ties broken by shorter distance.
    best = None
    if available_routes:
        best = sorted(available_routes, key=lambda c: (c["risk_score"], c["distance_meters"]))[0]

    routes_out: List[RouteOut] = []
    for c in candidates:
        routes_out.append(RouteOut(
            route_name=c["route_name"],
            distance_meters=c["distance_meters"],
            estimated_time_minutes=c["estimated_time_minutes"],
            risk_level=c["risk_level"],
            risk_score=c["risk_score"],
            road_status=c["road_status"],
            recommended=(best is not None and c["route_name"] == best["route_name"]),
            source_tag=c["source_tag"],
        ))

    return SafestRouteResponseOut(routes=routes_out)
