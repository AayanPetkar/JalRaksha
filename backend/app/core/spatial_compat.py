"""SQLite compatibility shim for geoalchemy2 spatial columns/functions.

The production data model (`app/models/*.py`) uses PostGIS-native
`geoalchemy2.Geometry` / `geoalchemy2.Geography` columns and PostGIS spatial
functions (`ST_Distance`, `ST_DWithin`, `ST_MakePoint`, ...). PostGIS is not
available in the SQLite-based SIH demo runtime.

This module makes the *same* SQLAlchemy models usable against a plain SQLite
file by:
  1. Compiling Geometry/Geography columns as TEXT on the "sqlite" dialect
     (coordinates are stored as WKT strings instead of PostGIS geography).
  2. Registering no-op/pass-through implementations of the PostGIS function
     names the codebase calls, so existing service code does not need to
     branch on database backend.
  3. Disabling geoalchemy2's own SQLite/SpatiaLite DDL listener, which would
     otherwise try to load the `mod_spatialite` extension (not installed
     here) during `CREATE TABLE`.

This pattern already exists and is proven working in
`tests/database/test_spatial_schema.py`; it is centralized here so the
running backend (not just the test suite) benefits from it.

No PostgreSQL/PostGIS code path is touched. This module has no effect unless
the active engine's dialect is "sqlite".
"""
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.compiler import compiles
from geoalchemy2 import Geometry, Geography
from geoalchemy2.admin.dialects import sqlite as geoalchemy_sqlite

# A valid WKB payload representing POINT(0 0), used as a harmless stand-in
# wherever code asks SQLite to decode a geometry back out of the database.
_DUMMY_WKB_POINT = b"\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

_compilers_installed = False


def _compile_spatial_as_text():
    @compiles(Geography, "sqlite")
    @compiles(Geometry, "sqlite")
    def _compile_spatial_sqlite(type_, compiler, **kw):  # pragma: no cover - trivial
        return "TEXT"


def _register_sqlite_spatial_functions(dbapi_connection, connection_record):
    dbapi_connection.create_function("ST_GeogFromText", 1, lambda val: val)
    dbapi_connection.create_function("ST_GeomFromText", 1, lambda val: val)
    dbapi_connection.create_function("ST_GeomFromText", 2, lambda val, srid: val)
    dbapi_connection.create_function("GeomFromEWKT", 1, lambda val: val)
    dbapi_connection.create_function("ST_GeomFromEWKT", 1, lambda val: val)
    dbapi_connection.create_function("ST_GeogFromEWKT", 1, lambda val: val)
    dbapi_connection.create_function("AsBinary", 1, lambda val: _DUMMY_WKB_POINT)
    dbapi_connection.create_function("ST_AsBinary", 1, lambda val: _DUMMY_WKB_POINT)
    dbapi_connection.create_function("AsEWKB", 1, lambda val: _DUMMY_WKB_POINT)
    dbapi_connection.create_function("ST_AsEWKB", 1, lambda val: _DUMMY_WKB_POINT)
    dbapi_connection.create_function("ST_AsGeoJSON", 1, lambda val: val)


def install_sqlite_spatial_support(engine: Engine) -> None:
    """Enable geoalchemy2 columns + PostGIS-named functions on a SQLite engine.

    Safe to call multiple times, including with multiple distinct engines
    (e.g. one per test). The column-compilation registration is process-wide
    and only needs to happen once; the connect-event listener that provides
    the spatial SQL functions is engine-specific and is (re-)attached for
    every engine passed in, since each engine gets its own DBAPI
    connections.
    """
    global _compilers_installed
    if engine.dialect.name != "sqlite":
        return

    if not _compilers_installed:
        _compile_spatial_as_text()
        # Prevent geoalchemy2 from attempting to load mod_spatialite during
        # CREATE TABLE / DROP TABLE against plain SQLite.
        geoalchemy_sqlite.after_create = lambda *args, **kwargs: None
        geoalchemy_sqlite.before_drop = lambda *args, **kwargs: None
        _compilers_installed = True

    if not getattr(engine, "_jalraksha_spatial_functions_installed", False):
        event.listen(engine, "connect", _register_sqlite_spatial_functions)
        engine._jalraksha_spatial_functions_installed = True
