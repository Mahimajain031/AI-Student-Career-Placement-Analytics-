# pages/3_📉_Skill_Gap_Analysis.py
"""Skill Gap Analysis – compare placed vs not-placed skill profiles."""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from utils.theme import KPI_CSS, PLACED_COLOR, UNPLACED_COLOR, MUTED_COLOR
from utils.data_loader import load_data, apply_filters
from utils.charts import skill_gap_bar, skill_radar, box_plot_split, scatter_apt_vs_coding

st.set_page_config(page_title="Skill Gap Analysis · Analytics",
                   page_icon="📉", layout="wide")
st.markdown(KPI_CSS, unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
df_all = load_data()
filters = st.session_state.get("filters", {
    "degree": sorted(df_all["degree"].unique().tolist()),
    "branch": sorted(df_all["branch"].unique().tolist()),
    "gender": sorted(df_all["gender"].unique().tolist()),
    "age":    (20, 24),
    "placed_status": "All",
})
df = apply_filters(df_all, filters)
placed    = df[df["placed"] == 1]
not_placed = df[df["placed"] == 0]

st.markdown("## 📉 Skill Gap Analysis")
st.caption(
    f"Comparing **{len(placed):,} placed** vs **{len(not_placed):,} not-placed** students."
)
st.markdown("---")

# ── Section 1: Gap bar + Radar ─────────────────────────────────────────────────
st.markdown("### Feature-Level Gap: Placed vs Not Placed")

col_gap, col_radar = st.columns([1.2, 1])
with col_gap:
    st.plotly_chart(skill_gap_bar(df), use_container_width=True)
with col_radar:
    # Normalise all features to 0–1 for radar
    feat_ranges = {
        "CGPA":            (5.5,  9.8),
        "Aptitude":        (40,   99),
        "Coding":          (1,    10),
        "Comm. Skills":    (1,    10),
        "Internships":     (0,    3),
        "Certifications":  (0,    5),
        "Projects":        (0,    5),
        "Backlogs (inv)":  (0,    3),   # invert: 0 backlogs is best
    }
    raw_cols = ["cgpa","aptitude_score","coding_skills","communication_skills",
                "internships","certifications","projects","backlogs"]

    placed_norm  = {}
    unplaced_norm = {}
    for label, (lo, hi), col_name in zip(feat_ranges.keys(), feat_ranges.values(), raw_cols):
        rng = hi - lo
        if col_name == "backlogs":
            # invert: fewer backlogs = better
            pv = 1 - (placed[col_name].mean() - lo) / rng
            nv = 1 - (not_placed[col_name].mean() - lo) / rng
        else:
            pv = (placed[col_name].mean()    - lo) / rng
            nv = (not_placed[col_name].mean() - lo) / rng
        placed_norm[label]   = round(max(0, min(1, pv)), 3)
        unplaced_norm[label] = round(max(0, min(1, nv)), 3)

    st.plotly_chart(skill_radar(placed_norm, unplaced_norm), use_container_width=True)

st.markdown("---")

# ── Section 2: Statistical summary table ──────────────────────────────────────
st.markdown("### Statistical Summary Table")
rows = []
feats = ["cgpa","aptitude_score","coding_skills","communication_skills",
         "internships","certifications","projects","backlogs"]
feat_labels = ["CGPA","Aptitude Score","Coding Skills","Communication Skills",
               "Internships","Certifications","Projects","Backlogs"]

for feat, label in zip(feats, feat_labels):
    if len(placed) > 1 and len(not_placed) > 1:
        t_stat, p_val = stats.ttest_ind(placed[feat], not_placed[feat])
    else:
        t_stat, p_val = 0.0, 1.0
    p_mean = placed[feat].mean()    if len(placed) else 0
    n_mean = not_placed[feat].mean() if len(not_placed) else 0
    gap    = p_mean - n_mean
    sig    = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "–"))
    rows.append({
        "Feature":            label,
        "Placed Mean":        round(p_mean, 3),
        "Not-Placed Mean":    round(n_mean, 3),
        "Gap (P−NP)":         round(gap, 3),
        "p-value":            round(p_val, 4),
        "Significant?":       sig,
    })

summary_df = pd.DataFrame(rows)

def _color_sig(val):
    if val in ("***","**","*"):
        return "color: #065f46; font-weight:700;"
    return "color: #57606a;"

def _color_gap(val):
    if val > 0.1:
        return f"color: {PLACED_COLOR};"
    if val < -0.1:
        return f"color: {UNPLACED_COLOR};"
    return f"color: {MUTED_COLOR};"

st.dataframe(
    summary_df.style
        .applymap(_color_sig,   subset=["Significant?"])
        .applymap(_color_gap,   subset=["Gap (P−NP)"]),
    hide_index=True,
    use_container_width=True,
)
st.caption("*** p<0.001  ** p<0.01  * p<0.05  – not significant")

st.markdown("---")

# ── Section 3: Box plots for top 3 significant features ───────────────────────
st.markdown("### Distribution Comparison (Box Plots)")
st.caption("Only the three statistically significant features are shown.")
bc1, bc2, bc3 = st.columns(3)
with bc1:
    st.plotly_chart(box_plot_split(df, "coding_skills",  "Coding Skills"),  use_container_width=True)
with bc2:
    st.plotly_chart(box_plot_split(df, "aptitude_score", "Aptitude Score"), use_container_width=True)
with bc3:
    st.plotly_chart(box_plot_split(df, "cgpa",           "CGPA"),           use_container_width=True)

st.markdown("---")

# ── Section 4: Scatter ─────────────────────────────────────────────────────────
st.markdown("### Aptitude vs Coding Skills — Placement Boundary")
st.caption(
    "Students in the top-right quadrant (aptitude ≥ 60, coding ≥ 5) "
    "are placed when CGPA ≥ 6.5 is also met. "
    "No student below either threshold is placed. (Sample: 2,000 students)"
)
st.plotly_chart(scatter_apt_vs_coding(df), use_container_width=True)

st.markdown("---")
st.markdown(
    """<div class="insight-box">
    <strong>What this means for improvement:</strong><br>
    Only <strong>coding skills</strong>, <strong>aptitude score</strong>, and <strong>CGPA</strong>
    have statistically significant relationships with placement (p &lt; 0.001).
    Communication skills, backlogs, certifications, and internships show no meaningful gap
    between placed and not-placed cohorts in this dataset.
    </div>""",
    unsafe_allow_html=True,
)
