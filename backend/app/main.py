from fastapi import FastAPI, HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    """Clean, uniform error body for 400/401/403/404/409 etc. Never leaks
    internals — `exc.detail` is always a message we set ourselves."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """422 for malformed/invalid request bodies, without echoing raw internals."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data.", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    """Catch-all: never expose a stack trace to the client."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.on_event("startup")
async def initialize_demo_runtime() -> None:
    """In DEMO_MODE, make startup deterministic and self-contained.

    Creates the SQLite demo database (if needed) and seeds/reseeds the
    baseline SIH demo dataset, so `uvicorn app.main:app` alone is enough to
    reach a ready, predictable demo state — no PostgreSQL, Docker, Redis, or
    Alembic required. Has no effect when DEMO_MODE is false (production /
    PostgreSQL path is untouched and does not auto-seed).
    """
    if not settings.DEMO_MODE:
        return

    from app.core.database import engine, SessionLocal
    from app.core.demo_seed import init_demo_database

    init_demo_database(engine, SessionLocal)


@app.get("/")
async def root():
    return {
        "message": "Welcome to JalRaksha API - The Flood Relief, Reminder & Safety Expert",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
