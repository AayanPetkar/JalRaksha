/* ================================================================
   JalRaksha — Admin Dashboard Application (Phase D)
   ================================================================
   Connects to the existing Phase B FastAPI backend.
   No backend modifications required — all endpoints already exist.
   ================================================================ */

(function () {
  'use strict';

  // ── API Configuration ──────────────────────────────────────────
  const params = new URLSearchParams(window.location.search);
const API_BASE = params.get('api') || 'https://jalraksha-backend.onrender.com/api/v1';

  // ── Polling ────────────────────────────────────────────────────
  const POLL_INTERVAL_MS = 4000;
  let pollTimer = null;
  let isOnline = true;

  // ── Map ────────────────────────────────────────────────────────
  let map = null;
  let mapMarkers = [];
  const CITIZEN_COORDS = [19.078, 72.879]; // Demo citizen seeded location

  // ── State ──────────────────────────────────────────────────────
  let lastRiskLevel = null;

  // ================================================================
  //  API LAYER
  // ================================================================

  class ApiError extends Error {
    constructor(message, status) {
      super(message);
      this.status = status;
    }
  }

  async function api(path, { method = 'GET', body } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
    } catch (networkErr) {
      throw new ApiError('Unable to connect to JalRaksha demo server.', 0);
    }

    if (!response.ok) {
      let detail = `Request failed (${response.status})`;
      try {
        const data = await response.json();
        if (data && typeof data.detail === 'string') detail = data.detail;
      } catch (_) { /* non-JSON body */ }
      throw new ApiError(detail, response.status);
    }

    if (response.status === 204) return null;
    return response.json();
  }

  // API calls
  const getCurrentRisk = () => api('/flood-risk/current');
  const getAdminOverview = () => api('/admin/overview');
  const getAlerts = () => api('/alerts');
  const getDistressSignals = () => api('/admin/distress-signals');
  const getReports = () => api('/admin/reports');
  const getSafeZones = () => api('/safe-zones/nearby?latitude=19.078&longitude=72.879');
  const getRoutes = () => api('/routes/safest');

  const simulateFlood = () => api('/admin/simulate-flood', { method: 'POST' });
  const simulateNormal = () => api('/admin/simulate-normal', { method: 'POST' });
  const simulateBlockedRoad = () => api('/admin/simulate-blocked-road', { method: 'POST' });
  const verifyReport = (id) => api(`/admin/reports/${id}/verify`, { method: 'POST' });

  // ================================================================
  //  DOM HELPERS
  // ================================================================

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ================================================================
  //  TOAST SYSTEM
  // ================================================================

  function showToast(message, type = 'success') {
    const container = $('#toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('toast-out');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ================================================================
  //  CONNECTION STATUS
  // ================================================================

  function setConnectionStatus(online) {
    isOnline = online;
    const dot = $('#connection-dot');
    const text = $('#connection-text');
    const banner = $('#error-banner');

    if (online) {
      dot.classList.remove('offline');
      text.textContent = 'Connected';
      banner.classList.remove('visible');
    } else {
      dot.classList.add('offline');
      text.textContent = 'Offline';
      banner.classList.add('visible');
    }
  }

  // ================================================================
  //  RISK LEVEL COLORS
  // ================================================================

  function riskColor(level) {
    switch (level) {
      case 'CRITICAL': return 'var(--color-critical)';
      case 'PREPARE': return 'var(--color-prepare)';
      case 'WATCH': return 'var(--color-watch)';
      default: return 'var(--color-low)';
    }
  }

  function roadStatusTag(status) {
    const cls = {
      'OPEN': 'tag-open',
      'WATCH': 'tag-demo',
      'HIGH_RISK': 'tag-high-risk',
      'BLOCKED': 'tag-blocked',
      'SUBMERGED': 'tag-blocked',
    }[status] || 'tag-demo';
    return `<span class="tag ${cls}">${escapeHtml(status)}</span>`;
  }

  // ================================================================
  //  RENDER: OVERVIEW CARDS
  // ================================================================

  function renderOverview(data) {
    const level = data.current_risk_level || 'LOW';
    const score = data.current_risk_score != null ? data.current_risk_score : 20;

    const riskEl = $('#overview-risk-level');
    riskEl.textContent = level;
    riskEl.className = `stat-value level-${level}`;

    $('#overview-risk-score').textContent = `Score: ${Math.round(score)}%`;
    $('#overview-alerts-count').textContent = data.active_alerts_count ?? 0;
    $('#overview-reports-count').textContent = data.citizen_reports_count ?? 0;
    $('#overview-unverified-count').textContent = data.unverified_reports_count ?? 0;
    $('#overview-distress-count').textContent = data.distress_signals_count ?? 0;
    $('#overview-roads-count').textContent = data.affected_roads_count ?? 0;
    $('#overview-zones-count').textContent = data.operational_safe_zones_count ?? 0;
  }

  // ================================================================
  //  RENDER: RISK DETAIL
  // ================================================================

  function renderRisk(data) {
    const score = data.risk_score != null ? data.risk_score : 20;
    const level = data.risk_level || 'LOW';
    const circumference = 2 * Math.PI * 52; // ~326.73
    const offset = circumference - (score / 100) * circumference;
    const color = riskColor(level);

    const fill = $('#risk-ring-fill');
    fill.style.strokeDashoffset = offset;
    fill.style.stroke = color;

    const percentEl = $('#risk-percent');
    percentEl.textContent = `${Math.round(score)}%`;
    percentEl.style.color = color;

    const levelText = $('#risk-level-text');
    levelText.textContent = level;
    levelText.style.color = color;

    // Source tag
    $('#risk-source-value').textContent = data.source_tag || 'SIMULATED_DEMO_DATA';

    // Last updated
    if (data.evaluated_at) {
      const evalDate = new Date(data.evaluated_at);
      const now = new Date();
      const diffMs = now - evalDate;
      const diffMin = Math.max(0, Math.floor(diffMs / 60000));
      $('#risk-updated-value').textContent = diffMin === 0 ? 'just now' : `${diffMin} min ago`;
    } else {
      $('#risk-updated-value').textContent = `${data.data_freshness_minutes || 5} min ago`;
    }

    // Risk factors
    const factors = data.main_risk_factors || [];
    const container = $('#risk-factors-list');
    if (factors.length === 0) {
      container.innerHTML = '<div class="empty-state"><span class="empty-icon">📊</span> No risk factor data</div>';
      return;
    }
    container.innerHTML = factors.map(f => `
      <div class="risk-factor-item">
        <div class="risk-factor-header">
          <span class="risk-factor-name">${escapeHtml(f.description_en || f.factor_key)}</span>
          <span class="risk-factor-pct">${f.contribution_percentage}%</span>
        </div>
        <div class="risk-factor-bar">
          <div class="risk-factor-fill" style="width:${Math.min(100, f.contribution_percentage * 2)}%;background:${color}"></div>
        </div>
        ${f.value != null ? `<span class="risk-factor-desc">${f.value} ${f.unit || ''}</span>` : ''}
      </div>
    `).join('');

    // Animate card border for risk changes
    if (lastRiskLevel !== level) {
      lastRiskLevel = level;
      const card = $('#card-risk');
      card.style.borderColor = color;
      setTimeout(() => { card.style.borderColor = ''; }, 2000);
    }
  }

  // ================================================================
  //  RENDER: ALERTS
  // ================================================================

  function renderAlerts(alerts) {
    const container = $('#alerts-list');
    const badge = $('#alerts-count-badge');

    if (!alerts || alerts.length === 0) {
      container.innerHTML = '<div class="empty-state"><span class="empty-icon">🔔</span> No active alerts</div>';
      badge.style.display = 'none';
      return;
    }

    badge.textContent = alerts.length;
    badge.style.display = 'inline-flex';

    container.innerHTML = alerts.map(a => `
      <div class="alert-item">
        <div class="alert-level-indicator ${escapeHtml(a.alert_level)}"></div>
        <div class="alert-body">
          <div class="alert-title-text">${escapeHtml(a.title)}</div>
          <div class="alert-message">${escapeHtml(a.message_en)}</div>
          <div class="alert-time">
            <span class="tag tag-${a.alert_level === 'CRITICAL' ? 'critical' : 'low'}">${escapeHtml(a.alert_level)}</span>
            &nbsp;·&nbsp;${formatTime(a.issued_at)}
            &nbsp;·&nbsp;<span class="tag tag-demo">${escapeHtml(a.source_tag || 'SIMULATED_DEMO_DATA')}</span>
          </div>
        </div>
      </div>
    `).join('');
  }

  // ================================================================
  //  RENDER: DISTRESS SIGNALS
  // ================================================================

  function renderDistress(events) {
    const tbody = $('#distress-tbody');
    const badge = $('#distress-count-badge');

    if (!events || events.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="empty-state"><span class="empty-icon">🆘</span> No distress signals received</td></tr>';
      badge.style.display = 'none';
      return;
    }

    badge.textContent = events.length;
    badge.style.display = 'inline-flex';

    tbody.innerHTML = events.map(e => `
      <tr>
        <td>
          <strong>${escapeHtml(e.user_name || 'Unknown')}</strong>
          <br><span class="text-muted" style="font-size:0.68rem">${escapeHtml(e.user_phone || '')}</span>
        </td>
        <td><span class="tag tag-critical">${escapeHtml(e.distress_type || 'NEED_HELP')}</span></td>
        <td style="font-size:0.72rem;">${e.latitude.toFixed(4)}, ${e.longitude.toFixed(4)}</td>
        <td style="font-size:0.72rem;">${formatTime(e.created_at)}</td>
      </tr>
    `).join('');
  }

  // ================================================================
  //  RENDER: CITIZEN REPORTS
  // ================================================================

  function renderReports(reports) {
    const tbody = $('#reports-tbody');
    const badge = $('#reports-unverified-badge');
    const unverifiedCount = reports ? reports.filter(r => r.verification_status === 'UNVERIFIED').length : 0;

    if (!reports || reports.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><span class="empty-icon">📋</span> No citizen reports</td></tr>';
      badge.style.display = 'none';
      return;
    }

    if (unverifiedCount > 0) {
      badge.textContent = `${unverifiedCount} unverified`;
      badge.style.display = 'inline-flex';
    } else {
      badge.style.display = 'none';
    }

    tbody.innerHTML = reports.map(r => {
      const isVerified = r.verification_status === 'VERIFIED';
      const statusTag = isVerified
        ? '<span class="tag tag-verified">VERIFIED</span>'
        : '<span class="tag tag-unverified">UNVERIFIED</span>';
      const sourceTag = `<span class="tag tag-citizen">${escapeHtml(r.source_tag || 'CITIZEN_REPORT')}</span>`;
      const verifyBtn = isVerified
        ? '<span class="text-muted" style="font-size:0.7rem;">✓ Done</span>'
        : `<button class="btn btn-verify" data-report-id="${r.id}" onclick="window._verifyReport('${r.id}')">VERIFY</button>`;

      return `
        <tr>
          <td><span class="tag tag-demo">${escapeHtml(r.disaster_category)}</span></td>
          <td style="max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(r.description || '')}">${escapeHtml(r.description || '—')}</td>
          <td style="font-size:0.72rem;">${r.latitude.toFixed(4)}, ${r.longitude.toFixed(4)}</td>
          <td style="font-size:0.72rem;">${formatTime(r.created_at)}</td>
          <td>${statusTag}</td>
          <td>${sourceTag}</td>
          <td>${verifyBtn}</td>
        </tr>
      `;
    }).join('');
  }

  // ================================================================
  //  RENDER: ROUTES
  // ================================================================

  function renderRoutes(data) {
    const container = $('#routes-list');
    const routes = data && data.routes ? data.routes : [];

    if (routes.length === 0) {
      container.innerHTML = '<div class="empty-state"><span class="empty-icon">🛣️</span> No route data available</div>';
      return;
    }

    container.innerHTML = routes.map(r => `
      <div class="route-item ${r.recommended ? 'recommended' : ''}">
        <span class="route-name">
          ${r.recommended ? '⭐ ' : ''}${escapeHtml(r.route_name)}
          ${r.recommended ? '<span class="tag tag-verified" style="margin-left:0.4rem">RECOMMENDED</span>' : ''}
        </span>
        <div class="route-meta">
          <span>${(r.distance_meters / 1000).toFixed(1)} km</span>
          <span>~${r.estimated_time_minutes} min</span>
          ${roadStatusTag(r.road_status)}
          <span class="text-muted">Risk: ${r.risk_score}%</span>
        </div>
      </div>
    `).join('');
  }

  // ================================================================
  //  MAP
  // ================================================================

  function initMap() {
    if (map) return;
    try {
      map = L.map('leaflet-map', {
        center: CITIZEN_COORDS,
        zoom: 14,
        zoomControl: true,
        attributionControl: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 18,
      }).addTo(map);

      // Fix Leaflet default icon path for vendored images
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'vendor/leaflet/images/marker-icon-2x.png',
        iconUrl: 'vendor/leaflet/images/marker-icon.png',
        shadowUrl: 'vendor/leaflet/images/marker-shadow.png',
      });

      // Citizen marker (always present)
      const citizenIcon = L.divIcon({
        className: '',
        html: '<div style="width:14px;height:14px;background:var(--accent,#38bdf8);border:2px solid #fff;border-radius:50%;box-shadow:0 0 8px rgba(56,189,248,0.5);"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      });
      L.marker(CITIZEN_COORDS, { icon: citizenIcon })
        .bindPopup('<strong>Demo Citizen</strong><br>Kurla, Mumbai<br><em style="font-size:0.8em">SIMULATED DEMO DATA</em>')
        .addTo(map);

      // Delay resize fix for tabs / hidden containers
      setTimeout(() => map.invalidateSize(), 200);
    } catch (err) {
      console.warn('Map initialization failed:', err);
    }
  }

  function updateMapMarkers(safeZones, routesData) {
    if (!map) return;

    // Clear old markers (keep first citizen marker)
    mapMarkers.forEach(m => map.removeLayer(m));
    mapMarkers = [];

    // Safe zone markers
    if (safeZones && safeZones.length > 0) {
      safeZones.forEach(sz => {
        if (sz.latitude && sz.longitude) {
          const szIcon = L.divIcon({
            className: '',
            html: '<div style="width:14px;height:14px;background:#34d399;border:2px solid #fff;border-radius:3px;box-shadow:0 0 6px rgba(52,211,153,0.5);"></div>',
            iconSize: [14, 14],
            iconAnchor: [7, 7],
          });
          const marker = L.marker([sz.latitude, sz.longitude], { icon: szIcon })
            .bindPopup(`<strong>${escapeHtml(sz.name)}</strong><br>${escapeHtml(sz.type)}<br>Capacity: ${sz.capacity}<br><em style="font-size:0.8em">${escapeHtml(sz.source_tag || 'OFFICIAL_DATA')}</em>`)
            .addTo(map);
          mapMarkers.push(marker);
        }
      });
    }

    // Route lines (if route data available with coordinates)
    // The demo routes use seeded road data, so we display markers for route status
    if (routesData && routesData.routes) {
      // Show route endpoint approximations based on seeded road geometry
      const routeCoords = [
        { name: 'Route A End', coords: [19.085, 72.885] },
        { name: 'Route B End', coords: [19.089, 72.890] },
        { name: 'Route C End', coords: [19.090, 72.888] },
      ];

      routesData.routes.forEach((route, i) => {
        if (i < routeCoords.length) {
          const rc = routeCoords[i];
          const isBlocked = route.road_status === 'BLOCKED' || route.road_status === 'SUBMERGED';
          const color = isBlocked ? '#ef4444' : (route.road_status === 'HIGH_RISK' ? '#f97316' : '#22d3ee');

          // Route line from citizen to endpoint
          const polyline = L.polyline([CITIZEN_COORDS, rc.coords], {
            color: color,
            weight: isBlocked ? 2 : 3,
            opacity: isBlocked ? 0.4 : 0.7,
            dashArray: isBlocked ? '8,8' : null,
          }).bindPopup(`<strong>${escapeHtml(route.route_name)}</strong><br>Status: ${escapeHtml(route.road_status)}<br>Risk: ${route.risk_score}%`)
            .addTo(map);
          mapMarkers.push(polyline);
        }
      });
    }
  }

  // ================================================================
  //  VERIFY REPORT HANDLER
  // ================================================================

  window._verifyReport = async function (reportId) {
    const btn = document.querySelector(`button[data-report-id="${reportId}"]`);
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Verifying…';
    }

    try {
      await verifyReport(reportId);
      showToast('Report verified successfully.', 'success');
      await refreshReports();
    } catch (err) {
      showToast(`Failed to verify report: ${err.message}`, 'error');
      if (btn) {
        btn.disabled = false;
        btn.textContent = 'VERIFY';
      }
    }
  };

  // ================================================================
  //  DEMO CONTROL HANDLERS
  // ================================================================

  async function handleSimulateFlood() {
    const btn = $('#btn-simulate-flood');
    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> Simulating…';
    try {
      const result = await simulateFlood();
      showToast(`Flood simulated! Risk level: ${result.risk_level}, Score: ${Math.round(result.risk_score)}%`, 'success');
      await refreshAll();
    } catch (err) {
      showToast(`Simulation failed: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span>🔴</span> SIMULATE FLOOD';
    }
  }

  async function handleBlockRoad() {
    const btn = $('#btn-block-road');
    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> Blocking…';
    try {
      const result = await simulateBlockedRoad();
      showToast(`Road blocked: ${result.road_name} (${result.previous_status} → ${result.new_status})`, 'success');
      await refreshAll();
    } catch (err) {
      showToast(`Block road failed: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span>🚧</span> BLOCK ROAD';
    }
  }

  async function handleRestoreNormal() {
    const btn = $('#btn-restore-normal');
    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> Restoring…';
    try {
      const result = await simulateNormal();
      showToast(`Baseline restored. Risk: ${result.risk_level}, Score: ${Math.round(result.risk_score)}%`, 'success');
      await refreshAll();
    } catch (err) {
      showToast(`Restore failed: ${err.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span>✅</span> RESTORE NORMAL';
    }
  }

  // ================================================================
  //  DATA REFRESH
  // ================================================================

  async function refreshRisk() {
    try {
      const risk = await getCurrentRisk();
      renderRisk(risk);
    } catch (err) {
      console.warn('Risk refresh failed:', err.message);
    }
  }

  async function refreshOverview() {
    try {
      const overview = await getAdminOverview();
      renderOverview(overview);
    } catch (err) {
      console.warn('Overview refresh failed:', err.message);
    }
  }

  async function refreshAlerts() {
    try {
      const alerts = await getAlerts();
      renderAlerts(alerts);
    } catch (err) {
      console.warn('Alerts refresh failed:', err.message);
    }
  }

  async function refreshDistress() {
    try {
      const events = await getDistressSignals();
      renderDistress(events);
    } catch (err) {
      console.warn('Distress refresh failed:', err.message);
    }
  }

  async function refreshReports() {
    try {
      const reports = await getReports();
      renderReports(reports);
    } catch (err) {
      console.warn('Reports refresh failed:', err.message);
    }
  }

  async function refreshRoutes() {
    try {
      const routes = await getRoutes();
      renderRoutes(routes);
      return routes;
    } catch (err) {
      console.warn('Routes refresh failed:', err.message);
      return null;
    }
  }

  async function refreshMap() {
    try {
      const [safeZones, routes] = await Promise.all([getSafeZones(), getRoutes()]);
      updateMapMarkers(safeZones, routes);
    } catch (err) {
      console.warn('Map refresh failed:', err.message);
    }
  }

  async function refreshAll() {
    try {
      const [risk, overview, alerts, distress, reports, routes, safeZones] = await Promise.allSettled([
        getCurrentRisk(),
        getAdminOverview(),
        getAlerts(),
        getDistressSignals(),
        getReports(),
        getRoutes(),
        getSafeZones(),
      ]);

      setConnectionStatus(true);

      if (risk.status === 'fulfilled') renderRisk(risk.value);
      if (overview.status === 'fulfilled') renderOverview(overview.value);
      if (alerts.status === 'fulfilled') renderAlerts(alerts.value);
      if (distress.status === 'fulfilled') renderDistress(distress.value);
      if (reports.status === 'fulfilled') renderReports(reports.value);
      if (routes.status === 'fulfilled') renderRoutes(routes.value);

      // Update map markers
      const szData = safeZones.status === 'fulfilled' ? safeZones.value : [];
      const rtData = routes.status === 'fulfilled' ? routes.value : null;
      updateMapMarkers(szData, rtData);

    } catch (err) {
      setConnectionStatus(false);
      console.error('Dashboard refresh failed:', err);
    }
  }

  // ================================================================
  //  POLLING
  // ================================================================

  function startPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(async () => {
      try {
        await refreshAll();
      } catch (err) {
        setConnectionStatus(false);
      }
    }, POLL_INTERVAL_MS);
  }

  // ================================================================
  //  TIME FORMATTING
  // ================================================================

  function formatTime(isoString) {
    if (!isoString) return '—';
    try {
      const d = new Date(isoString);
      if (isNaN(d.getTime())) return '—';
      const now = new Date();
      const diffMs = now - d;
      const diffMin = Math.floor(diffMs / 60000);
      if (diffMin < 1) return 'just now';
      if (diffMin < 60) return `${diffMin}m ago`;
      const diffHr = Math.floor(diffMin / 60);
      if (diffHr < 24) return `${diffHr}h ago`;
      return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
    } catch (_) {
      return '—';
    }
  }

  // ================================================================
  //  INITIALIZATION
  // ================================================================

  async function init() {
    // Bind demo control buttons
    $('#btn-simulate-flood').addEventListener('click', handleSimulateFlood);
    $('#btn-block-road').addEventListener('click', handleBlockRoad);
    $('#btn-restore-normal').addEventListener('click', handleRestoreNormal);

    // Initialize map
    initMap();

    // Initial data load
    try {
      await refreshAll();
      setConnectionStatus(true);
    } catch (err) {
      setConnectionStatus(false);
      showToast('Could not connect to backend. Please start the server.', 'error');
    }

    // Start polling
    startPolling();

    console.log('JalRaksha Admin Dashboard — Phase D initialized');
    console.log(`API Base: ${API_BASE}`);
    console.log(`Polling interval: ${POLL_INTERVAL_MS}ms`);
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
