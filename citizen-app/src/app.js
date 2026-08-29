import * as api from './api.js';
import { mountNavIcons } from './icons.js';

/* ---------------------------------------------------------------------
   Demo constants — the seeded Demo Citizen's location (matches
   backend/app/core/demo_seed.py DEMO_CITIZEN_LOCATION_ID exactly).
   --------------------------------------------------------------------- */
const DEMO_LAT = 19.078;
const DEMO_LNG = 72.879;

// Route waypoints mirroring the fixed demo road geometry seeded in
// backend/app/core/demo_seed.py (Road A/B/C LINESTRING values). The
// backend remains the source of truth for route STATUS/risk/recommendation
// (fetched live from GET /routes/safest); these coordinates only exist so
// the Map screen has something to draw — they are not independent data.
const ROUTE_WAYPOINTS = {
  'Route A': [[19.078, 72.879], [19.082, 72.882], [19.085, 72.885]],
  'Route B': [[19.078, 72.879], [19.083, 72.884], [19.089, 72.890]],
  'Route C': [[19.078, 72.879], [19.086, 72.883], [19.090, 72.888]],
};
const VILLAGE_CENTROID = [19.080, 72.880];

const RISK_COLOR_VAR = { LOW: '--signal-safe', WATCH: '--signal-watch', PREPARE: '--signal-watch', CRITICAL: '--signal-critical' };
const RISK_NARRATIVE = {
  LOW: 'Conditions are currently normal. Stay informed.',
  WATCH: 'Conditions are being monitored closely.',
  PREPARE: 'Prepare an emergency kit and stay alert.',
  CRITICAL: 'Heavy rainfall and rising water levels detected.',
};
const FACTOR_LABELS = {
  HEAVY_RAINFALL: 'Rainfall',
  RIVER_LEVEL: 'River Level',
  SOIL_SATURATION: 'Soil Moisture',
  LOW_ELEVATION: 'Elevation',
};
const SOURCE_LABELS = { SIMULATED_DEMO_DATA: 'SIMULATED DEMO DATA', OFFICIAL_DATA: 'OFFICIAL DATA', CITIZEN_REPORT: 'CITIZEN REPORT', CITIZEN_ACTION: 'CITIZEN ACTION' };

const POLL_MS = 4000;
const RING_CIRCUMFERENCE = 2 * Math.PI * 52;

/* ---------------------------------------------------------------------
   Central app state
   --------------------------------------------------------------------- */
const state = {
  activeScreen: 'home',
  risk: null,
  alerts: [],
  routes: null,
  whyData: null,
  whyLang: 'en',
  safeZones: [],
  reportHistory: [],
  lastRecommendedRoute: null,
  pollHandle: null,
  map: null,
  mapLayer: null,
  mapInitialized: false,
};

const $ = (sel) => document.querySelector(sel);
const $all = (sel) => Array.from(document.querySelectorAll(sel));

/* ---------------------------------------------------------------------
   Small helpers
   --------------------------------------------------------------------- */
const km = (meters) => `${(meters / 1000).toFixed(1)} km`;
const pct = (n) => `${Math.round(n)}%`;
const sourceLabel = (tag) => SOURCE_LABELS[tag] || tag;

function showToast(message, ms = 3200) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => { toast.hidden = true; }, ms);
}

function setRiskAccent(el, level) {
  const varName = RISK_COLOR_VAR[level] || '--signal-safe';
  el.style.setProperty('--risk-accent', `var(${varName})`);
}

/* ---------------------------------------------------------------------
   ENTRY / LOGIN
   --------------------------------------------------------------------- */
async function handleEnterDemo() {
  const btn = $('#btn-enter-demo');
  const statusEl = $('#entry-status');
  btn.disabled = true;
  btn.textContent = 'Signing in…';
  statusEl.textContent = '';
  try {
    const resp = await api.demoLogin();
    api.setToken(resp.access_token);
    $('#screen-entry').hidden = true;
    $('#app-shell').hidden = false;
    await bootstrapApp();
  } catch (err) {
    statusEl.textContent = err.message || 'Could not sign in to the demo.';
    btn.disabled = false;
    btn.textContent = 'Enter Demo';
  }
}

