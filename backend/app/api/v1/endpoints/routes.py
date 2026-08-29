from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.route_service import get_safest_routes
from app.schemas.route import SafestRouteResponseOut

router = APIRouter()


@router.get("/routes/safest", response_model=SafestRouteResponseOut, tags=["Routes"])
async def safest_route(db: Session = Depends(get_db)):
    return get_safest_routes(db)
