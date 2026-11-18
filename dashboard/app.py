"""
Streamlit dashboard: Conclusion for the cirrhosis / drug-metabolism gene expression project.

Run from the project root:
    streamlit run dashboard/app.py

Reads:
    results/de_all_genes.csv, results/de_panel_genes.csv   (written by notebooks/main.ipynb)
    figures/*.png                                         (saved by the notebook)
    dashboard/data/*                                      (tables copied from the notebook outputs)
"""
import json
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Cirrhosis and drug-metabolism genes", page_icon="🧬", layout="wide")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS, FIGS, DATA = ROOT / "results", ROOT / "figures", HERE / "data"

# ------------------------------------------------------------------ palette
SLATE, SLATE_DARK = "#6a7aa3", "#5a6a93"
BG, TEXT, MUTED, GRID = "#e8eaf6", "#4a5578", "#9aa3bd", "#dfe3f0"
BLUE, CYAN, YELLOW, ORANGE, GREEN, RED, PURPLE = "#4d8bff", "#2db0ff", "#fdc94a", "#ff9f4a", "#2ed8a3", "#ff5a5f", "#a43be0"

# One colour code for direction, used on every page: blue = lower, red = higher, grey = no change.
DOWN, UP, NS = BLUE, RED, "#c3c9dc"
DIR_COLOR = {"Down in cirrhosis": DOWN, "Up in cirrhosis": UP, "NS": NS}
DIR_SYMBOL = {"Down in cirrhosis": "triangle-down", "Up in cirrhosis": "triangle-up", "NS": "circle"}
DIR_LABEL = {"Down in cirrhosis": "Lower", "Up in cirrhosis": "Higher", "NS": "No change"}
ALPHA, LFC_T = 0.05, 0.58
FONT = "Montserrat, 'Segoe UI', Helvetica, Arial, sans-serif"

TONES = {  # KPI tile: wave gradient (start, end) and number colour
    "blue": ("#20d0ff", "#0a8cff", CYAN),
    "orange": ("#ffdb4d", "#ff9a4a", "#fdb52e"),
    "green": ("#4ff0f0", "#2ed8a3", GREEN),
    "purple": ("#d27bff", "#8f2fe0", PURPLE),
}


def _wave(c1, c2):
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 70' preserveAspectRatio='none'>"
        f"<defs><linearGradient id='g' x1='0' x2='1'><stop offset='0' stop-color='{c1}'/><stop offset='1' stop-color='{c2}'/></linearGradient></defs>"
        "<path d='M0 44 C25 20 55 56 95 42 S160 14 200 30 S265 22 300 10 L300 70 L0 70 Z' fill='url(#g)'/></svg>"
    )
    return f'url("data:image/svg+xml,{quote(svg)}")'


tone_css = "\n".join(f".kpi-{k} .kpi-wave{{background-image:{_wave(a, b)}}} .kpi-{k} .kpi-v{{color:{c}}}" for k, (a, b, c) in TONES.items())

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp td, .stApp th, .stApp input, .stApp button, .stApp textarea, [data-testid="stMetric"] div,
[data-baseweb="tab"] {{ font-family: 'Montserrat', 'Segoe UI', Helvetica, Arial, sans-serif; }}

.stApp {{ background: {BG}; color: {TEXT}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stAppDeployButton"], .stDeployButton {{ display: none; }}
.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1320px; }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{ background: {SLATE}; border-right: none; }}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{ display: none; }}
.side-brand {{ background: {SLATE_DARK}; color: #fff; font-weight: 700; letter-spacing: .6px; font-size: 1.05rem;
  padding: 1.5rem 1.3rem; margin: -1.5rem -1rem 1.6rem -1rem; text-transform: uppercase; }}
