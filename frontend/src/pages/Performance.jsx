import React, { useState, useEffect } from "react";
import { api } from "../api";

export default function Performance() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.backtest().then(setData);
  }, []);

  if (!data)
    return (
      <div className="loading">
        Chargement du backtest walk-forward (peut prendre une minute la
        première fois)...
      </div>
    );

  const best = data.results.reduce((a, b) =>
    a.valeur_finale > b.valeur_finale ? a : b
  );

  return (
    <>
      <h1>Performance prouvée</h1>
      <p className="subtitle">
        Pas de promesses en l'air : nous testons nos stratégies comme un vrai
        investisseur les aurait vécues — sans jamais connaître l'avenir.
      </p>

      <div className="card">
        <h2>🔬 Méthodologie walk-forward</h2>
        <p style={{ color: "var(--text-2)" }}>
          À chaque période de 6 mois, nous optimisons le portefeuille en
          utilisant <strong>uniquement les 2 années précédentes</strong> —
          exactement comme un investisseur réel. Cette méthode élimine le biais
          de lucidité rétrospective qui rend la plupart des backtests trop
          optimistes.
        </p>
      </div>

      <div className="card">
        <h2>
          {data.capital.toLocaleString("fr-FR")} € investis en 2017 seraient
          devenus...
        </h2>
        <table>
          <thead>
            <tr>
              <th>Stratégie</th>
              <th>Rendement / an</th>
              <th>Sharpe</th>
              <th>Pire chute</th>
              <th>Valeur finale (2024)</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((r) => (
              <tr key={r.strategie}>
                <td>
                  <strong>{r.strategie}</strong>
                  {r.strategie === best.strategie && (
                    <span className="badge badge-green" style={{ marginLeft: 8 }}>
                      🏆 Meilleur gain
                    </span>
                  )}
                </td>
                <td className="num" style={{ color: "var(--accent)" }}>
                  +{r.rendement_ann}%
                </td>
                <td className="num">{r.sharpe}</td>
                <td className="num" style={{ color: "var(--red)" }}>
                  {r.max_dd}%
                </td>
                <td className="num" style={{ fontSize: 16 }}>
                  {r.valeur_finale.toLocaleString("fr-FR")} €
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="alert alert-warning">
        💬 <strong>Honnêteté scientifique :</strong> la stratégie naïve
        equal-weight est réputée difficile à battre en ratio de Sharpe
        (DeMiguel et al., 2009). Notre valeur ajoutée n'est pas de la battre
        systématiquement, mais d'adapter la stratégie à VOTRE profil : Max
        Sharpe maximise le gain absolu, Min Variance minimise les chutes en
        période de crise.
      </div>
    </>
  );
}