async function bootstrapApp() {
  navigateTo('home');
  await Promise.all([refreshHomeSafeZone(), pollTick()]);
  if (state.pollHandle) clearInterval(state.pollHandle);
  state.pollHandle = setInterval(pollTick, POLL_MS);
}

/* ---------------------------------------------------------------------
   NAVIGATION
   --------------------------------------------------------------------- */
function navigateTo(name) {
  state.activeScreen = name;
  $all('.screen[data-screen]').forEach((el) => {
    el.classList.toggle('is-visible', el.dataset.screen === name);
  });
  $all('.nav-btn').forEach((btn) => btn.classList.toggle('is-active', btn.dataset.nav === name));

  if (name === 'map') openMapScreen();
  if (name === 'alerts') renderAlertsScreen();
}

/* ---------------------------------------------------------------------
   HOME — risk card, alert banner, safe zone card
   --------------------------------------------------------------------- */
function renderHomeRisk() {
  const loadingEl = $('#risk-loading');
  const bodyEl = $('#risk-body');
  const errorEl = $('#risk-error');
  const card = $('#risk-card');

  if (!state.risk) return;
  loadingEl.hidden = true;
  errorEl.hidden = true;
  bodyEl.hidden = false;

  const { risk_level, risk_score } = state.risk;
  setRiskAccent(card, risk_level);
  card.classList.toggle('is-critical', risk_level === 'CRITICAL');

  $('#risk-percent').textContent = pct(risk_score);
  $('#risk-level-label').textContent = risk_level === 'CRITICAL' ? 'CRITICAL FLOOD RISK' : `${risk_level} FLOOD RISK`;
  $('#risk-narrative').textContent = RISK_NARRATIVE[risk_level] || '—';

  const offset = RING_CIRCUMFERENCE * (1 - Math.min(100, Math.max(0, risk_score)) / 100);
  $('#risk-ring-fill').style.strokeDashoffset = String(offset);
}

function renderHomeRiskError(message) {
  $('#risk-loading').hidden = true;
  $('#risk-body').hidden = true;
  const errorEl = $('#risk-error');
  errorEl.hidden = false;
  errorEl.textContent = message;
}

function renderHomeAlertBanner() {
  const banner = $('#home-alert-banner');
  const badge = $('#nav-alert-badge');
  const critical = state.alerts.find((a) => a.alert_level === 'CRITICAL') || state.alerts[0];
  if (critical) {
    banner.hidden = false;
    $('#home-alert-text').textContent = 'Flood risk near your location has increased.';
    badge.hidden = false;
  } else {
    banner.hidden = true;
    badge.hidden = true;
  }
}

async function refreshHomeSafeZone() {
  try {
    const zones = await api.getNearbySafeZones(DEMO_LAT, DEMO_LNG);
    state.safeZones = zones;
    if (zones.length) {
      $('#home-safezone-name').textContent = zones[0].name;
      $('#home-safezone-distance').textContent = `${km(zones[0].distance_meters)} away`;
    } else {
      $('#home-safezone-name').textContent = 'No safe zone found';
      $('#home-safezone-distance').textContent = '';
    }
  } catch (err) {
    $('#home-safezone-name').textContent = 'Unable to load safe zone';
    $('#home-safezone-distance').textContent = err.message || '';
  }
}

/* ---------------------------------------------------------------------
   WHY SHEET
   --------------------------------------------------------------------- */
async function openWhySheet() {
  $('#why-backdrop').hidden = false;
  const body = $('#why-body');
  body.innerHTML = '<div class="empty-state">Loading risk factors…</div>';
  try {
    state.whyData = await api.getRiskWhy();
    renderWhyBody();
  } catch (err) {
    body.innerHTML = `<div class="empty-state">${err.message || 'Unable to load risk factors.'}</div>`;
  }
}

