import React, { useState } from "react";
import { api } from "../api";

export default function Rebalance() {
  const [positions, setPositions] = useState([{ ticker: "", euros: "" }]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function update(i, field, value) {
    const next = [...positions];
    next[i][field] = field === "ticker" ? value.toUpperCase() : value;
    setPositions(next);
  }

  function addRow() {
    setPositions([...positions, { ticker: "", euros: "" }]);
  }

  async function compare() {
    const body = {};
    positions.forEach((p) => {
      if (p.ticker && Number(p.euros) > 0) body[p.ticker] = Number(p.euros);
    });
    if (Object.keys(body).length === 0) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/compare", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("ps_token")}`,
        },
        body: JSON.stringify({ positions: body }),
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  const badge = { ok: "badge-green", sur: "badge-red", sous: "badge-amber" };
  const label = {
    ok: "✅ Aligné",
    sur: "⚠️ Surpondéré",
    sous: "📉 Sous-pondéré",
  };

  return (
    <>
      <h1>Rééquilibrage</h1>
      <p className="subtitle">
        Saisissez votre portefeuille actuel (depuis votre courtier) et découvrez
        les écarts avec votre allocation optimale.
      </p>

      <div className="card">
        <h2>Mes positions actuelles</h2>
        {positions.map((p, i) => (
          <div key={i} style={{ display: "flex", gap: 12, marginBottom: 10 }}>
            <input
              style={{
                width: 140,
                padding: "10px 14px",
                border: "1px solid var(--border)",
                borderRadius: 8,
              }}
              placeholder="Ticker (ex: AAPL)"
              value={p.ticker}
              onChange={(e) => update(i, "ticker", e.target.value)}
            />
            <input
              style={{
                width: 180,
                padding: "10px 14px",
                border: "1px solid var(--border)",
                borderRadius: 8,
              }}
              type="number"
              placeholder="Montant en €"
              value={p.euros}
              onChange={(e) => update(i, "euros", e.target.value)}
            />
          </div>
        ))}
        <div style={{ display: "flex", gap: 12, marginTop: 14 }}>
          <button
            className="btn"
            style={{ border: "1px solid var(--border)", background: "white" }}
            onClick={addRow}
          >
            + Ajouter une ligne
          </button>
          <button
            className="btn btn-primary"
            onClick={compare}
            disabled={loading}
          >
            {loading ? "Analyse..." : "Comparer à l'optimal"}
          </button>
        </div>
      </div>

      {result && (
        <div className="card">
          <h2>
            Votre portefeuille de {result.total.toLocaleString("fr-FR")} € vs
            l'allocation optimale ({result.profil})
          </h2>
          <table>
            <thead>
              <tr>
                <th>Actif</th>
                <th>Vous avez</th>
                <th>Optimal</th>
                <th>Statut</th>
                <th>Action suggérée</th>
              </tr>
            </thead>
            <tbody>
              {result.comparison.slice(0, 15).map((r) => (
                <tr key={r.ticker}>
                  <td>
                    <strong>{r.ticker}</strong>
                  </td>
                  <td className="num">{r.current_pct}%</td>
                  <td className="num">{r.optimal_pct}%</td>
                  <td>
                    <span className={`badge ${badge[r.statut]}`}>
                      {label[r.statut]}
                    </span>
                  </td>
                  <td className="num">{r.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="caption">
            💡 Ces suggestions sont indicatives — pensez aux frais de
            transaction et à la fiscalité avant de rééquilibrer.
          </p>
        </div>
      )}
    </>
  );
}
