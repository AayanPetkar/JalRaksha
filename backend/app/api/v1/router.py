from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "JalRaksha Backend",
        "version": "0.1.0"
    }
