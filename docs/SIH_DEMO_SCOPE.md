# JalRaksha — SIH Demonstration Scope

> This document supersedes the production-scale ambitions described in
> `PROJECT_ANALYSIS.md`, `ARCHITECTURE.md`, and `DEVELOPMENT_ROADMAP.md` **for the
> purpose of the SIH demo build only**. Those documents remain valid as the
> long-term product vision. Nothing here deletes or replaces existing
> architecture — it defines a minimal, reliable runtime path through the
> existing codebase for live demonstration.

---

## 1. Purpose of the Prototype

JalRaksha's SIH prototype exists to **prove the end-to-end concept** — trusted
data → AI risk score → transparent explanation → safe zone → safest route →
citizen action → community feedback → admin response — as a single, reliable,
repeatable demo. It is not a production disaster-management system and does
not claim to be one.

Goals:
- Demonstrate the complete user + admin journey without any live-demo failure
  points (no Docker boot races, no external API keys, no network dependency).
- Reuse the existing backend design (models, schemas, services) rather than
  rebuilding it.
- Make every piece of simulated/AI data visually unmistakable from real
  official data, per the project's own Safety/Data Distinction Protocol.

Non-goals: production security, real notification delivery, real routing
engines, offline support, multilingual completeness, scale, or hardening.

---

## 2. Demo Architecture

```
┌─────────────────────┐        ┌──────────────────────┐
│  Citizen Web Client   │◄─────►│                        │
│  (browser, phone-frame│  REST │                        │
│  styled HTML/JS)       │ + WS  │   FastAPI Backend      │
└─────────────────────┘        │   (existing app/)      │
                                 │   + new /demo endpoints│
┌─────────────────────┐        │                        │
│  Admin Dashboard      │◄─────►│                        │
│  (existing            │  REST │                        │
│  admin-dashboard/src) │        └──────────┬─────────────┘
└─────────────────────┘                    │
                                             │ SQLAlchemy ORM
                                             ▼
                                    ┌──────────────────┐
                                    │  SQLite (file)     │
                                    │  demo_jalraksha.db │
                                    │  seeded on boot     │
                                    └──────────────────┘
```

- **Backend**: existing FastAPI app (`backend/app/`), existing models,
  schemas, `risk_service.py`, `spatial_queries.py`, `notification_service.py`.
  A small set of new endpoints (Section 9) is added; nothing existing is
  removed.
- **Database**: SQLite file, created via `Base.metadata.create_all()` and
  seeded from the existing `database/seed_data.py` logic (adapted to run
  against SQLite instead of requiring a live Postgres/PostGIS server). This
  path is already proven working in `tests/database/test_spatial_schema.py`.
- **Spatial queries**: `spatial_queries.py`'s existing SQLite/non-PostGIS
  fallback path is used as the primary path for the demo, not an edge case.
- **Maps**: Leaflet + OpenStreetMap tiles (no API key required) on both
  citizen client and admin dashboard.
- **Routing**: no real routing engine. A small set of predefined named routes
  (seeded demo data) between the citizen location and the seeded safe zone,
  selected by simple logic that checks `RoadCondition.status` on the roads
  each route uses.
- **Notifications**: `notification_service.py`'s existing mock provider,
  displayed live in the citizen client via polling or a WebSocket, and logged
  in the admin dashboard. No SMS/FCM/Firebase calls are made.
- **Auth**: minimal demo login (phone number only, no OTP) issuing a JWT via
  the existing `security.py` utilities — enough to distinguish citizen
  sessions, not a real identity system.
- **ML**: existing heuristic scaffolding in `ml/src/` (data provider, feature
  engine, model pipeline, explainer) is used as-is to produce the risk score
  and "Why?" factors; no retraining or new model work.

---

## 3. Citizen Features (browser client)

1. **Risk dashboard** — current flood risk score, alert level (LOW / WATCH /
   PREPARE / CRITICAL), village name, clearly tagged as `AI_PREDICTION` or
   `SIMULATED_DEMO_DATA`.
2. **Simulated alert banner** — appears live when the admin triggers a flood
   or escalates risk, without a page reload.
3. **"Why am I at risk?"** — modal showing the contributing risk factors
   (rainfall, river level, soil saturation, elevation) from
   `risk_service.get_risk_why_explanation`.
4. **Map view (Leaflet/OSM)** — citizen location, nearest safe zone, and the
   currently recommended safest route.
5. **Safest available route** — labeled "Safest Available Route based on
   currently available data," never "100% safe." Updates live when the admin
   blocks a road.
6. **Quick actions** — "I'm Safe" and "Need Help" one-tap buttons; both
   produce a mock notification/event visible on the admin dashboard.
7. **Citizen flood report** — simple form (description, category, GPS
   coordinates, optional photo URL) submitted to the backend.

---

## 4. Admin Features (existing admin-dashboard, wired to live data)

1. **Overview cards** — active alert level, affected villages, population
   exposed, unverified report count — pulled from live backend state instead
   of the current hardcoded values.
2. **"Simulate Flood" control** — triggers a flood escalation event affecting
   the seeded village/risk record.
