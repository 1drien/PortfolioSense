# dashboard/page0_accueil.py
# Onboarding utilisateur — expérience SaaS
# L'utilisateur définit son profil en 3 questions simples

import streamlit as st


def render():
    st.title("Bienvenue sur PortfolioSense 👋")

    st.markdown(
        """
        ##### Les stratégies des grands fonds d'investissement, enfin accessibles.

        Répondez à **3 questions** et obtenez un portefeuille optimisé
        mathématiquement, surveillé en temps réel, et **expliqué en langage clair**.
        """
    )

    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("1️⃣ Votre capital")
        capital = st.number_input(
            "Combien souhaitez-vous investir ?",
            min_value=1_000,
            max_value=1_000_000,
            value=st.session_state.get("capital", 10_000),
            step=1_000,
            format="%d",
            help="Le montant total que vous êtes prêt à investir en bourse",
        )

        st.subheader("2️⃣ Votre horizon")
        horizon = st.slider(
            "Sur combien d'années investissez-vous ?",
            min_value=1, max_value=20,
            value=st.session_state.get("horizon", 5),
            help="Plus l'horizon est long, plus vous pouvez supporter les fluctuations",
        )

    with col2:
        st.subheader("3️⃣ Votre tolérance au risque")
        perte_max = st.slider(
            "Quelle perte maximale pouvez-vous supporter sans paniquer ?",
            min_value=5, max_value=50,
            value=st.session_state.get("perte_max", 15),
            format="%d%%",
            help="Soyez honnête : en mars 2020, les marchés ont perdu 30% en un mois",
        )

        # ── Déduction automatique du profil ──
        if perte_max <= 10:
            profil, emoji, desc = "conservateur", "🟢", (
                "Vous privilégiez la **stabilité**. Votre portefeuille sera "
                "construit pour minimiser les fluctuations, quitte à viser "
                "un rendement plus modeste."
            )
        elif perte_max <= 25:
            profil, emoji, desc = "equilibre", "🟡", (
                "Vous cherchez le **juste milieu**. Chaque actif de votre "
                "portefeuille contribuera de manière égale au risque total — "
                "la stratégie des plus grands fonds mondiaux."
            )
        else:
            profil, emoji, desc = "agressif", "🔴", (
                "Vous visez la **performance**. Votre portefeuille maximisera "
                "le rendement par unité de risque, en acceptant des "
                "fluctuations plus importantes."
            )

        st.divider()
        st.markdown(f"### Votre profil : {emoji} **{profil.capitalize()}**")
        st.markdown(desc)

    st.divider()

    # ── Validation ──
    if st.button("🚀 Construire mon portefeuille", type="primary", use_container_width=True):
        st.session_state["capital"]   = capital
        st.session_state["horizon"]   = horizon
        st.session_state["perte_max"] = perte_max
        st.session_state["profil"]    = profil
        st.session_state["onboarded"] = True
        st.success(
            "Profil enregistré ! Rendez-vous dans **💼 Mon portefeuille** "
            "(menu de gauche) pour découvrir votre allocation optimale."
        )
        st.balloons()
