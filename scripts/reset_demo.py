#!/usr/bin/env python3
"""Hard-reset the SIH demo database to its clean baseline state.

Usage (from repo root):

    python scripts/reset_demo.py

What it does:
  1. Deletes the SQLite demo database file, if one exists (removes anything
     created live during a previous demo run — e.g. escalated flood risk,
     blocked roads, distress events, extra citizen reports).
  2. Recreates all tables.
  3. Reseeds the baseline SIH demo dataset (LOW risk, no active flood, all
     roads open, no critical alert, seeded demo reports only, no active
     distress) via `app.core.demo_seed.seed_demo_data`.

This only touches the SQLite demo database. It never touches a configured
PostgreSQL/PostGIS database, and does nothing unless DEMO_MODE is enabled.
"""
import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, BACKEND_DIR)

from app.core.config import settings  # noqa: E402


def main() -> None:
    if not settings.DEMO_MODE:
        print("DEMO_MODE is not enabled (see backend/.env or environment variables).")
        print("Refusing to reset — this script only manages the SQLite demo database.")
        sys.exit(1)

    db_url = settings.EFFECTIVE_DATABASE_URL
    if not db_url.startswith("sqlite"):
        print(f"EFFECTIVE_DATABASE_URL is not SQLite ({db_url}); nothing to reset.")
        sys.exit(1)

    # EFFECTIVE_DATABASE_URL is always resolved to an absolute path by
    # Settings, so this matches the exact file the backend itself uses
    # regardless of the current working directory this script is run from.
    db_path = db_url.replace("sqlite:///", "", 1)

    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing demo database: {db_path}")
    else:
        print(f"No existing demo database found at {db_path} (nothing to remove).")

    # Re-create the engine fresh so it points at the (now deleted) file path
    # cleanly, rather than reusing any already-open connection/pool.
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.spatial_compat import install_sqlite_spatial_support
    from app.core.demo_seed import init_demo_database

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    install_sqlite_spatial_support(engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    init_demo_database(engine, session_factory)
    print("Demo database reset complete: fresh LOW-risk baseline state seeded.")


if __name__ == "__main__":
    main()
