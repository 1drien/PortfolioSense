import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

function deduceProfil(perteMax) {
  if (perteMax <= 10)
    return {
      id: "conservateur",
      emoji: "🟢",
      label: "Conservateur",
      desc: "Vous privilégiez la stabilité. Votre portefeuille minimisera les fluctuations, quitte à viser un rendement plus modeste.",
    };
  if (perteMax <= 25)
    return {
      id: "equilibre",
      emoji: "🟡",
      label: "Équilibré",
      desc: "Vous cherchez le juste milieu. Chaque actif contribuera de manière égale au risque total — la stratégie des plus grands fonds mondiaux.",
    };
  return {
    id: "agressif",
    emoji: "🔴",
    label: "Agressif",
    desc: "Vous visez la performance. Votre portefeuille maximisera le rendement par unité de risque, en acceptant des fluctuations importantes.",
  };
}

export default function Onboarding() {
  const [capital, setCapital] = useState(10000);
  const [horizon, setHorizon] = useState(5);
  const [perteMax, setPerteMax] = useState(15);
  const [saved, setSaved] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.getProfile().then((p) => {
      if (p) {
        setCapital(p.capital);
        setHorizon(p.horizon);
        setPerteMax(p.perte_max);
      }
    });
  }, []);

  const profil = deduceProfil(perteMax);

  async function save() {
    await api.saveProfile({ capital, horizon, perte_max: perteMax });
    setSaved(true);
    setTimeout(() => navigate("/portefeuille"), 900);
  }

  return (
    <>
      <h1>Mon profil d'investisseur</h1>
      <p className="subtitle">
        3 questions pour construire votre portefeuille sur mesure.
      </p>

      <div className="grid-2">
        <div className="card">
          <div className="field">
            <label>1. Combien souhaitez-vous investir ?</label>
            <input
              type="number"
              value={capital}
              min={1000}
              step={1000}
              onChange={(e) => setCapital(Number(e.target.value))}
            />
            <div className="hint">Montant total à investir en bourse</div>
          </div>

          <div className="field">
            <label>2. Sur combien d'années ? — {horizon} ans</label>
            <input
              type="range"
              min={1}
              max={20}
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
            />
            <div className="hint">
              Plus l'horizon est long, plus vous pouvez supporter les fluctuations
            </div>
          </div>

          <div className="field">
            <label>
              3. Perte maximale supportable sans paniquer ? — {perteMax}%
            </label>
            <input
              type="range"
              min={5}
              max={50}
              value={perteMax}
              onChange={(e) => setPerteMax(Number(e.target.value))}
            />
            <div className="hint">
              Soyez honnête : en mars 2020, les marchés ont perdu 30% en un mois
            </div>
          </div>
        </div>

        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <h2>Votre profil</h2>
          <div style={{ fontSize: 44, marginBottom: 8 }}>{profil.emoji}</div>
          <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 10 }}>
            {profil.label}
          </div>
          <p style={{ color: "var(--text-2)", flex: 1 }}>{profil.desc}</p>

          {saved ? (
            <div className="alert alert-success" style={{ marginBottom: 0 }}>
              ✅ Profil enregistré ! Redirection...
            </div>
          ) : (
            <button className="btn btn-primary btn-block" onClick={save}>
              🚀 Construire mon portefeuille
            </button>
          )}
        </div>
      </div>
    </>
  );
}
