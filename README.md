# JalRaksha — The Flood Relief, Reminder & Safety Expert

> **Know the Risk. Understand the Impact. Find Safety. Take Action.**

JalRaksha is an AI-powered flood safety, relief, and emergency-response platform designed to provide citizens and disaster management authorities with localized, understandable, and actionable intelligence before and during flood situations.

---

## 🏗️ Architecture & Documentation

Comprehensive architectural design and specifications are available in the `docs/` directory:

- 📘 [JALRAKSHA_SPEC.md](file:///w:/JalRaksha/docs/JALRAKSHA_SPEC.md) — Product Specification
- 📊 [PROJECT_ANALYSIS.md](file:///w:/JalRaksha/docs/PROJECT_ANALYSIS.md) — Comprehensive System Analysis
- 📐 [ARCHITECTURE.md](file:///w:/JalRaksha/docs/ARCHITECTURE.md) — Technical System Architecture & MVP Flow
- 🗄️ [DATABASE.md](file:///w:/JalRaksha/docs/DATABASE.md) — PostgreSQL + PostGIS Spatial Schema
- 🔌 [API_SPEC.md](file:///w:/JalRaksha/docs/API_SPEC.md) — REST API Specifications
- 🤖 [ML_ARCHITECTURE.md](file:///w:/JalRaksha/docs/ML_ARCHITECTURE.md) — XGBoost & SHAP Risk Engine Pipeline
- 🗺️ [PROJECT_STRUCTURE.md](file:///w:/JalRaksha/docs/PROJECT_STRUCTURE.md) — Monorepo Directory Map
- 🛣️ [DEVELOPMENT_ROADMAP.md](file:///w:/JalRaksha/docs/DEVELOPMENT_ROADMAP.md) — 15-Phase Development Plan

---

## 💻 Tech Stack Overview

- **Mobile Client**: Flutter (Android & iOS)
- **Backend Service**: FastAPI (Python 3.11+)
- **Spatial Database**: PostgreSQL 15+ with PostGIS 3+
- **AI / ML Engine**: Python, Scikit-learn, XGBoost, SHAP
- **Maps & Routing**: Mapbox, OpenStreetMap, PostGIS spatial algorithms
- **Notifications**: Firebase Cloud Messaging (FCM) & SMS Gateway API
- **Caching**: Redis
- **Orchestration**: Docker & Docker Compose

---

## 🚀 Quick Start (Development Setup)

1. **Clone & Configure Environment**:
   ```bash
   cp .env.example .env
   ```

2. **Launch Container Services**:
   ```bash
   docker-compose up -d --build
   ```

3. **Verify API Gateway**:
   Navigate to `http://localhost:8000/docs` to view interactive OpenAPI docs.
