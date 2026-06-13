import React, { useState } from "react";
import { api } from "../api";
import { Plus, Sparkles } from "lucide-react";

export default function Expert() {
  const [views, setViews] = useState([{ ticker: "", expected: "", conf: 70 }]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  function update(i, field, value) {
    const next = [...views];
    next[i][field] = field === "ticker" ? value.toUpperCase() : value;
    setViews(next);
  }

  function addView() {
    setViews([...views, { ticker: "", expected: "", conf: 70 }]);
  }

  async function run() {
    const v = {},
      c = {};
    views.forEach((row) => {
      if (row.ticker && row.expected !== "") {
        v[row.ticker] = Number(row.expected) / 100;
        c[row.ticker] = row.conf / 100;
      }
    });
    if (Object.keys(v).length === 0) return;
    setLoading(true);
    try {
      setResult(await api.blackLitterman(v, c));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1>Mode expert — Black-Litterman</h1>
      <p className="subtitle">
        Exprimez vos convictions sur certains actifs. Le modèle de
        Black-Litterman (1992) combine le consensus du marché avec vos vues pour
        produire une allocation sur mesure.
      </p>

      <div className="card">
        <h2>Mes convictions</h2>
        {views.map((row, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              gap: 12,
              marginBottom: 12,
              alignItems: "center",
            }}
          >
            <input
              style={{
                width: 120,
                padding: "10px 14px",
                border: "1px solid var(--border)",
                borderRadius: 8,
              }}
              placeholder="Ticker"
              value={row.ticker}
              onChange={(e) => update(i, "ticker", e.target.value)}
            />
            <span style={{ color: "var(--text-2)", fontSize: 13 }}>
              va faire
            </span>
            <input
              style={{
                width: 90,
                padding: "10px 14px",
                border: "1px solid var(--border)",
                borderRadius: 8,
              }}
              type="number"
              placeholder="% / an"
              value={row.expected}
              onChange={(e) => update(i, "expected", e.target.value)}
            />
            <span style={{ color: "var(--text-2)", fontSize: 13 }}>
              confiance
            </span>
            <input
              type="range"
              min={10}
              max={100}
              value={row.conf}
              style={{ width: 120 }}
              onChange={(e) => update(i, "conf", Number(e.target.value))}
            />
            <span style={{ fontSize: 13, width: 40 }}>{row.conf}%</span>
          </div>
        ))}
        <div style={{ display: "flex", gap: 12, marginTop: 14 }}>
          <button
            className="btn"
            style={{ border: "1px solid var(--border)", background: "white" }}
            onClick={addView}
          >
            <Plus size={15} /> Ajouter une vue
          </button>
          <button className="btn btn-primary" onClick={run} disabled={loading}>
            <Sparkles size={15} />{" "}
            {loading ? "Calcul..." : "Calculer l'allocation"}
          </button>
        </div>
      </div>

      {result && (
        <>
          <div className="grid-3">
            <div className="card metric">
              <div className="metric-label">Rendement espéré</div>
              <div className="metric-value positive">
                {(result.metrics.return * 100).toFixed(1)}%
              </div>
            </div>
            <div className="card metric">
              <div className="metric-label">Volatilité</div>
              <div className="metric-value">
                {(result.metrics.volatility * 100).toFixed(1)}%
              </div>
            </div>
            <div className="card metric">
              <div className="metric-label">Sharpe</div>
              <div className="metric-value">
                {result.metrics.sharpe.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="card">
            <h2>Allocation selon vos vues</h2>
            <table>
              <thead>
                <tr>
                  <th>Actif</th>
                  <th>Montant</th>
                  <th>Poids</th>
                </tr>
              </thead>
              <tbody>
                {result.allocation.map((a) => (
                  <tr key={a.ticker}>
                    <td>
                      <strong>{a.ticker}</strong>
                    </td>
                    <td className="num">{a.euros.toLocaleString("fr-FR")} €</td>
                    <td className="num">{a.pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}
