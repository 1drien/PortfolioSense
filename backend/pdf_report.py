# backend/pdf_report.py
# Génère le rapport PDF d'allocation personnalisé de l'utilisateur

import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

ACCENT = HexColor("#0d6b58")
TEXT   = HexColor("#14181f")
GRAY   = HexColor("#5a6472")
LIGHT  = HexColor("#e6f3f0")
RED    = HexColor("#c2421f")

PROFIL_LABELS = {
    "conservateur": "Conservateur — Minimum Variance",
    "equilibre":    "Équilibré — Risk Parity",
    "agressif":     "Agressif — Maximum Sharpe",
}


def build_pdf(profile: dict, portfolio: dict, risk: dict,
              explanations: list) -> bytes:
    """Construit le rapport PDF et retourne les bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=TEXT,
                        fontSize=20, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=GRAY,
                         fontSize=10, spaceAfter=12)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=ACCENT,
                        fontSize=13, spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("body", parent=styles["Normal"], textColor=TEXT,
                          fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=styles["Normal"], textColor=GRAY,
                           fontSize=8, leading=11)

    elems = []

    # ── En-tête ──
    elems.append(Paragraph("PortfolioSense", h1))
    elems.append(Paragraph(
        f"Rapport d'allocation personnalisé — {date.today().strftime('%d/%m/%Y')}",
        sub))
    elems.append(HRFlowable(width="100%", color=ACCENT, thickness=1.5))
    elems.append(Spacer(1, 8))

    # ── Profil ──
    elems.append(Paragraph("Votre profil", h2))
    profil_table = Table([
        ["Capital investi", f"{profile['capital']:,.0f} €".replace(",", " ")],
        ["Horizon", f"{profile['horizon']} ans"],
        ["Perte max tolérée", f"{profile['perte_max']}%"],
        ["Profil de risque", PROFIL_LABELS.get(profile["profil"], profile["profil"])],
    ], colWidths=[55 * mm, 100 * mm])
    profil_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), GRAY),
        ("TEXTCOLOR", (1, 0), (1, -1), TEXT),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elems.append(profil_table)

    # ── Métriques ──
    elems.append(Paragraph("Performances attendues", h2))
    m = portfolio["metrics"]
    metrics_table = Table([
        ["Rendement espéré", "Gain annuel estimé", "Volatilité", "Sharpe"],
        [f"{m['return']*100:.1f}% / an",
         f"+{portfolio['gain_espere']:,.0f} €".replace(",", " "),
         f"{m['volatility']*100:.1f}%",
         f"{m['sharpe']:.2f}"],
    ], colWidths=[40 * mm] * 4)
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, 1), 11),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e6e8ec")),
    ]))
    elems.append(metrics_table)

    # ── Allocation ──
    elems.append(Paragraph("Votre allocation recommandée", h2))
    alloc_rows = [["Actif", "Montant", "Poids", "Pourquoi ce choix ?"]]
    expl_map = {e["ticker"]: e["explanation"] for e in explanations}
    for a in portfolio["allocation"][:15]:
        alloc_rows.append([
            a["ticker"],
            f"{a['euros']:,.0f} €".replace(",", " "),
            f"{a['pct']}%",
            Paragraph(expl_map.get(a["ticker"], "—"), small),
        ])
    alloc_table = Table(alloc_rows, colWidths=[18 * mm, 24 * mm, 16 * mm, 100 * mm])
    alloc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("FONTSIZE", (0, 1), (2, -1), 9),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f7f9f8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e6e8ec")),
    ]))
    elems.append(alloc_table)

    # ── Risque ──
    elems.append(Paragraph("Votre exposition au risque", h2))
    elems.append(Paragraph(
        f"Sur une journée normale, votre portefeuille ne devrait pas perdre "
        f"plus de <b>{risk['var_eur']:,.0f} €</b> (VaR 95%). "
        f"Dans les 5% des pires journées, la perte moyenne serait de "
        f"<b>{risk['cvar_eur']:,.0f} €</b>. Lors de la pire crise de la "
        f"décennie (COVID, mars 2020), votre portefeuille aurait "
        f"temporairement perdu <b>{risk['max_dd_eur']:,.0f} €</b> avant de "
        f"se redresser.".replace(",", " "),
        body))
    elems.append(Spacer(1, 6))

    stress_rows = [["Scénario de crise", "Performance", "Impact sur votre capital"]]
    for s in risk["stress_tests"]:
        stress_rows.append([
            s["crise"], s["rendement"],
            f"{s['impact_eur']:,.0f} €".replace(",", " "),
        ])
    stress_table = Table(stress_rows, colWidths=[70 * mm, 35 * mm, 50 * mm])
    stress_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#faeae4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), RED),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e6e8ec")),
    ]))
    elems.append(stress_table)

    # ── Pied de page ──
    elems.append(Spacer(1, 14))
    elems.append(HRFlowable(width="100%", color=HexColor("#e6e8ec"), thickness=0.5))
    elems.append(Spacer(1, 4))
    elems.append(Paragraph(
        "PortfolioSense est un outil d'aide à la décision. Il ne constitue pas "
        "un conseil en investissement et n'exécute aucun ordre. Les performances "
        "passées ne préjugent pas des performances futures. Méthodes : "
        "optimisation Markowitz/Black-Litterman avec shrinkage Ledoit-Wolf, "
        "VaR validée par test de Kupiec, explicabilité SHAP.",
        small))

    doc.build(elems)
    return buf.getvalue()
