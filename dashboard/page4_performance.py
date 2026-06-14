# ============================================================
#  PortfolioSense — Page 4 : Données & Performance
#  Module data/ — Anas Daunes
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="Données & Performance — PortfolioSense",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS Custom ────────────────────────────────────────────
st.markdown("""
<style>
    /* Fond général */
    .stApp { background-color: #F6F8FA; color: #1C1C1A; }
    
    /* Header hero */
    .hero {
        background: linear-gradient(135deg, #1a3a5c 0%, #185FA5 100%);
        border: none;
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        color: #58A6FF;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #5F5E5A;
        margin-top: 0.3rem;
    }
    
    /* KPI cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E0DED8;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #58A6FF; }
    .kpi-label {
        font-size: 0.72rem;
        color: #5F5E5A;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1C1C1A;
        font-family: monospace;
    }
    .kpi-value.green { color: #3FB950; }
    .kpi-value.blue  { color: #58A6FF; }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #E0DED8;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #5F5E5A;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background: #1F6FEB !important;
        color: white !important;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1C1C1A;
        border-left: 3px solid #58A6FF;
        padding-left: 0.75rem;
        margin: 1.2rem 0 0.8rem 0;
    }
    
    /* Insight cards */
    .insight-card {
        background: #FFFFFF;
        border: 1px solid #E0DED8;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .insight-card.green { border-left: 3px solid #3FB950; }
    .insight-card.red   { border-left: 3px solid #F85149; }
    .insight-card.blue  { border-left: 3px solid #58A6FF; }
    .insight-card.amber { border-left: 3px solid #D29922; }
    .insight-title { font-size: 0.82rem; font-weight: 600; color: #1C1C1A; margin-bottom: 0.2rem; }
    .insight-text  { font-size: 0.78rem; color: #5F5E5A; }
    
    /* Badge */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-green  { background: #1A3A22; color: #3FB950; }
    .badge-red    { background: #3A1A1A; color: #F85149; }
    .badge-blue   { background: #1A2A3A; color: #58A6FF; }
    .badge-amber  { background: #3A2A0A; color: #D29922; }
    
    /* Metric override */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E0DED8;
        border-radius: 8px;
        padding: 0.8rem 1rem;
    }
    [data-testid="stMetricLabel"] { color: #5F5E5A !important; font-size: 0.75rem !important; }
    [data-testid="stMetricValue"] { color: #1C1C1A !important; font-size: 1.4rem !important; }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border-color: #E0DED8 !important;
        color: #1C1C1A !important;
    }
    
    /* Divider */
    hr { border-color: #E0DED8 !important; }
    
    /* Dataframe */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #B4B2A9;
        font-size: 0.75rem;
        padding: 1.5rem 0 0.5rem;
        border-top: 1px solid #21262D;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Chemins ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def path(f): return os.path.join(DATA_DIR, f)

# ── Chargement ────────────────────────────────────────────
@st.cache_data
def load(file, index=0, parse_dates=False):
    p = path(file)
    if not os.path.exists(p): return None
    return pd.read_csv(p, index_col=index, parse_dates=parse_dates)

returns     = load("returns_clean.csv", parse_dates=True)
dd_df       = load("drawdown_historique.csv")
attr_df     = load("attribution_actifs.csv")
sect_df     = load("attribution_secteurs.csv")
period_df   = load("attribution_periodes.csv")
covid_df    = load("stress_covid2020.csv")
rates_df    = load("stress_rates2022.csv")
gfc_df      = load("stress_gfc2008.csv")

# ── Données secteurs ──────────────────────────────────────
SECTEURS = {
    "AAPL":"Tech","MSFT":"Tech","NVDA":"Tech","GOOGL":"Tech","META":"Tech",
    "AMD":"Tech","INTC":"Tech","CRM":"Tech",
    "JPM":"Finance","BAC":"Finance","GS":"Finance","BLK":"Finance","MS":"Finance","AXP":"Finance",
    "JNJ":"Santé","UNH":"Santé","PFE":"Santé","ABBV":"Santé","MRK":"Santé","LLY":"Santé",
    "AMZN":"Conso.disc","TSLA":"Conso.disc","HD":"Conso.disc","NKE":"Conso.disc",
    "PG":"Conso.base","KO":"Conso.base","WMT":"Conso.base",
    "XOM":"Énergie","CVX":"Énergie",
    "CAT":"Industrie","BA":"Industrie","HON":"Industrie","UPS":"Industrie",
    "PLD":"Immobilier","NEE":"Collectivités",
}
COLORS = {
    "Tech":"#1F6FEB","Finance":"#8957E5","Santé":"#3FB950",
    "Conso.disc":"#F85149","Conso.base":"#6E7681",
    "Énergie":"#D29922","Industrie":"#79C0FF","Immobilier":"#56D364","Collectivités":"#FFA657",
}

PLOT_BG = "#FFFFFF"
PLOT_PAPER = "#FFFFFF"
GRID_COLOR = "#F0EEE8"
TEXT_COLOR = "#5F5E5A"
ACCENT = "#58A6FF"

def dark_layout(fig, h=420, title=None):
    fig.update_layout(
        height=h,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_PAPER,
        font=dict(color=TEXT_COLOR, size=11),
        title=dict(text=title, font=dict(color="#1C1C1A", size=13)) if title else None,
        margin=dict(l=10, r=10, t=40 if title else 20, b=10),
        legend=dict(bgcolor="#FFFFFF", bordercolor="#E0DED8", borderwidth=1, font=dict(size=10)),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR)),
    )
    return fig


# ════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-title">📊 Données & Performance</div>
    <div class="hero-sub">Pipeline de données · Statistiques · Stress Tests · Drawdown · Attribution — Module data/</div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────
ann = 252
rdt_moy = returns.mean().mean() * ann * 100
vol_moy = returns.std().mean() * np.sqrt(ann) * 100

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Actifs S&P 500</div>
        <div class="kpi-value blue">{returns.shape[1]}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Jours de données</div>
        <div class="kpi-value">{returns.shape[0]:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Période</div>
        <div class="kpi-value blue">{returns.index[0].year}–{returns.index[-1].year}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Valeurs manquantes</div>
        <div class="kpi-value green">0</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Rdt annualisé moy.</div>
        <div class="kpi-value green">+{rdt_moy:.1f}%</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── ONGLETS ───────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Statistiques",
    "🔗 Corrélations",
    "📉 Drawdown",
    "🚨 Stress Tests",
    "🏆 Attribution"
])


# ════════════════════════════════════════════════
# TAB 1 — STATISTIQUES
# ════════════════════════════════════════════════
with tab1:
    stats = pd.DataFrame({
        "Secteur": [SECTEURS.get(t,"Autre") for t in returns.columns],
        "Rdt annualisé (%)": (returns.mean()*ann*100).round(2),
        "Volatilité (%)": (returns.std()*np.sqrt(ann)*100).round(2),
        "Sharpe": (returns.mean()*ann/(returns.std()*np.sqrt(ann))).round(2),
        "Skewness": returns.skew().round(3),
        "Kurtosis": returns.kurtosis().round(3),
    }, index=returns.columns)

    col_left, col_right = st.columns([1, 3])

    with col_left:
        st.markdown('<div class="section-header">Filtres</div>', unsafe_allow_html=True)
        secteur_sel = st.selectbox("Secteur", ["Tous"] + sorted(stats["Secteur"].unique()))
        sort_by = st.selectbox("Trier par", ["Rdt annualisé (%)", "Sharpe", "Volatilité (%)"])
        ascending = st.toggle("Ordre croissant", value=False)

        st.markdown('<div class="section-header">Résumé</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="insight-card green">
    <div class="insight-title">Meilleur Sharpe</div>
    <div class="insight-text">NVDA — 1.17</div>
</div>
<div class="insight-card red">
    <div class="insight-title">Seul actif négatif</div>
    <div class="insight-text">INTC — -3.43%/an</div>
</div>
<div class="insight-card blue">
    <div class="insight-title">Plus volatile</div>
    <div class="insight-text">TSLA — 57.01%</div>
</div>
<div class="insight-card amber">
    <div class="insight-title">Fat tails</div>
    <div class="insight-text">META kurtosis 27.7</div>
</div>
""", unsafe_allow_html=True)

    with col_right:
        filtered = stats if secteur_sel == "Tous" else stats[stats["Secteur"] == secteur_sel]
        filtered = filtered.sort_values(sort_by, ascending=ascending)

        st.markdown('<div class="section-header">Tableau des actifs</div>', unsafe_allow_html=True)

        def style_df(df):
            def color_rdt(v):
                if isinstance(v, float):
                    return f"color: {'#3FB950' if v > 0 else '#F85149'}; font-weight: 600"
                return ""
            def color_sharpe(v):
                if isinstance(v, float):
                    if v >= 0.8: return "color: #3FB950; font-weight: 600"
                    if v >= 0.5: return "color: #D29922"
                    return "color: #F85149"
                return ""
            return df.style\
                .map(color_rdt, subset=["Rdt annualisé (%)"])\
                .map(color_sharpe, subset=["Sharpe"])

        st.dataframe(style_df(filtered), use_container_width=True, height=400)

        st.markdown('<div class="section-header">Carte Risque / Rendement</div>', unsafe_allow_html=True)
        fig = px.scatter(
            stats.reset_index().rename(columns={"index":"Actif"}),
            x="Volatilité (%)", y="Rdt annualisé (%)",
            text="Actif", color="Secteur",
            size=stats["Sharpe"].clip(lower=0.01).values,
            color_discrete_map=COLORS,
            hover_data={"Sharpe":True, "Kurtosis":True},
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#B4B2A9", opacity=0.8)
        fig.update_traces(textposition="top center", textfont_size=8, textfont_color="#8B949E")
        dark_layout(fig, h=460, title="Rendement annualisé vs Volatilité — taille = Sharpe")
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════
# TAB 2 — CORRÉLATIONS
# ════════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns([3, 1])

    with col_a:
        st.markdown('<div class="section-header">Matrice de corrélation</div>', unsafe_allow_html=True)
        corr = returns.corr()
        fig = px.imshow(
            corr, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            aspect="auto",
            color_continuous_midpoint=0,
        )
        fig.update_coloraxes(colorbar=dict(
            tickfont=dict(color=TEXT_COLOR),
            title=dict(text="Corr.", font=dict(color=TEXT_COLOR))
        ))
        dark_layout(fig, h=560, title="Corrélations 2015–2024")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Stats</div>', unsafe_allow_html=True)
        corr_vals = corr.where(lambda x: x < 1).stack()
        st.metric("Corrélation moy.", f"{corr_vals.mean():.3f}")
        st.metric("Max", f"{corr_vals.max():.3f}")
        st.metric("Min", f"{corr_vals.min():.3f}")

        st.markdown("""
<div style="margin-top: 1rem;">
<div class="insight-card red">
    <div class="insight-title">⚠ COVID 2020</div>
    <div class="insight-text">Corrélation moy. → <strong style="color:#F85149">0.714</strong><br>Diversification quasi nulle</div>
</div>
<div class="insight-card amber">
    <div class="insight-title">Taux 2022</div>
    <div class="insight-text">Corrélation moy. → <strong style="color:#D29922">0.426</strong><br>Diversification partielle</div>
</div>
<div class="insight-card green">
    <div class="insight-title">Normale</div>
    <div class="insight-text">Corrélation moy. → <strong style="color:#3FB950">~0.40</strong><br>Diversification efficace</div>
</div>
<div class="insight-card blue" style="margin-top:1rem;">
    <div class="insight-title">💡 Pourquoi le HMM ?</div>
    <div class="insight-text">Les corrélations ne sont pas stables. Elles explosent en crise → l'allocation doit s'adapter dynamiquement.</div>
</div>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="section-header">Corrélation glissante — 60 jours</div>', unsafe_allow_html=True)

    col_x, col_y, col_w = st.columns([2, 2, 1])
    a1 = col_x.selectbox("Actif 1", returns.columns.tolist(), index=0, key="rc1")
    a2 = col_y.selectbox("Actif 2", returns.columns.tolist(), index=1, key="rc2")
    window = col_w.selectbox("Fenêtre", [30, 60, 90, 120], index=1)

    if a1 != a2:
        rc = returns[a1].rolling(window).corr(returns[a2])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=rc.index, y=rc.values, mode="lines",
            name=f"{a1}/{a2}",
            line=dict(color=ACCENT, width=1.5),
            fill="tozeroy",
            fillcolor="rgba(88,166,255,0.06)"
        ))
        fig2.add_hline(y=rc.mean(), line_dash="dash", line_color="#B4B2A9",
                       annotation_text=f"Moy: {rc.mean():.2f}",
                       annotation_font_color=TEXT_COLOR)
        for xr, label, col in [
            ("2020-02-01","2020-04-30","COVID"),
            ("2022-01-01","2022-12-31","Taux 2022"),
            ("2008-01-01","2009-06-30","GFC 2008"),
        ]:
            if xr >= str(returns.index[0].date()):
                fig2.add_vrect(x0=xr, x1=label if label=="2020-04-30" else ("2022-12-31" if "2022" in xr else "2009-06-30"),
                               fillcolor="#F85149", opacity=0.07,
                               annotation_text=col, annotation_font_color="#F85149",
                               annotation_position="top left")
        fig2.add_hline(y=0, line_color="#B4B2A9", line_width=0.5)
        dark_layout(fig2, h=360, title=f"Corrélation glissante {window}j — {a1} / {a2}")
        fig2.update_yaxes(range=[-1, 1])
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Sélectionne deux actifs différents.")


# ════════════════════════════════════════════════
# TAB 3 — DRAWDOWN
# ════════════════════════════════════════════════
with tab3:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        if dd_df is not None:
            st.markdown('<div class="section-header">Maximum Drawdown par actif</div>', unsafe_allow_html=True)
            dd_plot = dd_df[["Max Drawdown (%)"]].copy()
            dd_plot["Statut"] = dd_df["Statut"]
            dd_plot = dd_plot.sort_values("Max Drawdown (%)")
            colors_dd = ["#F85149" if s=="Pas encore recupere" else ACCENT for s in dd_plot["Statut"]]

            fig = go.Figure(go.Bar(
                x=dd_plot["Max Drawdown (%)"], y=dd_plot.index,
                orientation="h", marker_color=colors_dd,
                text=dd_plot["Max Drawdown (%)"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside", textfont=dict(color=TEXT_COLOR, size=9)
            ))
            dark_layout(fig, h=580, title="Maximum Drawdown 2015–2024")
            fig.update_xaxes(range=[-90, 5])
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Actifs non récupérés</div>', unsafe_allow_html=True)
        if dd_df is not None:
            non_rec = dd_df[dd_df["Statut"]=="Pas encore recupere"][
                ["Max Drawdown (%)","Date Creux","Duree Chute (jours)"]
            ].sort_values("Max Drawdown (%)")
            for ticker, row in non_rec.iterrows():
                st.markdown(f"""
<div class="insight-card red">
    <div class="insight-title">{ticker} <span class="badge badge-red">Non récupéré</span></div>
    <div class="insight-text">Max DD: <strong style="color:#F85149">{row['Max Drawdown (%)']:.1f}%</strong> · Creux: {row['Date Creux']}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">Stats globales</div>', unsafe_allow_html=True)
        if dd_df is not None:
            st.metric("Pire drawdown", f"{dd_df['Max Drawdown (%)'].min():.1f}% (BA)")
            st.metric("Drawdown moyen", f"{dd_df['Max Drawdown (%)'].mean():.1f}%")
            non_count = (dd_df["Statut"]=="Pas encore recupere").sum()
            st.metric("Non récupérés", f"{non_count} / {len(dd_df)}")

    st.divider()
    st.markdown('<div class="section-header">Évolution temporelle — Sélectionne un actif</div>', unsafe_allow_html=True)

    actif_sel = st.selectbox("Actif", returns.columns.tolist(), key="dd_actif")
    prices = np.exp(returns[actif_sel].cumsum()) * 100
    rolling_max = prices.cummax()
    dd_serie = (prices - rolling_max) / rolling_max * 100

    fig_dd = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           row_heights=[0.6, 0.4], vertical_spacing=0.04,
                           subplot_titles=[f"Prix reconstitué — {actif_sel}", "Drawdown (%)"])

    fig_dd.add_trace(go.Scatter(x=prices.index, y=prices.values,
                                name="Prix", line=dict(color=ACCENT, width=1.5)), row=1, col=1)
    fig_dd.add_trace(go.Scatter(x=rolling_max.index, y=rolling_max.values,
                                name="Pic", line=dict(color="#3FB950", width=1, dash="dot")), row=1, col=1)
    fig_dd.add_trace(go.Scatter(x=dd_serie.index, y=dd_serie.values,
                                fill="tozeroy", name="Drawdown",
                                line=dict(color="#F85149", width=1),
                                fillcolor="rgba(248,81,73,0.15)"), row=2, col=1)

    fig_dd.update_layout(
        height=480, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_PAPER,
        font=dict(color=TEXT_COLOR), margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor="#FFFFFF", bordercolor="#E0DED8", borderwidth=1),
    )
    for ax in ["xaxis","xaxis2","yaxis","yaxis2"]:
        fig_dd.update_layout(**{ax: dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)})
    st.plotly_chart(fig_dd, use_container_width=True)


