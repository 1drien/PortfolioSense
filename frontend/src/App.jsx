import React from "react";
import { Routes, Route, NavLink, Navigate, useLocation } from "react-router-dom";
import { isLoggedIn, logout } from "./api";
import Auth from "./pages/Auth";
import Onboarding from "./pages/Onboarding";
import Portfolio from "./pages/Portfolio";
import Risk from "./pages/Risk";
import Regimes from "./pages/Regimes";
import Performance from "./pages/Performance";

function Layout({ children }) {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          Portfolio<span>Sense</span>
        </div>
        <NavLink to="/profil" className="nav-link">🏠 Mon profil</NavLink>
        <NavLink to="/portefeuille" className="nav-link">💼 Mon portefeuille</NavLink>
        <NavLink to="/risque" className="nav-link">🛡️ Mon risque</NavLink>
        <NavLink to="/marches" className="nav-link">🧠 Météo des marchés</NavLink>
        <NavLink to="/performance" className="nav-link">📈 Performance</NavLink>
        <div className="sidebar-footer">
          <button onClick={logout}>Se déconnecter</button>
          <div style={{ marginTop: 8 }}>
            Outil d'aide à la décision.
            <br />N'exécute aucun ordre.
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
      <Route path="/" element={isLoggedIn() ? <Navigate to="/portefeuille" /> : <Auth />} />
      <Route path="/profil" element={<Protected><Onboarding /></Protected>} />
      <Route path="/portefeuille" element={<Protected><Portfolio /></Protected>} />
      <Route path="/risque" element={<Protected><Risk /></Protected>} />
      <Route path="/marches" element={<Protected><Regimes /></Protected>} />
      <Route path="/performance" element={<Protected><Performance /></Protected>} />
    </Routes>
  );
}
