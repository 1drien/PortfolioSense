import React from "react";
import {
  Routes,
  Route,
  NavLink,
  Navigate,
  useLocation,
} from "react-router-dom";
import { isLoggedIn, logout, api } from "./api";
import Auth from "./pages/Auth";
import Onboarding from "./pages/Onboarding";
import Portfolio from "./pages/Portfolio";
import Risk from "./pages/Risk";
import Regimes from "./pages/Regimes";
import Performance from "./pages/Performance";
import Rebalance from "./pages/Rebalance";
import {
  Home,
  Briefcase,
  Shield,
  Brain,
  TrendingUp,
  RefreshCw,
  LogOut,
  RotateCw,
  Sparkles,
} from "lucide-react";

import Expert from "./pages/Expert";

function Layout({ children }) {
  const [refreshing, setRefreshing] = React.useState(false);
  const [refreshMsg, setRefreshMsg] = React.useState(null);

  async function refresh() {
    setRefreshing(true);
    setRefreshMsg(null);
    try {
      const r = await api.refresh();
      setRefreshMsg(r.message);
      if (r.status === "updated")
        setTimeout(() => window.location.reload(), 1500);
    } catch {
      setRefreshMsg("Erreur de connexion aux marchés.");
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          Portfolio<span>Sense</span>
        </div>
        <NavLink to="/profil" className="nav-link">
          <Home size={17} strokeWidth={2} /> Mon profil
        </NavLink>
        <NavLink to="/portefeuille" className="nav-link">
          <Briefcase size={17} strokeWidth={2} /> Mon portefeuille
        </NavLink>
        <NavLink to="/risque" className="nav-link">
          <Shield size={17} strokeWidth={2} /> Mon risque
        </NavLink>
        <NavLink to="/marches" className="nav-link">
          <Brain size={17} strokeWidth={2} /> Météo des marchés
        </NavLink>
        <NavLink to="/performance" className="nav-link">
          <TrendingUp size={17} strokeWidth={2} /> Performance
        </NavLink>
        <NavLink to="/reequilibrage" className="nav-link">
          <RotateCw size={17} strokeWidth={2} /> Rééquilibrage
        </NavLink>
        <NavLink to="/expert" className="nav-link">
          <Sparkles size={17} strokeWidth={2} /> Mode expert
        </NavLink>

        <div style={{ padding: "16px 12px" }}>
          <button
            className="btn btn-primary btn-block"
            style={{ fontSize: 13, padding: "9px 12px" }}
            onClick={refresh}
            disabled={refreshing}
          >
            {refreshing ? (
              "Mise à jour..."
            ) : (
              <>
                <RefreshCw size={15} /> Actualiser les marchés
              </>
            )}
          </button>
          {refreshMsg && (
            <div
              style={{ fontSize: 11.5, color: "var(--text-2)", marginTop: 8 }}
            >
              {refreshMsg}
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          <button onClick={logout}>
            <LogOut size={14} style={{ verticalAlign: "-2px" }} /> Se
            déconnecter
          </button>
          <div style={{ marginTop: 8 }}>
            Outil d'aide à la décision.
            <br />
            N'exécute aucun ordre.
          </div>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

function Protected({ children }) {
  const location = useLocation();
  if (!isLoggedIn()) return <Navigate to="/" state={{ from: location }} />;
  return <Layout>{children}</Layout>;
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={isLoggedIn() ? <Navigate to="/portefeuille" /> : <Auth />}
      />
      <Route
        path="/profil"
        element={
          <Protected>
            <Onboarding />
          </Protected>
        }
      />
      <Route
        path="/portefeuille"
        element={
          <Protected>
            <Portfolio />
          </Protected>
        }
      />
      <Route
        path="/risque"
        element={
          <Protected>
            <Risk />
          </Protected>
        }
      />
      <Route
        path="/marches"
        element={
          <Protected>
            <Regimes />
          </Protected>
        }
      />
      <Route
        path="/performance"
        element={
          <Protected>
            <Performance />
          </Protected>
        }
      />
      <Route
        path="/reequilibrage"
        element={
          <Protected>
            <Rebalance />
          </Protected>
        }
      />
      <Route
        path="/expert"
        element={
          <Protected>
            <Expert />
          </Protected>
        }
      />
    </Routes>
  );
}