# ════════════════════════════════════════════════
# TAB 4 — STRESS TESTS
# ════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Comportement du portefeuille en période de crise</div>', unsafe_allow_html=True)

    CRISES = {
        "🦠  COVID 2020": {
            "df": covid_df,
            "desc": "Fév. 2020 → Avr. 2020 · Krach éclair 62 jours · S&P 500 : -34%",
            "color": "#F85149", "badge": "badge-red",
            "corr": "0.714", "insight": "Diversification quasi nulle — toutes les actions chutent ensemble"
        },
        "📈  Taux 2022": {
            "df": rates_df,
            "desc": "Jan. 2022 → Déc. 2022 · Fed 0% → 5.25% · Tech massacrée",
            "color": "#D29922", "badge": "badge-amber",
            "corr": "0.426", "insight": "Rotation sectorielle — Tech -50%+, Énergie +87%"
        },
        "🏦  GFC 2008": {
            "df": gfc_df,
            "desc": "Jan. 2008 → Juin 2009 · Crise des subprimes · Lehman Brothers",
            "color": "#8957E5", "badge": "badge-blue",
            "corr": "0.563", "insight": "Banques dévastées — BAC -92%, MS -82%"
        },
    }

    crise = st.radio("", list(CRISES.keys()), horizontal=True, label_visibility="collapsed")
    info = CRISES[crise]
    df_s = info["df"]

    st.markdown(f"""
<div class="insight-card" style="border-left: 3px solid {info['color']}; margin-bottom: 1rem;">
    <div class="insight-title">{crise.strip()}</div>
    <div class="insight-text">{info['desc']} &nbsp;·&nbsp; Corrélation moy. : <strong style="color:{info['color']}">{info['corr']}</strong></div>
    <div class="insight-text" style="margin-top:4px; color: #1C1C1A;">{info['insight']}</div>
</div>
""", unsafe_allow_html=True)

    if df_s is not None and "Rendement cumulé (%)" in df_s.columns:
        c1, c2, c3 = st.columns(3)
        c1.metric("Rendement moyen", f"{df_s['Rendement cumulé (%)'].mean():.1f}%")
        if "Volatilité annualisée (%)" in df_s.columns:
            c2.metric("Volatilité moy.", f"{df_s['Volatilité annualisée (%)'].mean():.1f}%")
        if "Pire jour (%)" in df_s.columns:
            c3.metric("Pire journée", f"{df_s['Pire jour (%)'].min():.1f}%")

        col_g, col_p = st.columns(2)

        top5 = df_s["Rendement cumulé (%)"].nlargest(7)
        bot5 = df_s["Rendement cumulé (%)"].nsmallest(7)

        with col_g:
            st.markdown('<div class="section-header">🟢 Résistants</div>', unsafe_allow_html=True)
            fig_t = go.Figure(go.Bar(
                x=top5.values, y=top5.index, orientation="h",
                marker_color="#3FB950",
                text=[f"+{v:.1f}%" if v > 0 else f"{v:.1f}%" for v in top5.values],
                textposition="outside", textfont=dict(color="#3FB950", size=10)
            ))
            dark_layout(fig_t, h=300)
            fig_t.update_xaxes(range=[0, top5.max() * 1.3])
            st.plotly_chart(fig_t, use_container_width=True)

        with col_p:
            st.markdown('<div class="section-header">🔴 Perdants</div>', unsafe_allow_html=True)
            fig_b = go.Figure(go.Bar(
                x=bot5.values, y=bot5.index, orientation="h",
                marker_color="#F85149",
                text=[f"{v:.1f}%" for v in bot5.values],
                textposition="outside", textfont=dict(color="#F85149", size=10)
            ))
            dark_layout(fig_b, h=300)
            fig_b.update_xaxes(range=[bot5.min() * 1.3, 0])
            st.plotly_chart(fig_b, use_container_width=True)

        # Comparaison COVID vs 2022
        if covid_df is not None and rates_df is not None:
            st.divider()
            st.markdown('<div class="section-header">Comparaison COVID vs Taux 2022</div>', unsafe_allow_html=True)
            common = covid_df.index.intersection(rates_df.index)
            comp = pd.DataFrame({
                "COVID 2020": covid_df.loc[common, "Rendement cumulé (%)"],
                "Taux 2022": rates_df.loc[common, "Rendement cumulé (%)"],
            })
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(name="COVID 2020", x=comp.index, y=comp["COVID 2020"],
                                      marker_color="#F85149"))
            fig_comp.add_trace(go.Bar(name="Taux 2022", x=comp.index, y=comp["Taux 2022"],
                                      marker_color="#D29922"))
            fig_comp.update_layout(barmode="group")
            dark_layout(fig_comp, h=380, title="Rendement cumulé par actif — COVID vs Taux 2022")
            st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Données de stress tests non disponibles — lance d'abord `python data/stress_tests.py`")


