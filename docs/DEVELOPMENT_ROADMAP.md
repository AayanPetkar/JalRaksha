# Development Roadmap — JalRaksha

This document specifies the staged 15-phase implementation plan for building **JalRaksha — The Flood Relief, Reminder & Safety Expert**.

---

## Phase Breakdown Matrix

| Phase | Title | Core Goal | Primary Module |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Project Foundation | Project scaffolding & architecture docs | Root / Docs |
| **Phase 2** | Database & Spatial Schema | PostGIS schema, tables, spatial indexes | `database/` |
| **Phase 3** | FastAPI Core Backend | REST API gateway, CRUD endpoints, DB connection | `backend/` |
| **Phase 4** | Flutter Mobile Client UI | Mobile layout, screens, components | `mobile/` |
| **Phase 5** | Flutter + Backend Integration | Mobile HTTP client integration with FastAPI | `mobile/` + `backend/` |
| **Phase 6** | GPS & Interactive Maps | Mapbox rendering, user location tracking | `mobile/` + `backend/` |
| **Phase 7** | Flood ML Model & Pipeline | XGBoost model, SHAP explainability engine | `ml/` |
| **Phase 8** | Alert Engine & FCM/SMS | FCM push + SMS gateway dispatch pipeline | `backend/` |
| **Phase 9** | Emergency Circle & Quick Actions | Contact management, "I'm Safe", "Need Help" | `mobile/` + `backend/` |
| **Phase 10** | Citizen Ground Reporting | Photo, GPS, voice report submission & triage | `mobile/` + `backend/` |
| **Phase 11** | Safest Route Navigation Engine | Risk-weighted routing avoiding flood hazards | `backend/` + `mobile/` |
| **Phase 12** | Admin Disaster Dashboard | Regional monitoring map, alert dispatch web UI | `admin-dashboard/` |
| **Phase 13** | Offline Support & Local Sync | Hive/SQLite local caching, offline sync queue | `mobile/` |
| **Phase 14** | Automated Testing & QA | Integration, unit, and spatial routing test suite | `tests/` |
| **Phase 15** | SIH Demonstration Mode | Synthetic demo data provider & pitch preset | Root / All |

---

## Detailed Phase Specifications

### PHASE 1 — Project Foundation
- **Goal**: Establish technical architecture, documentation suite, monorepo project structure, and basic container scaffolding.
- **Features**: Architectural documentation, `.env.example`, initial directory skeletons for all modules.
- **Dependencies**: None.
- **Files/Modules Involved**: `docs/`, `.env.example`, `docker-compose.yml`, sub-folder manifests (`pubspec.yaml`, `requirements.txt`, `package.json`).
- **Tests Required**: Configuration syntax validation, docker file verification.
- **Definition of Done (DoD)**: All 6 architecture documents written, monorepo folders created, scaffolding passes initial sanity checks.

### PHASE 2 — Database Setup & Spatial Schema
- **Goal**: Provision PostgreSQL + PostGIS database container and execute DDL schemas for spatial entities, users, roads, and flood risks.
- **Features**: PostGIS extensions, tables (`users`, `villages`, `roads`, `safe_zones`, `flood_risks`, `citizen_reports`), spatial GIST indexes.
- **Dependencies**: Phase 1.
- **Files/Modules Involved**: `database/init.sql`, `database/Dockerfile`, `backend/app/core/database.py`.
- **Tests Required**: Database migration test, spatial query benchmark (`ST_DWithin`, `ST_Contains`).
- **Definition of Done (DoD)**: PostgreSQL + PostGIS container boots cleanly, all 17 tables created with spatial indexes verified.

### PHASE 3 — FastAPI Core Backend
- **Goal**: Implement FastAPI application structure, authentication middleware (JWT), database ORM connections, and core health check endpoints.
- **Features**: Authentication endpoints (`/auth/request-otp`, `/auth/verify-otp`), user profile CRUD, CORS middleware, error handling.
- **Dependencies**: Phase 2.
- **Files/Modules Involved**: `backend/app/main.py`, `backend/app/api/v1/router.py`, `backend/app/models/`, `backend/app/schemas/`.
- **Tests Required**: Pytest API endpoint unit tests, JWT token generation/validation tests.
- **Definition of Done (DoD)**: Backend boots on port 8000, OpenAPI docs accessible at `/docs`, Auth endpoints functional.