function renderWhyBody() {
  const body = $('#why-body');
  if (!state.whyData) return;
  const lang = state.whyLang;
  const descKey = `description_${lang}`;

  body.innerHTML = state.whyData.contributing_factors.map((f) => {
    const label = FACTOR_LABELS[f.factor_key] || f.factor_key;
    const valueText = f.value !== null && f.value !== undefined ? `${f.value}${f.unit ? ' ' + f.unit : ''}` : '—';
    const desc = f[descKey] || f.description_en;
    const barWidth = Math.min(100, Math.max(4, f.contribution_percentage * 2));
    return `
      <div class="factor-card">
        <div class="factor-head">
          <span class="factor-name">${label}</span>
          <span class="factor-value">${valueText}</span>
        </div>
        <div class="factor-bar-track"><div class="factor-bar-fill" style="width:${barWidth}%"></div></div>
        <p class="factor-contribution">${f.contribution_percentage}% contribution to overall risk</p>
        <p class="factor-desc">${desc}</p>
      </div>
    `;
  }).join('');
}

/* ---------------------------------------------------------------------
   ALERTS SCREEN
   --------------------------------------------------------------------- */
function renderAlertsScreen() {
  const list = $('#alerts-list');
  if (!state.alerts.length) {
    list.innerHTML = '<div class="empty-state">No active alerts right now.<br>You\'ll be notified here if that changes.</div>';
    return;
  }
  list.innerHTML = state.alerts.map((a) => `
    <div class="card alert-card">
      <p class="alert-card-title">${a.alert_level} FLOOD ALERT</p>
      <div class="alert-card-row"><span>Risk</span><b>${state.risk ? pct(state.risk.risk_score) : '—'}</b></div>
      <div class="alert-card-row"><span>Source</span><b>${sourceLabel(a.source_tag)}</b></div>
      <p class="alert-card-msg">${a.message_en}</p>
      <div class="alert-card-actions">
        <button class="btn btn-outline btn-small" data-action="view-risk">View Risk</button>
        <button class="btn btn-primary btn-small" data-action="find-route">Find Safe Route</button>
      </div>
    </div>
  `).join('');

  list.querySelectorAll('[data-action="view-risk"]').forEach((btn) => btn.addEventListener('click', () => { navigateTo('home'); openWhySheet(); }));
  list.querySelectorAll('[data-action="find-route"]').forEach((btn) => btn.addEventListener('click', openRoutesSheet));
}

/* ---------------------------------------------------------------------
   ROUTES SHEET
   --------------------------------------------------------------------- */
async function openRoutesSheet() {
  $('#routes-backdrop').hidden = false;
  await refreshRoutes(true);
}

async function refreshRoutes(forceRenderEvenIfClosed) {
  try {
    state.routes = await api.getSafestRoutes();
  } catch (err) {
    if (!$('#routes-backdrop').hidden) {
      $('#routes-body').innerHTML = `<div class="empty-state">${err.message}</div>`;
    }
    return;
  }
  const sheetOpen = !$('#routes-backdrop').hidden;
  if (sheetOpen || forceRenderEvenIfClosed) renderRoutesBody();
}

function renderRoutesBody() {
  const body = $('#routes-body');
  const routes = state.routes.routes;
  const recommended = routes.find((r) => r.recommended);
  const changed = state.lastRecommendedRoute && recommended && state.lastRecommendedRoute !== recommended.route_name;

  body.innerHTML = routes.map((r) => {
    const blocked = r.road_status === 'BLOCKED' || r.road_status === 'SUBMERGED';
    const flash = changed && r.recommended ? 'just-changed' : '';
    return `
      <div class="route-card ${r.recommended ? 'is-recommended' : ''} ${blocked ? 'is-blocked' : ''} ${flash}">
        <div class="route-head">
          <span class="route-name">${r.route_name}</span>
          ${r.recommended ? '<span class="route-recommended-badge">RECOMMENDED</span>' : ''}
        </div>
        <div class="route-meta">
          <span><b>${km(r.distance_meters)}</b></span>
          <span><b>${r.estimated_time_minutes} min</b> on foot</span>
        </div>
        <span class="route-status-pill risk-${r.risk_level}">${r.risk_level} RISK · ${r.road_status}</span>
        ${!r.recommended && blocked ? '<p class="route-not-recommended">Not recommended — road currently blocked.</p>' : ''}
        ${!r.recommended && !blocked ? '<p class="route-not-recommended">Not recommended right now.</p>' : ''}
      </div>
    `;
  }).join('');

  if (changed) {
    showToast(`Route updated — ${recommended.route_name} is now recommended.`);
  }
  if (recommended) state.lastRecommendedRoute = recommended.route_name;
}

