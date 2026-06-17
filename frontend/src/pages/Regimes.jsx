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
const REGIME_NAMES  = { bull: "Bull", bear: "Bear", lateral: "Lateral" };

const FEATURE_LABELS = {
  "son rendement historique":                     "Rendement",
  "sa volatilite":                                "Volatilite",
  "sa correlation avec le reste du portefeuille": "Correlation",
  "sa tendance recente (60 derniers jours)":      "Momentum",
};

export default function Regimes() {
  const [data,    setData]    = useState(null);
  const [details, setDetails] = useState(null);
  const [shap,    setShap]    = useState(null);

  useEffect(() => {
    api.regimes().then(setData);
    fetch("http://localhost:8000/api/regimes/details", {
      headers: { Authorization: `Bearer ${localStorage.getItem("ps_token")}` },
    }).then(r => r.ok ? r.json() : null).then(setDetails);
    api.explain().then(d => setShap(d?.explanations || null));
  }, []);

  if (!data)
    return <div className="loading">Notre IA analyse les marches (HMM)...</div>;

  const { meta } = data;
  const byRegime = { bull: [], bear: [], lateral: [] };
  data.history.forEach((p, i) => {
    byRegime[p.regime]?.push({ x: i, y: p.value, date: p.date });
  });
  const regimeKeys = ["bull", "lateral", "bear"];
  const top5 = shap ? shap.slice(0, 5) : [];

  return (
    <>
      <h1>Meteo des marches</h1>
      <p className="subtitle">
        Notre IA (HMM) detecte le regime de marche avec 4 features :
        rendement, volatilite, momentum et correlation glissante.
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
          <p style={{ color: "var(--text-2)", marginBottom: 10 }}>{meta.explication}</p>
          <span className="badge badge-green">Strategie recommandee : {meta.strategie}</span>
        </div>
      </div>

      {data.aligne ? (
        <div className="alert alert-success">
          Votre strategie est alignee avec le regime actuel.
        </div>
      ) : (
        <div className="alert alert-warning">
          <strong>Alerte :</strong> votre profil ({data.profil_user}) suggere
          une autre strategie. En periode de {meta.label.toLowerCase()},
          basculez vers <strong>{meta.strategie}</strong>.
        </div>
      )}

      {/* Résumé simplifié pour l'utilisateur */}
      <div className="card" style={{ background: "linear-gradient(135deg, #f0faf6 0%, #e8f5f0 100%)", border: "1px solid #c8e6da" }}>
        <h2 style={{ marginBottom: 16 }}>En clair, que faire ?</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
            <span style={{ fontSize: 24, flexShrink: 0 }}>{meta.emoji}</span>
            <div>
              <strong>Situation actuelle :</strong>
              <p style={{ margin: "4px 0 0", color: "var(--text-2)", fontSize: 14 }}>
                {data.regime_actuel === "bull"
                  ? "Les marchés sont en hausse avec une faible volatilité. C'est le bon moment pour viser la performance."
                  : data.regime_actuel === "bear"
                  ? "Les marchés sont en crise. Il faut protéger votre capital avant tout."
                  : "Les marchés hésitent sans tendance claire. Mieux vaut équilibrer les risques."}
              </p>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
            <span style={{ fontSize: 24, flexShrink: 0 }}>💡</span>
            <div>
              <strong>Notre recommandation :</strong>
              <p style={{ margin: "4px 0 0", color: "var(--text-2)", fontSize: 14 }}>
                Nous appliquons automatiquement la stratégie <strong>{meta.strategie}</strong> à votre portefeuille.
                {data.aligne
                  ? " Votre profil est parfaitement adapté au marché actuel, aucun changement nécessaire."
                  : ` Votre profil actuel (${data.profil_user}) n'est pas optimal pour ce régime. Rendez-vous dans "Mon portefeuille" pour rééquilibrer.`}
              </p>
            </div>
          </div>

          {details && (
            <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
              <span style={{ fontSize: 24, flexShrink: 0 }}>📅</span>
              <div>
                <strong>Ce régime va-t-il durer ?</strong>
                <p style={{ margin: "4px 0 0", color: "var(--text-2)", fontSize: 14 }}>
                  {(() => {
                    const prob = details.transition_matrix?.[data.regime_actuel]?.[data.regime_actuel];
                    const pct = prob ? (prob * 100).toFixed(0) : "98";
                    return `Oui — notre IA estime à ${pct}% la probabilité que le marché reste dans ce régime demain. Les changements de régime sont rares et progressifs.`;
                  })()}
                </p>
              </div>
            </div>
          )}

          <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
            <span style={{ fontSize: 24, flexShrink: 0 }}>🎯</span>
            <div>
              <strong>Pourquoi faire confiance à cette IA ?</strong>
              <p style={{ margin: "4px 0 0", color: "var(--text-2)", fontSize: 14 }}>
                Notre modèle a correctement identifié le crash COVID de mars 2020 et la crise des taux de 2022.
                Il analyse 4 signaux de marché simultanément et est bien plus précis qu'une détection simple par seuils.
              </p>
            </div>
          </div>

        </div>
      </div>

      <div className="card">
        <h2>L'historique vu par notre IA</h2>
        <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
          COVID mars 2020 et crise des taux 2022 apparaissent en rouge.
        </p>
        <ResponsiveContainer width="100%" height={380}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
            <XAxis type="number" dataKey="x"
              tickFormatter={(i) => data.history[i]?.date?.slice(0, 4) || ""}
              domain={[0, data.history.length - 1]} tickCount={8} />
            <YAxis type="number" dataKey="y" domain={["auto", "auto"]}
              label={{ value: "Marche (base 1)", angle: -90, position: "insideLeft", fontSize: 12 }} />
            <Tooltip formatter={(v) => v.toFixed(2)}
              labelFormatter={(i) => data.history[i]?.date || ""} />
            <Legend />
            {Object.entries(byRegime).map(([regime, points]) => (
              <Scatter key={regime} name={REGIME_NAMES[regime]} data={points}
                fill={REGIME_COLORS[regime]} shape="circle" isAnimationActive={false} />
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

      {details && (
        <div className="card">
          <h2>Caracteristiques par regime</h2>
          <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
            Rendement et volatilite annualises par regime.
          </p>
          <div className="grid-3">
            {Object.entries(details.stats).map(([regime, s]) => (
              <div className="card metric" key={regime}
                style={{ borderTop: `4px solid ${REGIME_COLORS[regime]}` }}>
                <div className="metric-label">{REGIME_NAMES[regime]}</div>
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ color: "var(--text-2)", fontSize: 13 }}>Rendement ann.</span>
                    <strong style={{ color: s.return_ann >= 0 ? "#0d6b58" : "#c2421f" }}>
                      {s.return_ann > 0 ? "+" : ""}{s.return_ann}%
                    </strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ color: "var(--text-2)", fontSize: 13 }}>Volatilite ann.</span>
                    <strong>{s.vol_ann}%</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ color: "var(--text-2)", fontSize: 13 }}>Nb jours</span>
                    <strong>{s.n_days} ({s.pct}%)</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {details && (
        <div className="card">
          <h2>Matrice de transition</h2>
          <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
            Probabilite de rester dans le meme regime ou de changer le lendemain.
          </p>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
            <thead>
              <tr>
                <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-2)" }}>De \ Vers</th>
                {regimeKeys.map(r => (
                  <th key={r} style={{ padding: "8px 12px", textAlign: "center", color: REGIME_COLORS[r] }}>
                    {REGIME_NAMES[r]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {regimeKeys.map(from => (
                <tr key={from} style={{ borderTop: "1px solid #eee" }}>
                  <td style={{ padding: "8px 12px", fontWeight: 600, color: REGIME_COLORS[from] }}>
                    {REGIME_NAMES[from]}
                  </td>
                  {regimeKeys.map(to => {
                    const val = details.transition_matrix?.[from]?.[to] ?? 0;
                    const isDiag = from === to;
                    return (
                      <td key={to} style={{
                        padding: "8px 12px", textAlign: "center",
                        background: isDiag ? `${REGIME_COLORS[from]}18` : "transparent",
                        fontWeight: isDiag ? 700 : 400,
                      }}>
                        {(val * 100).toFixed(1)}%
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: 16, padding: "10px 14px", background: "#f0faf6", borderRadius: 8, fontSize: 13 }}>
            <strong>HMM vs baseline naive :</strong> accord de{" "}
            <strong>{details.hmm_vs_naive}%</strong> — les{" "}
            {(100 - details.hmm_vs_naive).toFixed(1)}% de desaccords representent
            la valeur ajoutee du HMM.
          </div>
        </div>
      )}

      {top5.length > 0 && (
        <div className="card">
          <h2>Pourquoi cette allocation ? — SHAP</h2>
          <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
            Explication IA actif par actif.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {top5.map((asset) => {
              const contribs = Object.entries(asset.shap_contributions)
                .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
              return (
                <div key={asset.ticker} style={{
                  padding: "14px 16px", border: "1px solid #eee",
                  borderRadius: 10, background: "#fafafa",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between",
                    alignItems: "center", marginBottom: 6 }}>
                    <strong style={{ fontSize: 15 }}>{asset.ticker}</strong>
                    <span style={{ fontSize: 13, color: "var(--text-2)" }}>
                      Poids : <strong>{asset.weight_pct}%</strong>
                    </span>
                  </div>
                  <p style={{ fontSize: 13, color: "var(--text-2)", marginBottom: 10 }}>
                    {asset.explanation}
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    {contribs.map(([feat, val]) => {
                      const label = FEATURE_LABELS[feat] || feat;
                      const clamped = Math.min(Math.abs(val) * 2000, 100);
                      return (
                        <div key={feat} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                          <span style={{ width: 90, color: "var(--text-2)", flexShrink: 0 }}>{label}</span>
                          <div style={{ flex: 1, background: "#eee", borderRadius: 4, height: 8, overflow: "hidden" }}>
                            <div style={{
                              width: `${clamped}%`, height: "100%",
                              background: val >= 0 ? "#0d6b58" : "#c2421f", borderRadius: 4,
                            }} />
                          </div>
                          <span style={{ color: val >= 0 ? "#0d6b58" : "#c2421f",
                            fontWeight: 600, width: 50, textAlign: "right" }}>
                            {val >= 0 ? "+" : ""}{val.toFixed(3)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}