### PHASE 4 — Flutter Mobile Client UI
- **Goal**: Build the core Flutter user interface screens adhering to modern design principles, supporting Marathi, Hindi, and English.
- **Features**: Splash screen, Home Risk Dashboard, "Why?" Explainability Modal, Emergency Circle Screen, Citizen Reporting Form, Language Selector.
- **Dependencies**: Phase 1.
- **Files/Modules Involved**: `mobile/lib/main.dart`, `mobile/lib/features/`, `mobile/pubspec.yaml`.
- **Tests Required**: Flutter widget layout tests, internationalization string loading tests.
- **Definition of Done (DoD)**: Flutter app builds cleanly on Android/iOS emulators, rendering mock screens in 3 languages.

### PHASE 5 — Flutter + Backend Integration
- **Goal**: Connect Flutter mobile application to FastAPI backend endpoints via HTTP client.
- **Features**: User authentication flow, profile sync, location sending, live risk score retrieval.
- **Dependencies**: Phase 3, Phase 4.
- **Files/Modules Involved**: `mobile/lib/core/network/`, `mobile/lib/features/auth/`, `backend/app/api/v1/endpoints/`.
- **Tests Required**: End-to-end integration test (Mobile login -> Backend token verification -> User data returned).
- **Definition of Done (DoD)**: Mobile app performs successful authentication and displays real data from backend API.

### PHASE 6 — GPS & Interactive Maps
- **Goal**: Integrate Mapbox / OpenStreetMap vector tile renderer into Flutter client and implement user GPS tracking.
- **Features**: Interactive map display, current user GPS marker, village risk heatmaps, safe zone pins.
- **Dependencies**: Phase 5.
- **Files/Modules Involved**: `mobile/lib/features/home/map_widget.dart`, `backend/app/api/v1/endpoints/locations.py`.
- **Tests Required**: GPS permission handler test, spatial tile loading test.
- **Definition of Done (DoD)**: User location is accurately rendered on interactive vector map with risk overlay layers.

### PHASE 7 — Flood ML Model & Pipeline
- **Goal**: Implement Python XGBoost risk scoring model and SHAP explainability engine using Data Provider abstraction.
- **Features**: Feature engineering pipeline, XGBoost model predictor, SHAP feature attribution generator, synthetic data provider.
- **Dependencies**: Phase 3.
- **Files/Modules Involved**: `ml/src/data_loader.py`, `ml/src/feature_engineering.py`, `ml/src/model_pipeline.py`, `ml/src/explainer.py`, `backend/app/services/risk_engine.py`.
- **Tests Required**: ML pipeline test (Feature vector input -> Score 0-100% -> SHAP output array).
- **Definition of Done (DoD)**: Risk engine predicts risk scores with SHAP explanations and delivers results through `/flood-risk/explain` endpoint.

### PHASE 8 — Alert Engine & FCM/SMS
- **Goal**: Implement multi-channel alert dispatch pipeline targeting FCM push notifications and SMS gateways.
- **Features**: 4-Tier alert generator (Low/Watch/Prepare/Critical), FCM payload sender, SMS gateway dispatcher.
- **Dependencies**: Phase 5, Phase 7.
- **Files/Modules Involved**: `backend/app/services/notification.py`, `backend/app/api/v1/endpoints/alerts.py`.
- **Tests Required**: Mock FCM push delivery test, mock SMS gateway dispatch test.
- **Definition of Done (DoD)**: Escalating risk score automatically triggers push notification to app user and SMS to configured phone numbers.

### PHASE 9 — Emergency Circle & Quick Actions
- **Goal**: Implement Emergency Circle contact management and 1-tap "I'm Safe" / "Need Help" actions.
- **Features**: CRUD for contacts, custom preference toggles, "I'm Safe" SMS broadcast, "Need Help" distress signal + GPS broadcast.
- **Dependencies**: Phase 5, Phase 8.
- **Files/Modules Involved**: `mobile/lib/features/emergency_circle/`, `backend/app/api/v1/endpoints/emergency_circle.py`.
- **Tests Required**: Quick action API test, SMS payload verification for distress signals.
- **Definition of Done (DoD)**: Tapping "I'm Safe" or "Need Help" dispatches SMS alerts to all Emergency Circle contacts and updates backend status.

