// Client API — toutes les requêtes vers le backend FastAPI
const BASE = "http://localhost:8000";

function token() { return localStorage.getItem("ps_token"); }

export function isLoggedIn() { return !!token(); }

export function logout() {
  localStorage.removeItem("ps_token");
  window.location.href = "/";
}

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
      ...options.headers,
    },
  });
  if (res.status === 401) { logout(); return; }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Erreur serveur");
  }
  return res.json();
}

export const api = {
  register: (email, password) =>
    request("/api/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  login: (email, password) =>
    request("/api/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  getProfile: () => request("/api/profile"),
  saveProfile: (data) =>
    request("/api/profile", { method: "POST", body: JSON.stringify(data) }),
  portfolio: () => request("/api/portfolio"),
  frontier: () => request("/api/frontier"),
  risk: () => request("/api/risk"),
  regimes: () => request("/api/regimes"),
  backtest: () => request("/api/backtest"),
  explain: () => request("/api/explain"),
};