/* ---------------------------------------------------------------------
   MAP SCREEN (Leaflet + OpenStreetMap — no Mapbox token required)
   --------------------------------------------------------------------- */
function openMapScreen() {
  const loadingEl = $('#map-loading');
  if (!state.mapInitialized) {
    state.map = L.map('leaflet-map', { zoomControl: true }).setView([DEMO_LAT, DEMO_LNG], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(state.map);
    state.mapLayer = L.layerGroup().addTo(state.map);
    state.mapInitialized = true;
  }
  setTimeout(() => state.map.invalidateSize(), 50);
  loadingEl.hidden = true;
  redrawMap();
}

async function redrawMap() {
  if (!state.mapInitialized) return;
  state.mapLayer.clearLayers();

  // Citizen location.
  L.circleMarker([DEMO_LAT, DEMO_LNG], { radius: 8, color: '#1B6FA8', fillColor: '#1B6FA8', fillOpacity: 0.9, weight: 2 })
    .bindPopup('You are here (demo citizen location)')
    .addTo(state.mapLayer);

  // Safe zones (fetched live — never hardcoded).
  try {
    const zones = state.safeZones.length ? state.safeZones : await api.getNearbySafeZones(DEMO_LAT, DEMO_LNG);
    state.safeZones = zones;
    zones.forEach((z) => {
      if (z.latitude == null || z.longitude == null) return;
      L.circleMarker([z.latitude, z.longitude], { radius: 9, color: '#1E8E5A', fillColor: '#1E8E5A', fillOpacity: 0.85, weight: 2 })
        .bindPopup(`<b>${z.name}</b><br>${km(z.distance_meters)} away · capacity ${z.capacity}<br>${z.is_verified ? 'Verified' : 'Unverified'} · ${sourceLabel(z.source_tag)}`)
        .addTo(state.mapLayer);
    });
  } catch (_) { /* non-fatal for the map view */ }

  // Routes — drawn using fixed demo waypoints, coloured by live route status.
  if (state.routes) {
    state.routes.routes.forEach((r) => {
      const key = Object.keys(ROUTE_WAYPOINTS).find((k) => r.route_name.startsWith(k));
      const waypoints = key && ROUTE_WAYPOINTS[key];
      if (!waypoints) return;
      const blocked = r.road_status === 'BLOCKED' || r.road_status === 'SUBMERGED';
      const color = r.recommended ? '#1E8E5A' : (blocked ? '#D64545' : '#D98A1E');
      L.polyline(waypoints, {
        color,
        weight: r.recommended ? 5 : 3,
        opacity: blocked ? 0.55 : 0.85,
        dashArray: blocked ? '6 6' : null,
      }).bindPopup(`${r.route_name} — ${r.road_status}${r.recommended ? ' (recommended)' : ''}`).addTo(state.mapLayer);
    });
  }

  // Approximate flood-affected area overlay — a frontend-only visual cue
  // derived from the current (backend-sourced) risk level, not a real
  // hydrological boundary.
  if (state.risk && (state.risk.risk_level === 'CRITICAL' || state.risk.risk_level === 'PREPARE')) {
    L.circle(VILLAGE_CENTROID, {
      radius: 650,
      color: '#D64545',
      weight: 1,
      fillColor: '#D64545',
      fillOpacity: 0.12,
    }).bindPopup('Simulated flood-affected area (approximate, demo only)').addTo(state.mapLayer);
  }
}

/* ---------------------------------------------------------------------
   EMERGENCY CIRCLE ACTIONS
   --------------------------------------------------------------------- */
async function handleImSafe(resultEl) {
  try {
    await api.postImSafe({ latitude: DEMO_LAT, longitude: DEMO_LNG, custom_message: 'Marked safe from JalRaksha demo app.' });
    const msg = "I'm Safe: Safety status recorded.";
    showToast(msg);
    if (resultEl) { resultEl.hidden = false; resultEl.classList.remove('is-error'); resultEl.textContent = msg; }
  } catch (err) {
    const msg = err.message || 'Could not record your status.';
    showToast(msg);
    if (resultEl) { resultEl.hidden = false; resultEl.classList.add('is-error'); resultEl.textContent = msg; }
  }
}

async function handleNeedHelp(resultEl) {
  try {
    await api.postNeedHelp({ latitude: DEMO_LAT, longitude: DEMO_LNG, distress_type: 'TRAPPED_WATER' });
    const msg = 'Need Help: Emergency request recorded.';
    showToast(msg);
    if (resultEl) { resultEl.hidden = false; resultEl.classList.remove('is-error'); resultEl.textContent = msg; }
  } catch (err) {
    const msg = err.message || 'Could not send your request.';
    showToast(msg);
    if (resultEl) { resultEl.hidden = false; resultEl.classList.add('is-error'); resultEl.textContent = msg; }
  }
}

/* ---------------------------------------------------------------------
   REPORT FORM
   --------------------------------------------------------------------- */
function renderReportHistory() {
  const container = $('#report-history');
  if (!state.reportHistory.length) { container.innerHTML = ''; return; }
  container.innerHTML = state.reportHistory.map((r) => `
    <div class="card">
      <div class="rh-head">
        <span class="rh-cat">${r.disaster_category.replaceAll('_', ' ')}</span>
        <span class="tag tag-citizen">CITIZEN REPORT</span>
      </div>
      <p class="rh-desc">${r.description || 'No description provided.'}</p>
      <p class="rh-meta">${r.verification_status} · ${new Date(r.created_at).toLocaleTimeString()}</p>
    </div>
  `).join('');
}

async function handleReportSubmit(evt) {
  evt.preventDefault();
  const btn = $('#btn-submit-report');
  const resultEl = $('#report-result');
  btn.disabled = true;
  btn.textContent = 'Submitting…';
  try {
    const payload = {
      disaster_category: $('#report-category').value,
      description: $('#report-description').value || null,
      latitude: parseFloat($('#report-lat').value),
      longitude: parseFloat($('#report-lng').value),
    };
    const report = await api.submitReport(payload);
    state.reportHistory.unshift(report);
    renderReportHistory();
    resultEl.hidden = false;
    resultEl.classList.remove('is-error');
    resultEl.textContent = 'Report submitted for verification.';
    $('#report-description').value = '';
  } catch (err) {
    resultEl.hidden = false;
    resultEl.classList.add('is-error');
    resultEl.textContent = err.message || 'Unable to connect to JalRaksha demo server.';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit Report';
  }
}

function handleUseLocation() {
  if (!navigator.geolocation) { showToast('Location not available in this browser.'); return; }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      $('#report-lat').value = pos.coords.latitude.toFixed(4);
      $('#report-lng').value = pos.coords.longitude.toFixed(4);
    },
    () => showToast('Could not get your location — using demo default.'),
  );
}

