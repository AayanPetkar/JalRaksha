from typing import List
from pydantic import BaseModel


class RouteOut(BaseModel):
    route_name: str
    distance_meters: float
    estimated_time_minutes: int
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH'
    risk_score: float
    road_status: str  # 'OPEN', 'WATCH', 'HIGH_RISK', 'BLOCKED', 'SUBMERGED'
    recommended: bool
    source_tag: str = "SIMULATED_DEMO_DATA"


class SafestRouteResponseOut(BaseModel):
    disclaimer: str = "Safest Available Route based on currently available data."
    routes: List[RouteOut]
