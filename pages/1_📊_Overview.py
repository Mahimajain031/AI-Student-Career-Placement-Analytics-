# pages/1_📊_Overview.py
"""Overview page – headline KPIs and the core placement story."""

import streamlit as st
from utils.theme import KPI_CSS, kpi_card, PLACED_COLOR, UNPLACED_COLOR, GREEN_COLOR, AMBER_COLOR
from utils.data_loader import load_data, apply_filters, placement_rate, threshold_pass_rates
from utils.charts import placement_donut, correlation_bar, segment_bar
from scipy import stats

st.set_page_config(page_title="Overview · Placement Analytics",
                   page_icon="📊", layout="wide")
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

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Overview")
st.caption(f"Showing **{len(df):,}** students after filters · Overall placement rate: **{placement_rate(df):.1f}%**")
st.markdown("---")

# ── Row 1: KPI cards ──────────────────────────────────────────────────────────
n_total   = len(df)
n_placed  = int(df["placed"].sum())
n_not     = n_total - n_placed
rate      = placement_rate(df)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(kpi_card("Total Students", f"{n_total:,}", "in filtered cohort"), unsafe_allow_html=True)
c2.markdown(kpi_card("Placed", f"{n_placed:,}", f"{rate:.1f}% of cohort", PLACED_COLOR), unsafe_allow_html=True)
c3.markdown(kpi_card("Not Placed", f"{n_not:,}", f"{100-rate:.1f}% of cohort", UNPLACED_COLOR), unsafe_allow_html=True)
c4.markdown(kpi_card("Placement Rate", f"{rate:.1f}%", "dataset-wide: 30.4%",
            GREEN_COLOR if rate >= 30 else AMBER_COLOR), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 2: Threshold pass-rate KPI cards ──────────────────────────────────────
thr = threshold_pass_rates(df)
t1, t2, t3, t4 = st.columns(4)
t1.markdown("**Placement Threshold Compliance**")
t1.caption("Share of cohort meeting each eligibility criterion")
t2.markdown(kpi_card("Coding ≥ 5", f"{thr['coding']:.1f}%", "of students meet threshold",
            GREEN_COLOR if thr['coding'] >= 50 else AMBER_COLOR), unsafe_allow_html=True)
t3.markdown(kpi_card("Aptitude ≥ 60", f"{thr['apt']:.1f}%", "of students meet threshold",
            GREEN_COLOR if thr['apt'] >= 50 else AMBER_COLOR), unsafe_allow_html=True)
t4.markdown(kpi_card("CGPA ≥ 6.5", f"{thr['cgpa']:.1f}%", "of students meet threshold",
            GREEN_COLOR if thr['cgpa'] >= 50 else AMBER_COLOR), unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: Donut + Correlation bar ────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.6])

with col_left:
    st.markdown("#### Placement Outcome")
    fig_donut = placement_donut(df)
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    st.markdown("#### What Drives Placement?")
    corr_data = {}
    for col_name in ["coding_skills","aptitude_score","cgpa","internships",
                     "certifications","projects","communication_skills","backlogs"]:
        r, _ = stats.pointbiserialr(df["placed"], df[col_name])
        corr_data[col_name.replace("_"," ").title()] = round(r, 4)
    st.plotly_chart(correlation_bar(corr_data), use_container_width=True)

st.markdown("---")

# ── Row 4: Segment bars ───────────────────────────────────────────────────────
st.markdown("#### Placement Rate by Segment")
col_deg, col_br = st.columns(2)
with col_deg:
    st.plotly_chart(segment_bar(df, "degree", "By Degree"), use_container_width=True)
with col_br:
    st.plotly_chart(segment_bar(df, "branch", "By Branch"), use_container_width=True)

st.markdown("---")

# ── Key insight callout ───────────────────────────────────────────────────────
st.markdown("#### 💡 Core Finding")
st.markdown(
    """<div class="insight-box">
    <strong>Three factors determine placement in this dataset with 100% accuracy:</strong><br>
    Coding Skills ≥ 5 &nbsp;·&nbsp; Aptitude Score ≥ 60 &nbsp;·&nbsp; CGPA ≥ 6.5<br><br>
    Students meeting <em>all three</em> are placed; missing <em>any one</em> results in non-placement.
    Degree, branch, gender, backlogs, certifications, and communication skills have no additional
    predictive power in this dataset (p &gt; 0.05 for all except coding, aptitude, and CGPA).
    </div>""",
    unsafe_allow_html=True,
)
st.caption(
    "Note: This rule is descriptive of the dataset and should not be interpreted as a universal guarantee of placement."
)