/* ---------------------------------------------------------------------
   POLLING — /flood-risk/current, /alerts, /routes/safest
   --------------------------------------------------------------------- */
let pollTickSeq = 0;

async function pollTick() {
  const tickId = ++pollTickSeq;
  try {
    const [risk, alerts, routes] = await Promise.all([
      api.getCurrentRisk(),
      api.getAlerts(),
      api.getSafestRoutes(),
    ]);

    // Guard against overlapping ticks resolving out of order (e.g. a slow
    // earlier request completing after a faster later one): only the most
    // recently *started* tick is allowed to write state.
    if (tickId !== pollTickSeq) return;

    state.risk = risk;
    state.alerts = alerts;
    state.routes = routes;

    renderHomeRisk();
    renderHomeAlertBanner();
    if (state.activeScreen === 'alerts') renderAlertsScreen();
    if (!$('#routes-backdrop').hidden) renderRoutesBody();
    else if (state.routes) {
      const rec = state.routes.routes.find((r) => r.recommended);
      if (rec) state.lastRecommendedRoute = rec.route_name;
    }
    if (state.activeScreen === 'map') redrawMap();
  } catch (err) {
    if (tickId !== pollTickSeq) return;
    renderHomeRiskError(err.message || 'Unable to connect to JalRaksha demo server.');
  }
}

