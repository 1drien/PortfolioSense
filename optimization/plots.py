import plotly.graph_objects as go
import sys
sys.path.insert(0, '.')
from optimization.optimizer import (
    efficient_frontier_curve, max_sharpe, min_variance, risk_parity
)
from config import RISK_FREE_RATE

def plot_efficient_frontier(returns, n_portfolios=2000):
    """Retourne une figure Plotly — usage : st.plotly_chart(fig)"""
    curve = efficient_frontier_curve(returns, n_portfolios)
    ms = max_sharpe(returns)["metrics"]
    mv = min_variance(returns)["metrics"]
    rp = risk_parity(returns)["metrics"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=curve["volatility"] * 100,
        y=curve["return"] * 100,
        mode="markers",
        marker=dict(size=3, opacity=0.4,
                    color=curve["sharpe"],
                    colorscale="Viridis",
                    colorbar=dict(title="Sharpe")),
        name="Portefeuilles simulés",
        hovertemplate="Vol: %{x:.1f}%<br>Rdt: %{y:.1f}%<extra></extra>",
    ))
    for label, m, color, symbol in [
        ("Max Sharpe",   ms, "red",   "star"),
        ("Min Variance", mv, "blue",  "diamond"),
        ("Risk Parity",  rp, "green", "circle"),
    ]:
        fig.add_trace(go.Scatter(
            x=[m["volatility"] * 100],
            y=[m["return"] * 100],
            mode="markers+text",
            marker=dict(size=14, color=color, symbol=symbol),
            text=[f"{label} | Sharpe: {m['sharpe']:.2f}"],
            textposition="top center",
            name=label,
        ))
    fig.update_layout(
        title="Frontière efficiente — PortfolioSense",
        xaxis_title="Volatilité annualisée (%)",
        yaxis_title="Rendement annualisé (%)",
        height=500,
        template="plotly_white",
    )
    return fig
