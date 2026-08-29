# JalRaksha — Citizen Demo App (Phase C)

A plain HTML/CSS/JS browser client for the SIH demonstration. No build step,
no framework — just static files served locally, talking to the Phase B
FastAPI backend over its existing REST API.

## Run it

**1. Start the backend** (from the repo root, in a separate terminal):

```bash
cd backend
uvicorn app.main:app --reload
```

This starts the API on `http://localhost:8000` in `DEMO_MODE`, auto-creating
and seeding the SQLite demo database (see Phase A/B). CORS is already open
(`allow_origins=["*"]`) so no backend changes were needed for the browser
client to reach it.

**2. Start the citizen app** (from the repo root, in another terminal):

```bash
cd citizen-app
python3 -m http.server 5500
```

**3. Open** `http://localhost:5500` in a browser.

If your backend runs somewhere other than `http://localhost:8000`, open the
app with `?api=` pointing at it, e.g.
`http://localhost:5500/?api=http://localhost:9000/api/v1`.

## What it does

- **Entry screen** — "Enter Demo" calls `POST /demo/login` (no OTP/password)
  and stores the JWT in `localStorage` so a page refresh mid-demo doesn't
  force another login.
- **Home** — live risk ring + level from `GET /flood-risk/current`, an alert
  banner when an alert is active, nearest safe zone from
  `GET /safe-zones/nearby`, and the I'm Safe / Need Help / Report Flood
  actions.
- **Why am I at risk?** — bottom sheet backed by `GET /flood-risk/current/why`,
  with an EN/HI/MR language toggle over the same fetched data.
- **Map** — Leaflet + OpenStreetMap (no Mapbox token). Citizen location and
  safe zones are plotted from live API data; the three demo routes are drawn
  using fixed waypoints that mirror the backend's seeded road geometry, but
  route colour/status/"recommended" always comes from live
  `GET /routes/safest` data, never hardcoded.
- **Alerts** — `GET /alerts`, with "View Risk" and "Find Safe Route" actions.
- **Routes** — `GET /routes/safest`; the recommended card is visually
  highlighted, and flashes + toasts when the recommendation changes (e.g.
  after an admin blocks a road).
- **Emergency** — demo emergency contacts (hardcoded, clearly labeled `DEMO
  CONTACT` — there's no contacts-list endpoint in Phase B) plus I'm Safe /
  Need Help, calling the real endpoints and showing only the exact demo
  wording ("Emergency request recorded.") — never claims a rescue was
  dispatched.
- **Report** — submits to `POST /reports`, shows "Report submitted for
  verification.", and lists session reports tagged `CITIZEN REPORT`.

## State sync

Once logged in, the app polls `GET /flood-risk/current`, `GET /alerts`, and
`GET /routes/safest` every 4 seconds. All state changes (LOW → CRITICAL, a
route becoming blocked, a new alert) are driven entirely by these polls —
nothing is simulated client-side. The backend is always the source of truth.

## Demo/data labeling

`DEMO MODE` is shown in the top status bar at all times. Simulated data is
tagged `SIMULATED DEMO DATA`, AI-derived explanations are tagged
`AI-ASSISTED DEMO`, and citizen-submitted content is tagged `CITIZEN REPORT`
— matching the source tags the backend already returns. The safest-route
disclaimer always reads *"Safest Available Route based on currently
available data"* and the app never states or implies "100% safe".
