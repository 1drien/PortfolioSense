import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Auth() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const fn = mode === "login" ? api.login : api.register;
      const { token } = await fn(email, password);
      localStorage.setItem("ps_token", token);
      navigate(mode === "register" ? "/profil" : "/portefeuille");
      window.location.reload();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>
          Portfolio<span style={{ color: "var(--accent)" }}>Sense</span>
        </h1>
        <p className="tagline">
          Les stratégies des grands fonds, enfin accessibles.
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={submit}>
          <div className="field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@exemple.fr"
              required
            />
          </div>
          <div className="field">
            <label>Mot de passe</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="6 caractères minimum"
              required
              minLength={6}
            />
          </div>
          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading
              ? "Chargement..."
              : mode === "login"
              ? "Se connecter"
              : "Créer mon compte"}
          </button>
        </form>

        <div className="auth-switch">
          {mode === "login" ? (
            <>
              Pas encore de compte ?{" "}
              <a onClick={() => setMode("register")}>S'inscrire</a>
            </>
          ) : (
            <>
              Déjà un compte ?{" "}
              <a onClick={() => setMode("login")}>Se connecter</a>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
