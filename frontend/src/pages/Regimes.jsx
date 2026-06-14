import React, { useState, useEffect } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
  LineChart,
  Line,
  ReferenceLine,
} from "recharts";
import { api } from "../api";

const REGIME_COLORS = { bull: "#0d6b58", bear: "#c2421f", lateral: "#9a6a10" };
const REGIME_NAMES = {
  bull: "Bull 🟢",
  bear: "Bear 🔴",
  lateral: "Latéral 🟡",
};

export default function Regimes() {
  const [data, setData] = useState(null);
  const [corrData, setCorrData] = useState(null);

  useEffect(() => {
    api.regimes().then(setData);
    api.correlations().then(setCorrData);
  }, []);

  if (!data)
    return <div className="loading">Notre IA analyse les marchés (HMM)...</div>;

  const { meta } = data;

  // Préparer les données par régime pour le scatter
  const byRegime = { bull: [], bear: [], lateral: [] };
  data.history.forEach((p, i) => {
    byRegime[p.regime]?.push({ x: i, y: p.value, date: p.date });
  });

  return (
    <>
      <h1>Météo des marchés</h1>
      <p className="subtitle">
        Notre intelligence artificielle (Hidden Markov Model) détecte
        automatiquement le régime de marché en continu.
      </p>

      <div className="card regime-hero">
        <div className="regime-emoji">
          <span
            style={{
              display: "inline-block",
              width: 40,
              height: 40,
              borderRadius: "50%",
              background:
                data.regime_actuel === "bull"
                  ? "#0d6b58"
                  : data.regime_actuel === "bear"
                    ? "#c2421f"
                    : "#9a6a10",
            }}
          />
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ marginBottom: 4 }}>{meta.label}</h2>
          <p style={{ color: "var(--text-2)", marginBottom: 10 }}>
            {meta.explication}
          </p>
          <span className="badge badge-green">
            Stratégie recommandée : {meta.strategie}
          </span>
        </div>
      </div>

      {data.aligne ? (
        <div className="alert alert-success">
          ✅ Votre stratégie actuelle est alignée avec le régime de marché
          détecté.
        </div>
      ) : (
        <div className="alert alert-warning">
          ⚠️ <strong>Alerte :</strong> votre profil ({data.profil_user}) suggère
          une autre stratégie que celle adaptée au marché actuel. En période de{" "}
          {meta.label.toLowerCase()}, nous recommandons de basculer
          temporairement vers <strong>{meta.strategie}</strong>.
        </div>
      )}

      <div className="card">
        <h2>L'historique vu par notre IA</h2>
        <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
          Validation : COVID (mars 2020) et la crise des taux (2022) doivent
          apparaître en rouge — c'est bien le cas.
        </p>
        <ResponsiveContainer width="100%" height={380}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis
              type="number"
              dataKey="x"
              tickFormatter={(i) => data.history[i]?.date?.slice(0, 4) || ""}
              domain={[0, data.history.length - 1]}
              tickCount={8}
            />
            <YAxis
              type="number"
              dataKey="y"
              domain={["auto", "auto"]}
              label={{
                value: "Marché (base 1)",
                angle: -90,
                position: "insideLeft",
                fontSize: 12,
              }}
            />
            <Tooltip
              formatter={(v) => v.toFixed(2)}
              labelFormatter={(i) => data.history[i]?.date || ""}
            />
            <Legend />
            {Object.entries(byRegime).map(([regime, points]) => (
              <Scatter
                key={regime}
                name={REGIME_NAMES[regime]}
                data={points}
                fill={REGIME_COLORS[regime]}
                shape="circle"
                isAnimationActive={false}
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="grid-3">
        {Object.entries(data.repartition).map(([regime, pct]) => (
          <div className="card metric" key={regime}>
            <div className="metric-label">{REGIME_NAMES[regime]}</div>
            <div className="metric-value">{pct}%</div>
            <div className="metric-sub">du temps depuis 2015</div>
          </div>
        ))}
      </div>
      {corrData && (
  <>
    <div className="card">
      <h2>🔗 Corrélations entre actifs</h2>
      <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
        Quand les corrélations explosent, les actifs chutent ensemble — la diversification ne protège plus. Signal clé du modèle HMM.
      </p>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={corrData.history} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="date" tickFormatter={(d) => d?.slice(0, 4)} tickCount={8} />
          <YAxis domain={[0, 1]} label={{ value: "Corrélation", angle: -90, position: "insideLeft", fontSize: 12 }} />
          <Tooltip formatter={(v) => v.toFixed(3)} />
          <ReferenceLine y={0.65} stroke="#c2421f" strokeDasharray="4 4" label={{ value: "Seuil Bear", fill: "#c2421f", fontSize: 11 }} />
          <ReferenceLine y={0.40} stroke="#0d6b58" strokeDasharray="4 4" label={{ value: "Seuil Bull", fill: "#0d6b58", fontSize: 11 }} />
          <Line type="monotone" dataKey="corr_moyenne" stroke="#185FA5" dot={false} strokeWidth={1.5} name="Corrélation moyenne" />
        </LineChart>
      </ResponsiveContainer>
    </div>

    <div className="grid-3">
      <div className="card metric">
        <div className="metric-label">Corrélation actuelle</div>
        <div className="metric-value" style={{ color: corrData.corr_actuelle > 0.55 ? "#c2421f" : "#0d6b58" }}>
          {corrData.corr_actuelle}
        </div>
        <div className="metric-sub">{corrData.corr_actuelle > 0.55 ? "⚠ Élevée" : "✓ Normale"}</div>
      </div>
      <div className="card metric">
        <div className="metric-label">Pic COVID (mars 2020)</div>
        <div className="metric-value">{corrData.corr_covid_max}</div>
        <div className="metric-sub">Maximum historique</div>
      </div>
      <div className="card metric">
        <div className="metric-label">Normale (2021)</div>
        <div className="metric-value">{corrData.corr_normale}</div>
        <div className="metric-sub">Référence basse</div>
      </div>
    </div>
  </>
)}
    </>
  );
}