/* ---------------------------------------------------------------------
   WIRING
   --------------------------------------------------------------------- */
function wireEvents() {
  $('#btn-enter-demo').addEventListener('click', handleEnterDemo);
  $('#btn-refresh').addEventListener('click', () => { showToast('Refreshing…'); pollTick(); });

  $all('.nav-btn').forEach((btn) => btn.addEventListener('click', () => navigateTo(btn.dataset.nav)));

  $('#btn-why').addEventListener('click', openWhySheet);
  $('#btn-close-why').addEventListener('click', () => { $('#why-backdrop').hidden = true; });
  $('#why-backdrop').addEventListener('click', (e) => { if (e.target.id === 'why-backdrop') $('#why-backdrop').hidden = true; });
  $all('.lang-btn').forEach((btn) => btn.addEventListener('click', () => {
    state.whyLang = btn.dataset.lang;
    $all('.lang-btn').forEach((b) => b.classList.toggle('is-active', b === btn));
    renderWhyBody();
  }));

  $('#btn-close-routes').addEventListener('click', () => { $('#routes-backdrop').hidden = true; });
  $('#routes-backdrop').addEventListener('click', (e) => { if (e.target.id === 'routes-backdrop') $('#routes-backdrop').hidden = true; });

  $('#btn-view-alert').addEventListener('click', () => navigateTo('alerts'));
  $('#btn-view-map').addEventListener('click', () => navigateTo('map'));
  $('#btn-report-flood').addEventListener('click', () => navigateTo('report'));

  $('#btn-im-safe').addEventListener('click', () => handleImSafe(null));
  $('#btn-need-help').addEventListener('click', () => handleNeedHelp(null));
  $('#btn-im-safe-2').addEventListener('click', () => handleImSafe($('#emergency-result')));
  $('#btn-need-help-2').addEventListener('click', () => handleNeedHelp($('#emergency-result')));

  $('#report-form').addEventListener('submit', handleReportSubmit);
  $('#btn-use-location').addEventListener('click', handleUseLocation);

  // A "Safest Route" quick-access from the map screen's legend area.
  const legend = $('.map-legend');
  const routeBtn = document.createElement('button');
  routeBtn.className = 'btn btn-outline btn-small';
  routeBtn.textContent = 'Safest Route';
  routeBtn.style.marginTop = '10px';
  routeBtn.addEventListener('click', openRoutesSheet);
  legend.insertAdjacentElement('afterend', routeBtn);
}

/* ---------------------------------------------------------------------
   BOOT
   --------------------------------------------------------------------- */
function prefillReportLocation() {
  $('#report-lat').value = DEMO_LAT;
  $('#report-lng').value = DEMO_LNG;
}

(function init() {
  mountNavIcons(document);
  wireEvents();
  prefillReportLocation();

  // If a demo token already exists (page refresh mid-demo), skip straight
  // to the dashboard instead of forcing another login tap.
  const existingToken = localStorage.getItem('jalraksha_demo_token');
  if (existingToken) {
    api.getMe().then(() => {
      $('#screen-entry').hidden = true;
      $('#app-shell').hidden = false;
      bootstrapApp();
    }).catch(() => api.clearToken());
  }
})();