### PHASE 10 — Citizen Ground Reporting
- **Goal**: Build photo geotagging, voice note recording, and submission interface for ground flood reporting.
- **Features**: Geotagged photo capture, voice note audio recorder, report submission endpoint, storage upload.
- **Dependencies**: Phase 5.
- **Files/Modules Involved**: `mobile/lib/features/reports/`, `backend/app/api/v1/endpoints/reports.py`.
- **Tests Required**: Multipart image upload test, GPS coordinate verification test.
- **Definition of Done (DoD)**: User submits a photo + GPS report; report is persisted in database and object storage.

### PHASE 11 — Safest Route Navigation Engine
- **Goal**: Develop risk-weighted routing algorithm in PostGIS / OSRM and display recommended safe route on mobile client.
- **Features**: Safe zone spatial lookup, hazard-penalized shortest path calculation, "Safest Available Route" disclaimer UI.
- **Dependencies**: Phase 6, Phase 10.
- **Files/Modules Involved**: `backend/app/services/routing.py`, `backend/app/api/v1/endpoints/routes.py`, `mobile/lib/features/routes/`.
- **Tests Required**: Spatial routing test (Verify flooded road segment is avoided in calculated route).
- **Definition of Done (DoD)**: App displays safest route navigating away from active flood polygons to nearest shelter with explicit disclaimer.

### PHASE 12 — Admin Disaster Dashboard
- **Goal**: Build web dashboard for disaster management authorities to monitor active regional risks and dispatch alerts.
- **Features**: District risk map, active distress pin feed, citizen report triage queue, manual SMS/FCM broadcast trigger.
- **Dependencies**: Phase 3, Phase 8.
- **Files/Modules Involved**: `admin-dashboard/src/`, `backend/app/api/v1/endpoints/admin.py`.
- **Tests Required**: Admin dashboard API authentication test, alert broadcast dispatch test.
- **Definition of Done (DoD)**: Web dashboard renders active village risks, displays live distress pins, and dispatches broadcast alerts.

### PHASE 13 — Offline Support & Local Sync
- **Goal**: Implement client-side offline storage (Hive/SQLite) and auto-sync queue for low-connectivity environments.
- **Features**: Local caching of contacts, last-known risk score, emergency instructions; background report sync queue when back online.
- **Dependencies**: Phase 5, Phase 10.
- **Files/Modules Involved**: `mobile/lib/core/storage/`, `mobile/lib/core/network/sync_queue.dart`.
- **Tests Required**: Offline cache read test, network state change sync test.
- **Definition of Done (DoD)**: Mobile app operates without Internet, showing cached contacts/shelters, and syncs offline reports when reconnected.

### PHASE 14 — Automated Testing & QA Verification
- **Goal**: Execute comprehensive test suite across backend API, spatial routing engine, ML pipeline, and Flutter widgets.
- **Features**: Pytest backend test suite, ML feature calculation checks, Flutter UI widget tests, spatial PostGIS query benchmarks.
- **Dependencies**: Phase 1 through Phase 13.
- **Files/Modules Involved**: `tests/backend/`, `tests/ml/`, `tests/mobile/`.
- **Tests Required**: Full automated test suite execution.
- **Definition of Done (DoD)**: All automated test suites pass cleanly with 0 failures.

### PHASE 15 — SIH Demonstration & Pitch Mode
- **Goal**: Configure synthetic demo data provider, pre-populated demonstration scenarios, and presentation pitch mode.
- **Features**: Demo mode toggle in app, pre-seeded flood escalation scenario for Sangli district, live dynamic re-routing demonstration.
- **Dependencies**: Phase 1 through Phase 14.
- **Files/Modules Involved**: `ml/src/data_loader.py`, `database/init.sql`, `mobile/lib/core/config/demo_config.dart`.
- **Tests Required**: Demo scenario dry-run walkthrough.
- **Definition of Done (DoD)**: System executes a seamless 5-minute end-to-end demonstration flow from alert generation to evacuation routing and distress dispatch.
