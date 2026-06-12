import React, { useState, useEffect } from "react";
import { api } from "../api";

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
          <div className="metric-label">Très mauvaise journée (pire 5%)</div>
          <div className="metric-value negative">
            −{data.cvar_eur.toLocaleString("fr-FR")} €
          </div>
          <div className="metric-sub">
            CVaR : perte moyenne dans les 5% des pires journées ({data.cvar_pct}%)
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
        Lors de la pire crise de la décennie (COVID, mars 2020), il aurait
        temporairement perdu {data.max_dd_eur.toLocaleString("fr-FR")} € avant
        de se redresser.
      </div>

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
              <th>Impact sur votre capital</th>
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

      <div className="card">
        <h2>🔬 Validation scientifique</h2>
        <p style={{ color: "var(--text-2)", marginBottom: 14 }}>
          Nous ne nous contentons pas de calculer le risque — nous vérifions
          que nos modèles sont fiables. Le test statistique de Kupiec compare
          nos prédictions de pertes avec la réalité observée.
        </p>
        {data.kupiec_valide ? (
          <span className="badge badge-green">
            ✅ Modèle de risque statistiquement validé (p-value : {data.kupiec_pvalue})
          </span>
        ) : (
          <span className="badge badge-amber">
            ⚠️ Modèle en cours de recalibration
          </span>
        )}
      </div>
    </>
  );
}
