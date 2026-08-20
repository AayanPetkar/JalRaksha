# Project Structure — JalRaksha Monorepo

## 1. Directory Tree Overview

```
JalRaksha/
├── mobile/                  # Flutter Cross-Platform Application (Android / iOS)
│   ├── lib/
│   │   ├── main.dart        # Mobile entry point
│   │   ├── core/            # App theme, network client, constants, local storage
│   │   └── features/        # Feature modules (auth, flood_risk, alerts, safe_zones, routes, emergency_circle, reports)
│   └── pubspec.yaml         # Flutter dependencies
│
├── backend/                 # FastAPI Asynchronous Service (Python 3.11+)
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── core/            # Config, security, DB session, FCM/SMS clients
│   │   ├── api/v1/          # REST API endpoints & routers
│   │   ├── models/          # SQLAlchemy / GeoAlchemy2 DB models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── services/        # Risk calculation, spatial routing, notification services
│   ├── Dockerfile           # Backend container build script
│   └── requirements.txt     # Python backend dependencies
│
├── ml/                      # AI/ML Flood Risk & Explainability Engine
│   ├── src/
│   │   ├── data_loader.py         # Data provider abstractions (Synthetic vs Real)
│   │   ├── feature_engineering.py # Feature extraction pipeline
│   │   ├── model_pipeline.py      # XGBoost risk model definition
│   │   └── explainer.py           # SHAP explainability generator
│   ├── models/                    # Saved trained model artifacts (.pkl / .json)
│   ├── notebooks/                 # EDA & experimentation Jupyter notebooks
│   ├── Dockerfile                 # ML service container build script
│   └── requirements.txt           # ML dependencies (Pandas, XGBoost, SHAP)
│
├── admin-dashboard/         # Disaster Management Web Dashboard
│   ├── src/
│   │   ├── index.html       # Single-page web dashboard HTML
│   │   ├── app.js           # Dashboard JavaScript logic (Maps, Risk feeds, Alert dispatch)
│   │   └── styles.css       # Clean dashboard styling
│   ├── package.json         # Node manifest
│   └── Dockerfile           # Dashboard web server container
│
├── database/                # PostgreSQL + PostGIS Schemas & Migrations
│   ├── init.sql             # Extensions enabling & baseline DDL script
│   ├── alembic.ini          # DB Migration configuration
│   └── Dockerfile           # PostGIS customized container setup
│
├── docs/                    # Architectural & Project Specifications
│   ├── JALRAKSHA_SPEC.md    # Original product specification
│   ├── PROJECT_ANALYSIS.md  # Comprehensive project analysis
│   ├── ARCHITECTURE.md      # Technical architecture & MVP flow
│   ├── DATABASE.md          # Database schema & spatial definitions
│   ├── API_SPEC.md          # REST API specification
│   ├── ML_ARCHITECTURE.md   # AI/ML pipeline & XAI architecture
│   ├── PROJECT_STRUCTURE.md # Monorepo directory map (This file)
│   └── DEVELOPMENT_ROADMAP.md # 15-phase execution plan
│
├── infrastructure/          # Container & Server Infrastructure
│   ├── docker-compose.yml   # Multi-container orchestration (Backend, DB, Redis, Admin)
│   ├── docker-compose.dev.yml # Local development configuration
│   └── nginx.conf           # Gateway reverse proxy configuration
│
└── tests/                   # Cross-Module Test Suites
    ├── backend/             # Pytest backend integration & unit tests
    ├── ml/                  # ML pipeline verification tests
    └── mobile/              # Flutter widget & unit tests
```

---

## 2. Monorepo Principles & Modular Boundaries

1. **Independent Development**: Each sub-folder (`mobile`, `backend`, `ml`, `admin-dashboard`) contains its own dependencies and configuration files.
2. **API Contract Enforcement**: Communication between frontend clients (Mobile & Admin) and backend services happens exclusively over documented HTTP/REST contracts (`docs/API_SPEC.md`).
3. **No Direct Database Access from Mobile/Admin**: Mobile and Web clients NEVER connect directly to PostgreSQL. All spatial and data access is mediated by FastAPI.
4. **Environment Isolation**: `.env.example` at the root defines environment variables for docker orchestration, while sub-components read their relevant parameters via environment configuration modules.
