import React, { useState, useEffect } from "react";
import { api } from "../api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Risk() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.risk().then(setData);
  }, []);

  if (!data) return <div className="loading">Analyse du risque de votre portefeuille...</div>;

  return (
    <>
      <h1>Mon risque</h1>
      <p className="subtitle">La question que tout investisseur se pose : combien puis-je perdre ?</p>

      {/* ─── 1. LES PIRES JOURNÉES (AJOUT CORNISH-FISHER) ─── */}
      <div className="grid-3">
        <div className="card metric">
          <div className="metric-label">Mauvaise journée (cas typique)</div>
          <div className="metric-value negative">
            −{data.var_eur.toLocaleString("fr-FR")} €
          </div>
          <div className="metric-sub">
            VaR 95% : dans 95% des cas, votre perte quotidienne ne dépassera
            pas ce montant ({data.var_pct}%)
          </div>
        </div>
        <div className="card metric">
          <div className="metric-label">Choc Extrême (Cornish-Fisher)</div>
          <div className="metric-value negative">
            −{data.var_cornish_fisher_95_eur.toLocaleString("fr-FR")} €
          </div>
          <div className="metric-sub">
            VaR Ajustée (95%) : calcul quantitatif qui prend en compte l'asymétrie des marchés ({data.var_cornish_fisher_95_pct}%)
          </div>
        </div>
        <div className="card metric">
          <div className="metric-label">Pire crise traversée (2015-2024)</div>
          <div className="metric-value negative">
            −{data.max_dd_eur.toLocaleString("fr-FR")} €
          </div>
          <div className="metric-sub">
            Maximum Drawdown : la pire chute depuis un sommet ({data.max_dd_pct}%)
          </div>
        </div>
      </div>

      <div className="alert alert-success">
        💬 <strong>En clair :</strong> sur une journée normale, votre portefeuille
        ne devrait pas perdre plus de {data.var_eur.toLocaleString("fr-FR")} €.
        Cependant, nos modèles de chocs extrêmes estiment le risque réel à {data.var_cornish_fisher_95_eur.toLocaleString("fr-FR")} €.
      </div>

      {/* ─── 2. GRAPHIQUE DES CHUTES (NOUVEAU) ─── */}
      <div className="card">
        <h2>📉 L'historique de vos chutes (Underwater Chart)</h2>
        <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
          Ce graphique illustre la profondeur et la durée des périodes où votre portefeuille était "sous l'eau" par rapport à son sommet.
        </p>
        <div style={{ width: '100%', height: 250 }}>
          <ResponsiveContainer>
            <LineChart data={data.drawdown_series}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} vertical={false} />
              <XAxis dataKey="date" minTickGap={40} tick={{fontSize: 12}} />
              <YAxis tickFormatter={(val) => `${(val * 100).toFixed(0)}%`} tick={{fontSize: 12}} />
              <Tooltip 
                formatter={(value) => [`${(value * 100).toFixed(2)}%`, "Chute (Drawdown)"]} 
                labelStyle={{color: 'black'}} 
              />
              <Line type="monotone" dataKey="drawdown" stroke="#d90429" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ─── 3. QUALITÉ ET STABILITÉ (NOUVEAU) ─── */}
      <div className="card">
        <h2>⚖️ Qualité et Stabilité du portefeuille</h2>
        <div className="grid-3" style={{ marginTop: 16 }}>
          <div className="metric">
            <div className="metric-label">Ratio de Sortino</div>
            <div className="metric-value">{data.sortino_ratio}</div>
            <div className="metric-sub">Mesure la performance ajustée au risque de <strong>chute uniquement</strong>.</div>
          </div>
          <div className="metric">
            <div className="metric-label">Ratio de Calmar</div>
            <div className="metric-value">{data.calmar_ratio}</div>
            <div className="metric-sub">Compare le rendement annuel face au <strong>Maximum Drawdown</strong>.</div>
          </div>
          <div className="metric">
            <div className="metric-label">Ulcer Index</div>
            <div className="metric-value">{data.ulcer_index}</div>
            <div className="metric-sub">Indice de "douleur" : pénalise les longues périodes dans le rouge.</div>
          </div>
        </div>
      </div>

      {/* ─── 4. TABLEAU DES CRISES (EXISTANT) ─── */}
      <div className="card">
        <h2>Et si une crise éclatait demain ?</h2>
        <p className="caption" style={{ marginTop: 0, marginBottom: 16 }}>
          Nous rejouons les grandes crises historiques sur VOTRE portefeuille.
        </p>
        <table>
          <thead>
            <tr>
              <th>Scénario de crise</th>
              <th>Performance</th>
              <th>Pire chute</th>
              <th>Impact sur capital</th>
            </tr>
          </thead>
          <tbody>
            {data.stress_tests.map((s) => (
              <tr key={s.crise}>
                <td><strong>{s.crise}</strong></td>
                <td className="num" style={{ color: "var(--red)" }}>{s.rendement}</td>
                <td className="num">{s.drawdown}</td>
                <td className="num" style={{ color: "var(--red)" }}>
                  {s.impact_eur.toLocaleString("fr-FR")} €
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ─── 5. VALIDATION SCIENTIFIQUE (AMÉLIORÉ) ─── */}
      <div className="card">
        <h2>🔬 Profil Quantitatif & Validation</h2>
        <p style={{ color: "var(--text-2)", marginBottom: 14 }}>
          Nos modèles analysent la "forme" mathématique de vos rendements pour s'assurer que nos calculs de risques sont parfaitement adaptés.
        </p>
        
        {/* Badges Statistiques */}
        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "16px" }}>
          <span className="badge" style={{ background: "#f1f5f9", color: "#475569", border: "1px solid #cbd5e1" }}>
            📊 Skewness (Asymétrie) : {data.skewness}
          </span>
          <span className="badge" style={{ background: "#f1f5f9", color: "#475569", border: "1px solid #cbd5e1" }}>
            🏔️ Kurtosis (Queues épaisses) : {data.kurtosis}
          </span>
        </div>
        
        {/* Badges de Tests */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {data.kupiec_valide ? (
            <span className="badge badge-green">
              ✅ Modèle de prédiction des pertes validé (Test de Kupiec : {data.kupiec_pvalue})
            </span>
          ) : (
            <span className="badge badge-amber">
              ⚠️ Modèle de pertes en cours de recalibration (Test de Kupiec)
            </span>
          )}

          {!data.jarque_bera.is_normal ? (
            <span className="badge badge-green">
              ✅ Marchés non-normaux détectés (Test Jarque-Bera : {data.jarque_bera.p_value}). Utilisation des modèles extrêmes activée.
            </span>
          ) : (
            <span className="badge badge-amber">
              ℹ️ Distribution classique (Test Jarque-Bera).
            </span>
          )}
        </div>
      </div>
    </>
  );
}