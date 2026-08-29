// Thin wrapper around the JalRaksha Phase B backend API.
// Backend base URL is configurable via ?api=<url> in the page URL,
// defaulting to the standard local dev server.
const params = new URLSearchParams(window.location.search);
export const API_BASE = params.get('api') || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

function getToken() {
  return localStorage.getItem('jalraksha_demo_token');
}

export function setToken(token) {
  localStorage.setItem('jalraksha_demo_token', token);
}

export function clearToken() {
  localStorage.removeItem('jalraksha_demo_token');
}

async function request(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (!token) throw new ApiError('Not logged in.', 401);
    headers['Authorization'] = `Bearer ${token}`;
  }

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
      if (data && data.detail) detail = typeof data.detail === 'string' ? data.detail : detail;
    } catch (_) { /* non-JSON error body */ }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) return null;
  return response.json();
}

// ---- Auth -------------------------------------------------------------
export const demoLogin = () => request('/demo/login', { method: 'POST' });
export const getMe = () => request('/users/me', { auth: true });

// ---- Flood risk ---------------------------------------------------------
export const getCurrentRisk = () => request('/flood-risk/current');
export const getRiskWhy = () => request('/flood-risk/current/why');

// ---- Alerts ---------------------------------------------------------------
export const getAlerts = () => request('/alerts');

// ---- Safe zones -------------------------------------------------------------
export const getNearbySafeZones = (lat, lng) =>
  request(`/safe-zones/nearby?latitude=${lat}&longitude=${lng}`);

// ---- Routes -------------------------------------------------------------------
export const getSafestRoutes = () => request('/routes/safest');

// ---- Emergency circle -------------------------------------------------------------
export const postImSafe = (data) => request('/emergency-circle/im-safe', { method: 'POST', body: data, auth: true });
export const postNeedHelp = (data) => request('/emergency-circle/need-help', { method: 'POST', body: data, auth: true });

// ---- Reports -----------------------------------------------------------------------
export const submitReport = (data) => request('/reports', { method: 'POST', body: data, auth: true });