3. **"Block Road" control** — flips a seeded road segment's `RoadCondition`
   to `BLOCKED`/`SUBMERGED`, which live-changes the citizen's safest route.
4. **Live distress/status feed** — incoming "I'm Safe" / "Need Help" events
   with citizen name and coordinates.
5. **Citizen report queue** — list of submitted reports with an admin
   "Verify" action that updates `verification_status`.
6. **Map overview (Leaflet/OSM)** — village, safe zones, and road conditions
   at a glance.

---

## 5. Demo Data Strategy

- All demo content is centered on the existing seeded **Sangli Rural**
  village and its infrastructure, safe zones, and roads (see
  `database/seed_data.py`).
- A fixed **demo citizen account** and a fixed **demo admin account** are
  seeded so the walkthrough requires no signup during the live demo.
- 2–3 named routes between the citizen's seeded location and the seeded
  safe zone are added as demo data, each composed of existing/seeded road
  segments, so that blocking a road visibly changes the recommended route.
- The database is recreated and reseeded on each backend startup so every
  demo run starts from a known, clean state.
- Every seeded record keeps the project's existing `source_tag` values
  (`OFFICIAL_DATA`, `AI_PREDICTION`, `CITIZEN_REPORT`, `SIMULATED_DEMO_DATA`)
  already present in the schema — no new tagging scheme is introduced.

---

## 6. Safety / Data Labeling Rules

Carried forward unchanged from `ARCHITECTURE.md` Section 4–5, enforced in the
demo UI:

- Every risk score, alert, route, and pre-seeded scenario value is visibly
  tagged **"DEMO"** or **"SIMULATED DATA"** in both the citizen client and
  admin dashboard — not just in an API field, but as a visible on-screen
  badge/banner.
- AI-generated risk predictions are **never** displayed as an official
  government warning. Any risk/alert card includes the existing disclaimer:
  *"AI prediction; not an official government warning."*
- Routes are always labeled **"Safest Available Route based on currently
  available data"** — never "100% safe" or "guaranteed safe."
- Citizen reports are labeled **"Citizen Report (Unverified)"** until an
  admin marks them verified, at which point the label updates accordingly.

---

## 7. Complete Demo Flow

1. Admin opens the dashboard and sees the current (LOW/WATCH) situation.
2. Admin clicks **"Simulate Flood"**.
3. Backend escalates the seeded flood risk record and issues a demo alert.
4. Citizen's browser client receives the simulated alert live (poll/WS) and
   the risk card updates to CRITICAL, clearly marked as simulated.
5. Citizen opens **"Why am I at risk?"** and sees the contributing factors.
6. Citizen opens the map and sees their location and the nearest safe zone.
7. Citizen sees the **safest available route** to that safe zone.
8. Admin clicks **"Block Road"** on the segment the current route uses.
9. Citizen's route recommendation updates live to an alternate route.
10. Citizen taps **"I'm Safe"** or **"Need Help."**
11. The resulting event appears immediately in the admin's live feed.
12. Citizen submits a **flood report** (description + category + location).
13. Admin sees the new report in the report queue.
14. Admin marks the report **Verified**, and its label updates in real time.

---

## 8. Features Intentionally Excluded From the Demo Build

- PostgreSQL / PostGIS, Docker, Redis — SQLite + in-process FastAPI only.
- Mapbox — Leaflet + OpenStreetMap tiles only.
- Firebase Auth / FCM, real SMS gateway — mock notification records only.
- Real OTP / production authentication — phone-number-only demo login.
- Real OSRM / pgRouting routing engine — predefined demo routes with simple
  road-status-based selection logic.
- Voice-note recording, STT/NLP processing.
- Real satellite/IoT/hydrological data feeds — synthetic data provider only.
- Offline support / local sync queue.
- Full multilingual UI (existing EN/MR/HI strings in risk factors are kept
  where already present; full i18n coverage is not a demo requirement).
- The Flutter mobile app is **left untouched as future implementation** —
  the demo uses a browser-based citizen client instead.

---

## 9. Implementation Phases

**Phase A — Backend runtime simplification**
Switch `DATABASE_URL` to a SQLite file for demo runtime, seed on startup
using existing seed logic, verify existing services run unchanged against it.

**Phase B — New minimal endpoints**
Add only the endpoints needed for the flow above: demo login, current risk,
"why" explanation, nearest safe zone, safest route (demo logic), admin
simulate-flood, admin block-road, I'm-Safe/Need-Help, citizen reports
(create + list + verify), admin overview/live feed. No existing endpoint or
service is changed in a breaking way.

**Phase C — Citizen web client**
Phone-frame styled HTML/JS page implementing Section 3 features against the
new endpoints, with Leaflet map integration.

**Phase D — Admin dashboard wiring**
Replace the existing dashboard's hardcoded values and static map placeholder
with live calls to the new/admin endpoints and a Leaflet map.

**Phase E — Data labeling pass**
Add visible DEMO/SIMULATED badges and disclaimers across both clients per
Section 6.

**Phase F — Full walkthrough rehearsal**
Run the complete Section 7 flow start to finish multiple times to confirm
reliability before the live presentation.
