from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    flood_risk,
    admin,
    safe_zones,
    routes,
    emergency_circle,
    reports,
    alerts,
)

api_router = APIRouter()

@api_router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "JalRaksha Backend",
        "version": "0.1.0"
    }

api_router.include_router(auth.router)
api_router.include_router(flood_risk.router)
api_router.include_router(admin.router)
api_router.include_router(safe_zones.router)
api_router.include_router(routes.router)
api_router.include_router(emergency_circle.router)
api_router.include_router(reports.router)
api_router.include_router(alerts.router)
