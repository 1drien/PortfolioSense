import React, { useState, useEffect } from "react";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, Legend, CartesianGrid,
} from "recharts";
import { api } from "../api";

const COLORS = [
  "#0d6b58", "#1d9e75", "#3eb489", "#65c39e", "#8dd2b4",
  "#185fa5", "#378add", "#6aa9e8", "#9bc6f0", "#c2421f",
  "#d85a30", "#e58a64",
];

const STRAT_LABELS = {
  conservateur: "Minimum Variance — priorité à la stabilité",
  equilibre: "Risk Parity — risque équilibré entre tous les actifs",
  agressif: "Maximum Sharpe — rendement maximal par unité de risque",
};

export default function Portfolio() {
  const [data, setData] = useState(null);
  const [frontier, setFrontier] = useState(null);

  useEffect(() => {
    api.portfolio().then(setData);
    api.frontier().then(setFrontier);
  }, []);

  if (!data) return <div className="loading">Optimisation de votre portefeuille...</div>;

  const top12 = data.allocation.slice(0, 12);

  return (
    <>
      <h1>Mon portefeuille</h1>
      <p className="subtitle">
        Stratégie appliquée : <strong>{STRAT_LABELS[data.profil]}</strong>
      </p>

      <div className="grid-3">
        <div className="card metric">
          <div className="metric-label">Rendement espéré</div>
          <div className="metric-value positive">
            {(data.metrics.return * 100).toFixed(1)}% / an
          </div>
          <div className="metric-sub">Basé sur l'historique 2015-2024</div>
        </div>
        <div className="card metric">
          <div className="metric-label">Soit environ</div>
          <div className="metric-value positive">
            +{data.gain_espere.toLocaleString("fr-FR")} € / an
          </div>
          <div className="metric-sub">Sur votre capital de {data.capital.toLocaleString("fr-FR")} €</div>
        </div>
        <div className="card metric">
          <div className="metric-label">Ratio de Sharpe</div>
          <div className="metric-value">{data.metrics.sharpe.toFixed(2)}</div>
          <div className="metric-sub">Rendement par unité de risque</div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h2>Votre allocation pour {data.capital.toLocaleString("fr-FR")} €</h2>
          <div style={{ maxHeight: 360, overflowY: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>Actif</th>
                  <th>Montant</th>
                  <th>Poids</th>
                </tr>
              </thead>
              <tbody>
                {data.allocation.map((a) => (
                  <tr key={a.ticker}>
                    <td><strong>{a.ticker}</strong></td>
                    <td className="num">{a.euros.toLocaleString("fr-FR")} €</td>
                    <td className="num">{a.pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h2>Répartition</h2>
          <ResponsiveContainer width="100%" height={340}>
            <PieChart>
              <Pie
                data={top12}
                dataKey="euros"
                nameKey="ticker"
                innerRadius={70}
                outerRadius={120}
                paddingAngle={2}
                label={({ ticker, pct }) => `${ticker} ${pct}%`}
                labelLine={false}
                fontSize={11}
              >
                {top12.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(v) => `${v.toLocaleString("fr-FR")} €`}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {frontier && (
        <div className="card">
          <h2>Où se situe votre portefeuille ?</h2>
          <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
            Chaque point gris est un portefeuille possible. Les points colorés sont
            nos stratégies optimisées — toujours sur la frontière des meilleurs choix.
          </p>
          <ResponsiveContainer width="100%" height={380}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis
                type="number"
                dataKey="volatility"
                name="Volatilité"
                unit=""
                domain={["auto", "auto"]}
                tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                label={{ value: "Risque (volatilité annuelle)", position: "bottom", fontSize: 12 }}
              />
              <YAxis
                type="number"
                dataKey="return"
                name="Rendement"
                domain={["auto", "auto"]}
                tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                label={{ value: "Rendement", angle: -90, position: "insideLeft", fontSize: 12 }}
              />
              <Tooltip
                formatter={(v, name) => [`${(v * 100).toFixed(1)}%`, name]}
              />
              <Legend verticalAlign="top" />
              <Scatter
                name="Portefeuilles possibles"
                data={frontier.cloud}
                fill="#d4d8de"
                shape="circle"
                isAnimationActive={false}
              />
              <Scatter
                name="Max Sharpe (agressif)"
                data={[frontier.strategies.max_sharpe]}
                fill="#c2421f"
                shape="star"
              />
              <Scatter
                name="Min Variance (conservateur)"
                data={[frontier.strategies.min_variance]}
                fill="#185fa5"
                shape="diamond"
              />
              <Scatter
                name="Risk Parity (équilibré)"
                data={[frontier.strategies.risk_parity]}
                fill="#0d6b58"
                shape="circle"
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}

      <p className="caption">
        💡 PortfolioSense recommande — vous décidez. Pour appliquer cette
        allocation, passez vos ordres sur votre courtier habituel.
      </p>
    </>
  );
}