[data-testid="stSidebar"] [role="radiogroup"] {{ gap: .2rem; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding: .65rem .9rem; border-radius: 8px; width: 100%; cursor: pointer; }}
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child {{ display: none; }}
[data-testid="stSidebar"] [role="radiogroup"] label * {{ color: #e6ebfa; font-size: .93rem; font-weight: 500; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background: rgba(255,255,255,.09); }}
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] * {{ color: #5fc8ff; font-weight: 700; }}
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] {{ background: rgba(255,255,255,.10); }}
.side-foot {{ color: #d6ddf3; font-size: .72rem; line-height: 1.5; margin-top: 2rem; opacity: .85; }}

/* ---------- top bar ---------- */
.topbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: .9rem; }}
.crumb {{ color: {MUTED}; font-size: .85rem; }}
.crumb b {{ color: #aab2cb; font-weight: 700; }}
.pill {{ background: #fff; color: {SLATE}; font-size: .75rem; font-weight: 600; padding: .35rem .9rem; border-radius: 999px;
  box-shadow: 0 4px 14px rgba(120,135,190,.16); }}
h1 {{ color: {SLATE_DARK}; font-weight: 700; font-size: 1.7rem !important; padding: 0 0 .3rem 0 !important; }}
h2, h3 {{ color: {SLATE_DARK}; font-weight: 600; }}
.page-sub {{ color: {MUTED}; font-size: .85rem; margin: -.2rem 0 1.1rem 0; }}

/* ---------- cards ---------- */
[class*="st-key-card_"] {{ background: #fff; border-radius: 8px; padding: 1.3rem 1.5rem 1.2rem 1.5rem;
  box-shadow: 0 10px 28px rgba(120,135,190,.20); }}
.card-title {{ font-size: 1.02rem; font-weight: 600; color: {TEXT}; margin-bottom: .15rem; }}
.card-take {{ font-size: .8rem; color: {MUTED}; margin-bottom: .5rem; line-height: 1.45; }}
.answer {{ border-left: 6px solid {BLUE}; padding-left: 1rem; }}
.answer .a-label {{ font-size: .72rem; font-weight: 700; letter-spacing: .8px; color: {BLUE}; text-transform: uppercase; }}
.answer .a-text {{ font-size: 1.1rem; font-weight: 600; color: {SLATE_DARK}; line-height: 1.5; margin-top: .25rem; }}

/* ---------- KPI tiles (like the Earnings / Downloads tiles) ---------- */
.kpi {{ background: #fff; border-radius: 8px; box-shadow: 0 10px 28px rgba(120,135,190,.20); text-align: center;
  padding: 1.4rem 1rem 0 1rem; overflow: hidden; min-height: 235px; display: flex; flex-direction: column; }}
.kpi-t {{ font-size: 1.05rem; color: {TEXT}; font-weight: 500; }}
.kpi-v {{ font-size: 1.9rem; font-weight: 700; margin: .5rem 0 .15rem 0; line-height: 1.15; }}
.kpi-c {{ font-size: .75rem; color: {MUTED}; line-height: 1.4; }}
.kpi-wave {{ flex: 1; min-height: 70px; margin: .9rem -1rem 0 -1rem; background-repeat: no-repeat; background-size: 100% 100%; background-position: bottom; }}
{tone_css}

/* ---------- finding list (like "Recently News") ---------- */
.find {{ padding: .85rem 0 .9rem 0; border-bottom: 1px solid #eef0f8; }}
.find:last-child {{ border-bottom: none; }}
.find-top {{ display: flex; justify-content: space-between; font-size: .72rem; font-weight: 700; color: {TEXT}; margin-bottom: .3rem; }}
.find-top span:last-child {{ color: {MUTED}; font-weight: 600; }}
.find-text {{ font-size: .8rem; color: #8a93ae; line-height: 1.55; }}

/* ---------- html table ---------- */
.tbl {{ width: 100%; border-collapse: collapse; font-size: .8rem; }}
.tbl th {{ color: {MUTED}; text-align: left; font-weight: 600; padding: .5rem .6rem; border-bottom: 1px solid #eef0f8; }}
.tbl td {{ padding: .75rem .6rem; border-bottom: 1px solid #f1f3fa; color: #8a93ae; vertical-align: top; line-height: 1.5; }}
.tbl tr:last-child td {{ border-bottom: none; }}
.tbl td:first-child {{ color: {TEXT}; font-weight: 600; white-space: nowrap; }}
.tag {{ background: #e3f9f1; color: #15b283; font-weight: 700; font-size: .68rem; padding: .18rem .65rem; border-radius: 999px; }}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-card_"]) {{ flex: 1 1 auto; }}
[class*="st-key-card_"] {{ flex: 1 1 auto; }}

/* ---------- native widgets ---------- */
[data-testid="stMetric"] {{ background: #fff; border-radius: 8px; padding: .9rem 1.1rem; box-shadow: 0 10px 28px rgba(120,135,190,.20); }}
[data-testid="stMetricLabel"] p {{ color: {MUTED}; font-size: .78rem; font-weight: 600; }}
[data-testid="stMetricValue"] {{ color: {SLATE_DARK}; font-weight: 700; font-size: 1.5rem; }}
button[data-baseweb="tab"] {{ font-weight: 600; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {BLUE}; }}
[data-baseweb="tab-highlight"] {{ background-color: {BLUE}; }}
[data-testid="stCaptionContainer"] {{ color: {MUTED}; }}
.stApp a {{ color: {BLUE}; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ data
@st.cache_data
def load_all():
    de = pd.read_csv(RESULTS / "de_all_genes.csv", index_col=0)
    panel = pd.read_csv(RESULTS / "de_panel_genes.csv", index_col=0)
    ann = pd.read_csv(DATA / "panel_annotations.csv", index_col=0)
    panel = panel.join(ann)
    return {
        "de": de,
        "panel": panel,
        "gsea": pd.read_csv(DATA / "gsea_kegg.csv"),
        "ora": pd.read_csv(DATA / "ora_top.csv"),
        "drug": pd.read_csv(DATA / "drug_pathways.csv", index_col=0),
        "ml": pd.read_csv(DATA / "ml_cv.csv"),
        "sum": json.loads((DATA / "summary.json").read_text()),
    }


try:
    D = load_all()
except FileNotFoundError as e:
    st.error(f"Missing file: {e.filename}. Run the notebook and commit `results/`, "
             "and make sure `dashboard/data/` is present.")
    st.stop()

DE, PANEL, S = D["de"], D["panel"], D["sum"]


# ------------------------------------------------------------------ helpers
_n = {"card": 0}


def card(name=None):
    """A white card. Use as: with card(): ..."""
    _n["card"] += 1
    return st.container(key=f"card_{name or _n['card']}")


def plot(fig, h=400, legend=True, grid_y=True, bar=False):
    """Styled plotly chart. The hover toolbar is hidden unless bar=True."""
    st.plotly_chart(style(fig, h, grid_y=grid_y, legend=legend), width="stretch", config={"displayModeBar": bar})


def fp(v):
    """Format a p-value or FDR for display."""
    return "<0.001" if v < 0.001 else f"{v:.2g}"


def table(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    st.markdown(f"<table class='tbl'><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>", unsafe_allow_html=True)


def head(title, takeaway=None):
    html = f"<div class='card-title'>{title}</div>"
    if takeaway:
        html += f"<div class='card-take'>{takeaway}</div>"
    st.markdown(html, unsafe_allow_html=True)


def kpi(title, value, caption, tone):
    st.markdown(
        f"<div class='kpi kpi-{tone}'><div class='kpi-t'>{title}</div><div class='kpi-v'>{value}</div>"
        f"<div class='kpi-c'>{caption}</div><div class='kpi-wave'></div></div>",
        unsafe_allow_html=True,
    )


def topbar(section):
    st.markdown(
        f"<div class='topbar'><div class='crumb'><b>Dashboard</b> &gt; {section}</div>"
        f"<div class='pill'>GSE14323 · {S['samples']['healthy']} healthy vs {S['samples']['cirrhosis']} cirrhosis</div></div>",
        unsafe_allow_html=True,
    )


def show_fig(name, caption=None):
    p = FIGS / name
    if p.exists():
        st.image(str(p), caption=caption, width="stretch")
    else:
        st.caption(f"(figure {name} not found in figures/)")


def style(fig, h=400, grid_y=True, legend=True):
    fig.update_layout(
        height=h, margin=dict(l=4, r=8, t=6, b=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=MUTED),
        showlegend=legend, legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=11, color=TEXT)),
        hoverlabel=dict(font_family=FONT, bgcolor="#fff", font_color=TEXT, bordercolor=GRID),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, griddash="dot", zeroline=False, linecolor=GRID,
                     tickfont=dict(size=11, color=MUTED), title_font=dict(size=11, color=MUTED))
    fig.update_yaxes(showgrid=grid_y, gridcolor=GRID, griddash="dot", zeroline=False, linecolor=GRID,
                     tickfont=dict(size=11, color=TEXT), title_font=dict(size=11, color=MUTED))
    return fig


# ------------------------------------------------------------------ pages
def page_conclusion():
    topbar("Conclusion")
    st.title("Does cirrhosis lower drug-metabolism gene expression?")
    st.markdown("<div class='page-sub'>Partly. A few specific CYP enzymes drop, but drug metabolism as a whole does not.</div>", unsafe_allow_html=True)

    with card():
        st.markdown(
            "<div class='answer'><div class='a-label'>Answer</div>"
            "<div class='a-text'>Cirrhosis lowers CYP2C19, CYP1A2 and CYP2E1. Other drug-metabolism genes are unchanged or higher, "
            "and the main first-pass enzyme, CYP3A4, does not drop.</div></div>",
            unsafe_allow_html=True,
        )
    st.write("")

    d = S["panel"]
    drug = D["drug"].loc["Metabolism of xenobiotics by cytochrome P450"]
    ml = D["ml"]
    panel_lr = ml[(ml.feature_set.str.startswith("A")) & (ml.model == "Logistic Regression")].iloc[0]

    left, right = st.columns([2.1, 1], gap="medium")
    with left:
        k1, k2, k3 = st.columns(3, gap="medium")
        with k1:
            kpi("Samples", f"{S['samples']['healthy']} vs {S['samples']['cirrhosis']}", "healthy vs cirrhotic liver", "blue")
        with k2:
            kpi("CYP pathway shift", f"{drug.GSEA_NES:+.2f}", f"GSEA score, FDR {drug.GSEA_FDR:.3f}<br>slightly up, not down", "orange")
        with k3:
            kpi("Panel classifier", f"{panel_lr.balanced_accuracy_mean:.2f}", "balanced accuracy, cross-validated", "green")
        st.write("")

        c1, c2 = st.columns([1, 1.5], gap="medium")
        with c1:
            with card():
                head("Panel genes", "16 genes tested at FDR < 0.05")
                fig = go.Figure(go.Pie(
                    labels=["Lower", "Higher", "No change"], values=[d["down"], d["up"], d["ns"]], hole=0.72,
                    marker=dict(colors=[DOWN, UP, NS], line=dict(color="#fff", width=3)),
                    textinfo="value", textfont=dict(color="#fff", size=13, family=FONT), sort=False, direction="clockwise",
                    hovertemplate="%{label}: %{value} genes<extra></extra>",
                ))
                fig.add_annotation(text="<b>16</b><br><span style='font-size:11px'>genes</span>", showarrow=False,
                                   font=dict(size=26, color=SLATE_DARK, family=FONT))
                plot(fig, 330)
        with c2:
            with card():
                head("Change in expression", "log2 fold change. Grey = not significant.")
                P = PANEL.sort_values("log2FC")
                fig = go.Figure(go.Bar(
                    x=P.log2FC, y=P.index, orientation="h", marker_color=[DIR_COLOR[x] for x in P.direction],
                    customdata=np.c_[P.padj, [DIR_LABEL[x] for x in P.direction]],
                    hovertemplate="%{y}: %{x:.2f}<br>FDR %{customdata[0]:.2g} (%{customdata[1]})<extra></extra>",
                ))
                fig.update_layout(bargap=0.35, xaxis_title="log2 fold change")
                fig.update_yaxes(showgrid=False)
                plot(fig, 330, legend=False)

    with right:
        with card("findings"):
            head("Key findings")
            items = [
                ("Genes", "16 tested",
                 "3 lower (CYP2C19, CYP1A2, CYP2E1), 5 higher, 8 unchanged. CYP3A4 looks higher, but its probes disagree."),
                ("Pathways", "GSEA",
                 "The xenobiotic CYP pathway shifts slightly up. What falls: protein secretion, cholesterol, clotting. What rises: immune and tissue-repair signals."),
                ("Cell mix", "adjusted",
                 "The three lower CYPs stay lower after adjusting for a hepatocyte marker score."),
                ("Classifier", "cross-validated",
                 "Separates the groups almost perfectly, partly through genes that rise, so it does not show that metabolism is lower."),
            ]
            st.markdown(
                "".join(f"<div class='find'><div class='find-top'><span>{a}</span><span>{b}</span></div><div class='find-text'>{c}</div></div>"
                        for a, b, c in items),
                unsafe_allow_html=True,
            )
    st.write("")

    a, b = st.columns([1.5, 1], gap="medium")
    with a:
        with card():
            head("Against the four project objectives")
            table(["Objective", "Status", "Result"], [
                ("1. Acquire and preprocess", "<span class='tag'>Done</span>",
                 f"GSE14323. {S['samples']['cirrhosis_before_hcc_filter']} cirrhosis samples minus 17 with HCC leaves {S['samples']['cirrhosis']}. {S['samples']['genes_tested']:,} genes tested."),
                ("2. Explore and visualise", "<span class='tag'>Done</span>", "Groups separate on PCA. No batch effect, no outliers. Panel genes move both ways."),
                ("3. Train a classifier", "<span class='tag'>Done</span>", "Balanced accuracy 0.99 (panel) to 1.00 (top 50 genes). Permutation p = 0.005."),
                ("4. Interpret and conclude", "<span class='tag'>Done</span>", "Hypothesis partly supported: selective loss of CYP2C19, CYP1A2, CYP2E1."),
            ])
    with b:
        with card():
            head("What it means for drugs")
            st.markdown(
                "<div class='find-text'>Lower CYP2C19, CYP1A2 and CYP2E1 points to slower clearance of drugs such as omeprazole, diazepam, "
                "theophylline and clozapine, and less activation of clopidogrel. That fits the usual advice to reduce doses or monitor closely in cirrhosis."
                "<br><br>Blood flow and shunting also shape first-pass exposure, and expression data cannot see them. See <b>Limits</b>.</div>",
                unsafe_allow_html=True,
            )


def page_genes():
    topbar("Drug-metabolism genes")
    st.title("Drug-metabolism genes")
    st.markdown("<div class='page-sub'>Welch t-test on log2 expression, Benjamini-Hochberg FDR across all 12,316 genes. log2FC = cirrhosis minus healthy.</div>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    classes = sorted(PANEL["class"].unique())
    pick_class = f1.multiselect("Gene class", classes, default=classes)
    pick_dir = f2.multiselect("Direction", list(DIR_COLOR), default=list(DIR_COLOR), format_func=lambda k: DIR_LABEL[k])
    P = PANEL[PANEL["class"].isin(pick_class) & PANEL["direction"].isin(pick_dir)].sort_values("log2FC")

    with card():
        head("Change in expression with 95% confidence intervals",
             "Three genes are clearly lower, five clearly higher. An interval that crosses zero is not significant.")
        fig = go.Figure()
        for dname, col in DIR_COLOR.items():
            sub = P[P.direction == dname]
            if sub.empty:
                continue
            fig.add_trace(go.Scatter(
                x=sub.log2FC, y=sub.index, mode="markers", name=DIR_LABEL[dname],
                marker=dict(color=col, size=11, symbol=DIR_SYMBOL[dname], line=dict(color="#fff", width=1)),
                error_x=dict(type="data", symmetric=False, array=sub.CI_high - sub.log2FC,
                             arrayminus=sub.log2FC - sub.CI_low, color="#cfd4e6", thickness=1.6),
                customdata=np.c_[sub.padj, sub["class"]],
                hovertemplate="%{y} (%{customdata[1]})<br>log2FC %{x:.2f}<br>FDR %{customdata[0]:.3g}<extra></extra>",
            ))
        fig.add_vline(x=0, line_color=SLATE, line_width=1)
        fig.update_layout(xaxis_title="log2 fold change (cirrhosis − healthy)",
                          yaxis=dict(categoryorder="array", categoryarray=list(P.index)))
        fig.update_yaxes(showgrid=False)
        plot(fig, 90 + 30 * max(len(P), 3))
        st.caption("CYP3A4 is shown as higher, but its probes disagree, so treat that direction with caution.")

    st.write("")
    with card():
        head("Results table")
        T = P[["class", "log2FC", "CI_low", "CI_high", "padj", "direction", "log2FC_adj_hepatocyte", "padj_adj_hepatocyte"]].copy()
        T["direction"] = T["direction"].map(lambda x: {"Down in cirrhosis": "▼ Lower", "Up in cirrhosis": "▲ Higher", "NS": "● No change"}[x])
        T.columns = ["Class", "log2FC", "CI low", "CI high", "FDR", "Direction", "log2FC (hepatocyte-adj.)", "FDR (hepatocyte-adj.)"]
        st.dataframe(
            T.style.format({"log2FC": "{:.2f}", "CI low": "{:.2f}", "CI high": "{:.2f}", "FDR": fp,
                            "log2FC (hepatocyte-adj.)": "{:.2f}", "FDR (hepatocyte-adj.)": fp}),
            width="stretch",
        )

    st.write("")
    with card():
        head("Gene detail")
        order = list(PANEL.sort_values("log2FC").index)
        g = st.selectbox("Gene", order, index=order.index("CYP2E1"))
        r = PANEL.loc[g]
        a, b, c, d = st.columns(4)
        a.metric("Healthy mean (log2)", f"{r.mean_healthy:.2f}")
        b.metric("Cirrhosis mean (log2)", f"{r.mean_cirrhosis:.2f}", f"{r.log2FC:+.2f}")
        c.metric("FDR", fp(r.padj))
        d.metric("Effect size (Hedges g)", f"{r.hedges_g:.2f}")
        st.markdown(f"**{g}** ({r['class']}). Example substrates: {r.example_substrates}.")
        if g == "CYP3A4":
            st.warning("CYP3A4 probes disagree: one shows no change and another shows an increase. The direction is not reliable.")
        with st.expander("Per-gene box plots from the EDA"):
            show_fig("eda5_panel_boxplots.png")


def page_transcriptome():
    topbar("Whole transcriptome")
    st.title("Whole transcriptome")
    st.markdown(f"<div class='page-sub'>{len(DE):,} genes tested. Cirrhosis changes thousands of genes, in both directions.</div>", unsafe_allow_html=True)

    with card():
        c1, c2, c3 = st.columns([1, 1, 2])
        alpha = c1.slider("FDR cut-off", 0.001, 0.10, ALPHA, 0.001, format="%.3f")
        lfc_t = c2.slider("|log2FC| cut-off", 0.0, 2.0, LFC_T, 0.05)
        extra = c3.multiselect("Highlight genes", list(DE.index), default=[], placeholder="Type a gene symbol")
        show_panel = st.checkbox("Outline the 16 panel genes", value=True)

    d = DE.copy()
    d["nlp"] = -np.log10(d.padj.clip(lower=1e-300))
    sig = (d.padj < alpha) & (d.log2FC.abs() >= lfc_t)
    d["group"] = np.where(~sig, "Not significant", np.where(d.log2FC < 0, "Down in cirrhosis", "Up in cirrhosis"))
    n_dn, n_up = int((d.group == "Down in cirrhosis").sum()), int((d.group == "Up in cirrhosis").sum())

    st.write("")
    k1, k2, k3 = st.columns(3, gap="medium")
    with k1:
        kpi("Lower in cirrhosis", f"{n_dn:,}", "genes past both cut-offs", "blue")
    with k2:
        kpi("Higher in cirrhosis", f"{n_up:,}", "genes past both cut-offs", "orange")
    with k3:
        kpi("Genes tested", f"{len(d):,}", "after probe-to-gene mapping", "green")
    st.write("")

    with card():
        head("Volcano plot", "Each dot is a gene. Far left or right means a large change, high up means a strong statistical signal.")
        fig = go.Figure()
        for name, col, lab in [("Not significant", "#d3d8e8", "Not significant"), ("Down in cirrhosis", DOWN, "Lower"), ("Up in cirrhosis", UP, "Higher")]:
            s = d[d.group == name]
            fig.add_trace(go.Scatter(x=s.log2FC, y=s.nlp, mode="markers", name=f"{lab} ({len(s):,})",
                                       marker=dict(size=4.5, color=col, opacity=0.65), text=s.index,
                                       hovertemplate="%{text}<br>log2FC %{x:.2f}<br>-log10 FDR %{y:.1f}<extra></extra>"))
        hl_all = list(dict.fromkeys((list(PANEL.index) if show_panel else []) + extra))
        if hl_all:
            h = d.loc[hl_all]
            # label only the significant panel genes and anything the user picked; outline the rest
            labels = [g if (g in extra or (g in PANEL.index and PANEL.loc[g, "padj"] < ALPHA)) else "" for g in h.index]
            fig.add_trace(go.Scatter(x=h.log2FC, y=h.nlp, mode="markers+text", text=labels, textposition="top center",
                                     hovertext=h.index, hoverinfo="text",
                                     name="Highlighted", marker=dict(size=10, color="rgba(0,0,0,0)", line=dict(color=SLATE_DARK, width=1.5)),
                                     textfont=dict(size=10, color=TEXT)))
        fig.add_hline(y=-np.log10(alpha), line_dash="dash", line_color=MUTED, line_width=1)
        for x in (-lfc_t, lfc_t):
            fig.add_vline(x=x, line_dash="dash", line_color=MUTED, line_width=1)
        fig.update_layout(xaxis_title="log2 fold change (cirrhosis − healthy)", yaxis_title="-log10(FDR)")
        plot(fig, 560)
        st.caption(f"At the notebook defaults (FDR < 0.05, |log2FC| ≥ 0.58): {S['de_all']['strong_down']:,} lower and {S['de_all']['strong_up']:,} higher.")

    st.write("")
    with card():
        head("Strongest changes", "Top 25 by FDR among genes past both cut-offs.")
        t1, t2 = st.tabs(["Most lower", "Most higher"])
        cols = ["mean_healthy", "mean_cirrhosis", "log2FC", "padj"]
        names = {"mean_healthy": "Healthy mean", "mean_cirrhosis": "Cirrhosis mean", "log2FC": "log2FC", "padj": "FDR"}
        fmt = {"Healthy mean": "{:.2f}", "Cirrhosis mean": "{:.2f}", "log2FC": "{:.2f}", "FDR": "{:.2g}"}
        t1.dataframe(d[sig & (d.log2FC < 0)].sort_values("padj")[cols].head(25).rename(columns=names).style.format(fmt), width="stretch")
        t2.dataframe(d[sig & (d.log2FC > 0)].sort_values("padj")[cols].head(25).rename(columns=names).style.format(fmt), width="stretch")


def page_pathways():
    topbar("Pathways and cells")
    st.title("Pathways and cell composition")
    st.markdown("<div class='page-sub'>Is the drug-metabolism machinery lower as a whole, and could fewer liver cells explain the drops?</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Drug-metabolism pathways", "What goes down and up", "Fewer hepatocytes?"])

    with t1:
        dp = D["drug"].copy()
        with card():
            head("Pathway shift (GSEA)", "No. The closest pathway to drug metabolism is shifted slightly up.")
            fig = go.Figure(go.Bar(
                x=dp.GSEA_NES, y=dp.index, orientation="h",
                marker_color=[UP if v > 0 else DOWN for v in dp.GSEA_NES],
                customdata=np.c_[dp.GSEA_FDR, dp.n_down, dp.n_up, dp.genes_tested],
                hovertemplate="%{y}<br>NES %{x:.2f}<br>FDR %{customdata[0]:.3f}<br>%{customdata[1]} down / %{customdata[2]} up of %{customdata[3]}<extra></extra>",
            ))
            fig.add_vline(x=0, line_color=SLATE, line_width=1)
            fig.update_layout(xaxis_title="GSEA NES (negative = lower in cirrhosis)", yaxis=dict(autorange="reversed"), bargap=0.4)
            fig.update_yaxes(showgrid=False)
            plot(fig, 320, legend=False)
            out = dp[["genes_tested", "n_down", "n_up", "median_log2FC", "GSEA_NES", "GSEA_FDR"]].round(3)
            out.columns = ["Genes tested", "Down", "Up", "Median log2FC", "NES", "FDR"]
            st.dataframe(out, width="stretch")
            st.caption("KEGG *Drug metabolism – cytochrome P450* and *– other enzymes* are not in the Enrichr KEGG_2021 library, so they could not be tested.")
        st.write("")
        with st.expander("Enrichment plots from the notebook"):
            show_fig("bioint3_drug_pathway_gsea.png")

    with t2:
        g = D["gsea"].copy()
        g["sig"] = g["FDR q-val"] < 0.25
        with card():
            head("Most shifted KEGG pathways", "Lower: protein making and secretion, cholesterol. Higher: immune signalling and tissue remodelling.")
            fig = go.Figure(go.Bar(
                x=g.NES, y=g.Term, orientation="h",
                marker_color=[UP if v > 0 else DOWN for v in g.NES],
                marker_opacity=[1.0 if s else 0.35 for s in g.sig],
                customdata=g["FDR q-val"], hovertemplate="%{y}<br>NES %{x:.2f}<br>FDR %{customdata:.3f}<extra></extra>",
            ))
            fig.add_vline(x=0, line_color=SLATE, line_width=1)
            fig.update_layout(xaxis_title="GSEA NES (faded bars: FDR ≥ 0.25)", yaxis=dict(autorange="reversed"), bargap=0.3)
            fig.update_yaxes(showgrid=False)
            plot(fig, 720, legend=False)
            st.caption("Top 15 lower and top 15 higher. In total 138 pathways pass FDR < 0.25: 11 lower, 127 higher.")
        st.write("")
        o = D["ora"].copy()
        o["FDR"] = o.fdr.map(lambda v: f"{v:.1e}")
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            with card():
                head("Top terms, lower in cirrhosis", "Over-representation analysis")
                st.dataframe(o[o.direction.str.startswith("Down")][["library", "term", "FDR"]], hide_index=True, width="stretch")
        with c2:
            with card():
                head("Top terms, higher in cirrhosis", "Over-representation analysis")
                st.dataframe(o[o.direction.str.startswith("Up")][["library", "term", "FDR"]], hide_index=True, width="stretch")
        st.caption("KEGG disease terms such as viral myocarditis or allograft rejection appear because they share immune and MHC genes. The diseases themselves are not implied.")
        with st.expander("Dot plot from the notebook"):
            show_fig("bioint1_ora_dotplot.png")

    with t3:
        p = S["cell_scores_p"]
        k1, k2, k3, k4 = st.columns(4, gap="medium")
        with k1:
            kpi("Hepatocyte score", "same", f"p = {p['hepatocyte']}", "green")
        with k2:
            kpi("Fibrosis score", "higher", f"p = {p['fibrosis']:.1e}", "orange")
        with k3:
            kpi("Ductular score", "higher", f"p = {p['ductular']:.0e}", "blue")
        with k4:
            kpi("Immune score", "higher", f"p = {p['immune']:.1e}", "purple")
        st.write("")
        A = PANEL.sort_values("log2FC")
        with card():
            head("Panel change before and after adjusting for hepatocyte content",
                 "CYP2C19, CYP1A2 and CYP2E1 stay lower with similar effect sizes, so fewer hepatocytes is not the whole story.")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=A.index, y=A.log2FC, name="Unadjusted", marker_color="#c3c9dc"))
            fig.add_trace(go.Bar(x=A.index, y=A.log2FC_adj_hepatocyte, name="Adjusted for hepatocyte score", marker_color=SLATE))
            fig.update_layout(barmode="group", yaxis_title="log2 fold change", bargap=0.25)
            fig.update_xaxes(showgrid=False)
            plot(fig, 400)
            st.markdown(
                "<div class='find-text'>Adjustment makes more genes significant (13 of 16), but the new ones have small effects (|log2FC| ≤ 0.52). "
                "The hepatocyte score is built from plasma-protein genes and may not track hepatocyte numbers well, "
                "so this rules out the simple explanation but does not settle it.</div>",
                unsafe_allow_html=True,
            )
        st.write("")
        with st.expander("Cell-score box plots from the notebook"):
            show_fig("bioint4_cell_composition.png")


def page_classifier():
    topbar("Classifier")
    st.title("Classifier: healthy vs cirrhotic liver")
    m = S["ml"]
    st.markdown("<div class='page-sub'>5-fold cross-validation repeated 10 times. Feature selection runs inside each fold, so there is no leakage.</div>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        kpi("Best model", "Random Forest", "top 50 genes", "blue")
    with k2:
        kpi("Out-of-fold AUC", f"{m['oof_roc_auc']:.2f}", f"{m['oof_misclassified']} of 60 misclassified", "green")
    with k3:
        kpi("Permutation test", f"p = {m['perm_p']}", f"shuffled labels score ≈ {m['perm_mean']:.2f}", "purple")
    with k4:
        kpi("Naive baseline", f"{m['majority_baseline_accuracy']:.2f}", "always guess cirrhosis (accuracy)", "orange")
    st.write("")

    M = D["ml"]
    with card():
        head("Cross-validated performance", "Every real model beats the baseline by a wide margin. Error bars show the spread across folds.")
        label = st.radio("Metric", ["balanced accuracy", "roc auc", "f1", "accuracy"], horizontal=True)
        metric = label.replace(" ", "_")
        fig = go.Figure()
        for fs, col in zip(M.feature_set.unique(), [PURPLE, YELLOW]):
            s = M[M.feature_set == fs]
            fig.add_trace(go.Bar(x=s.model, y=s[f"{metric}_mean"], name=fs, marker_color=col,
                                 error_y=dict(type="data", array=s[f"{metric}_sd"], color="#8a93ae", thickness=1.2)))
        fig.update_layout(barmode="group", yaxis=dict(range=[0, 1.05], title=label), bargap=0.3)
        fig.update_xaxes(showgrid=False)
        plot(fig, 380)
        st.caption("Panel = the 16 drug-metabolism genes. Top 50 = the 50 most different genes out of 12,316, picked inside each fold.")

    st.write("")
    W = PANEL[["lr_coef", "rf_importance", "log2FC", "padj"]].sort_values("lr_coef")
    l, r = st.columns(2, gap="medium")
    with l:
        with card():
            head("Logistic regression weights", "Positive predicts cirrhosis. Blue = gene is lower in cirrhosis, red = higher.")
            col = [DIR_COLOR[PANEL.loc[g, "direction"]] for g in W.index]
            f1 = go.Figure(go.Bar(x=W.lr_coef, y=W.index, orientation="h", marker_color=col))
            f1.update_layout(xaxis_title="standardised coefficient", bargap=0.35)
            f1.update_yaxes(showgrid=False)
            plot(f1, 480, legend=False)
    with r:
        with card():
            head("Random forest importance", "ABCB1 tops the list, and it rises in cirrhosis.")
            R = W.sort_values("rf_importance")
            col = [DIR_COLOR[PANEL.loc[g, "direction"]] for g in R.index]
            f2 = go.Figure(go.Bar(x=R.rf_importance, y=R.index, orientation="h", marker_color=col))
            f2.update_layout(xaxis_title="importance", bargap=0.35)
            f2.update_yaxes(showgrid=False)
            plot(f2, 480, legend=False)
    st.write("")
    with card():
        head("How to read this")
        st.markdown(
            "<div class='find-text'>CYP2E1 and CYP2C19 carry the strongest negative weights, matching the lower CYPs. "
            "ABCB1 and GSTA1 carry the strongest positive weights. The panel classifies well because its genes change in <b>both</b> directions, "
            "which is not the same as metabolism being lower.</div>",
            unsafe_allow_html=True,
        )
    st.write("")
    with st.expander("Confusion matrix, ROC and permutation plots"):
        show_fig("ml2_best_model.png")
        show_fig("ml3_permutation.png")


def page_limits():
    topbar("Limits")
    st.title("Limits")
    st.markdown("<div class='page-sub'>What the data can and cannot support.</div>", unsafe_allow_html=True)
    s = S["samples"]
    blocks = [
        ("Data", [
            "One study, one chip (GPL571), no external validation set.",
            f"Unbalanced groups: {s['healthy']} healthy vs {s['cirrhosis']} cirrhosis. A rerun with all {s['cirrhosis_before_hcc_filter']} cirrhosis samples (17 with HCC) gave similar results.",
            "No sex, age or cause-of-disease information. The sex mix looked different between groups in the EDA.",
            "UGT2B7 is not on the chip, so 16 of 17 planned genes were tested.",
        ]),
        ("Analysis", [
            "Each gene is represented by its highest-mean probe. CYP3A4 probes disagree, so its direction is unreliable.",
            "The hepatocyte score does not differ between groups, which is surprising in cirrhosis. Treat it as a rough proxy.",
            "Two core KEGG drug-metabolism pathways are missing from the library, so the pathway test uses the closest one.",
            "Why some drug genes rise (for example ductular cell expansion) is a hypothesis and was not tested.",
        ]),
        ("Classifier", [
            "60 samples from a single study. Scores near 1.0 show the groups are easy to separate here, not that the model is ready for clinical use.",
            "The best model was picked on the same cross-validation it is reported on, which gives a small optimistic bias.",
        ]),
        ("Interpretation", [
            "mRNA level is not enzyme activity, and bulk tissue mixes cell types.",
            "First-pass exposure also depends on blood flow and shunting, which this data cannot measure.",
        ]),
    ]
    for (t1, b1), (t2, b2) in [(blocks[0], blocks[1]), (blocks[2], blocks[3])]:
        c1, c2 = st.columns(2, gap="medium")
        for col, t, b in [(c1, t1, b1), (c2, t2, b2)]:
            with col:
                with card():
                    head(t)
                    st.markdown("".join(f"<div class='find-text' style='padding:.35rem 0'>• {x}</div>" for x in b), unsafe_allow_html=True)
        st.write("")


PAGES = {
    ":material/home: Conclusion": page_conclusion,
    ":material/biotech: Drug-metabolism genes": page_genes,
    ":material/bubble_chart: Whole transcriptome": page_transcriptome,
    ":material/account_tree: Pathways and cells": page_pathways,
    ":material/psychology: Classifier": page_classifier,
    ":material/error: Limits": page_limits,
}

with st.sidebar:
    st.markdown("<div class='side-brand'>Cirrhosis × CYP</div>", unsafe_allow_html=True)
    choice = st.radio("Section", list(PAGES), label_visibility="collapsed")
    st.markdown("<div class='side-foot'>Data: GSE14323 (GPL571).<br>Numbers come from notebooks/main.ipynb.</div>", unsafe_allow_html=True)
PAGES[choice]()