# ════════════════════════════════════════════════
# TAB 5 — ATTRIBUTION
# ════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">Portefeuille équipondéré — 2015 à 2024</div>', unsafe_allow_html=True)

    if attr_df is not None:
        c1, c2, c3, c4 = st.columns(4)
        cum = attr_df["Contribution cumulée (%)"].sum()
        ann_rdt = attr_df["Contribution annualisée (%)"].sum()
        c1.metric("Rendement cumulé", f"+{cum:.0f}%")
        c2.metric("Rendement annualisé", f"+{ann_rdt:.2f}%")
        c3.metric("Actifs positifs", f"{(attr_df['Rendement annualisé actif (%)']>0).sum()} / {len(attr_df)}")
        c4.metric("Meilleur actif", "NVDA +56.6%/an")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-header">Top contributeurs</div>', unsafe_allow_html=True)
            top10 = attr_df["Contribution annualisée (%)"].nlargest(10)
            bot3  = attr_df["Contribution annualisée (%)"].nsmallest(3)
            combined = pd.concat([top10, bot3])
            bar_colors = ["#3FB950" if v > 0 else "#F85149" for v in combined.values]
            fig = go.Figure(go.Bar(
                x=combined.values, y=combined.index, orientation="h",
                marker_color=bar_colors,
                text=[f"{v:.3f}%" for v in combined.values],
                textposition="outside", textfont=dict(color=TEXT_COLOR, size=9)
            ))
            dark_layout(fig, h=400, title="Contribution annualisée au portefeuille (%)")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            if sect_df is not None:
                st.markdown('<div class="section-header">Contribution par secteur</div>', unsafe_allow_html=True)
                sect_reset = sect_df.reset_index()
                sect_col = sect_reset.columns[0]
                fig2 = px.pie(
                    sect_reset,
                    values="Contribution cumulée (%)",
                    names=sect_col,
                    color=sect_col,
                    color_discrete_map={
                        "Technologie":"#1F6FEB","Finance":"#8957E5","Santé":"#3FB950",
                        "Conso. discrétionnaire":"#F85149","Conso. de base":"#6E7681",
                        "Énergie":"#D29922","Industrie":"#79C0FF","Immobilier":"#56D364",
                        "Collectivités":"#FFA657"
                    },
                    hole=0.45,
                )
                fig2.update_layout(
                    height=400, paper_bgcolor=PLOT_BG,
                    font=dict(color=TEXT_COLOR),
                    legend=dict(bgcolor="#FFFFFF", bordercolor="#E0DED8", borderwidth=1, font=dict(size=10)),
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                fig2.update_traces(textfont_color="white")
                st.plotly_chart(fig2, use_container_width=True)

        # Périodes
        if period_df is not None:
            st.divider()
            st.markdown('<div class="section-header">Performance par période de marché</div>', unsafe_allow_html=True)
            period_colors = ["#1F6FEB", "#F85149", "#D29922", "#3FB950"]
            fig3 = make_subplots(rows=1, cols=3, subplot_titles=[
                "Rendement cumulé (%)", "Volatilité (%)", "Ratio de Sharpe"
            ])
            for col_i, metric in enumerate(["Rendement cumulé (%)", "Volatilité (%)", "Sharpe"], 1):
                if metric in period_df.columns:
                    fig3.add_trace(go.Bar(
                        x=period_df.index, y=period_df[metric],
                        marker_color=period_colors,
                        text=[f"{v:.2f}" for v in period_df[metric]],
                        textposition="outside",
                        textfont=dict(color=TEXT_COLOR, size=9),
                        showlegend=False
                    ), row=1, col=col_i)

            fig3.update_layout(
                height=380, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_PAPER,
                font=dict(color=TEXT_COLOR), margin=dict(l=10, r=10, t=40, b=10)
            )
            for ax in ["xaxis","xaxis2","xaxis3","yaxis","yaxis2","yaxis3"]:
                fig3.update_layout(**{ax: dict(gridcolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR))})
            st.plotly_chart(fig3, use_container_width=True)

        # Highlight NVDA
        st.markdown(f"""
<div class="insight-card blue" style="margin-top:1rem;">
    <div class="insight-title">⚡ NVDA — le cas extrême</div>
    <div class="insight-text">
        +28 357% sur 10 ans · Contribution cumulée : <strong style="color:{ACCENT}">810%</strong> sur {cum:.0f}% de rendement total du portefeuille équipondéré.<br>
        Dans un portefeuille équipondéré, NVDA est plafonné à 2.86%. L'optimisation Markowitz va naturellement le surpondérer — c'est la valeur ajoutée du module optimization/.
    </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("Lance d'abord `python data/attribution.py` pour générer les fichiers d'attribution.")

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Module data/ · Anas Daunes · PortfolioSense · CY Tech 2024–2025
</div>
""", unsafe_allow_html=True)