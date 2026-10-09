# pages/2_🎯_Placement_Insights.py
"""Placement Insights – threshold analysis, segment breakdowns, root causes."""

import streamlit as st
import pandas as pd
from utils.theme import KPI_CSS
from utils.data_loader import load_data, apply_filters
from utils.charts import (
    threshold_cliff_chart, heatmap_degree_branch,
    root_cause_pie, segment_bar, threshold_progress_bar,
)

st.set_page_config(page_title="Placement Insights · Analytics",
                   page_icon="🎯", layout="wide")
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

st.markdown("## 🎯 Placement Insights")
st.caption(
    f"Showing **{len(df):,}** students · "
    f"Placement rate: **{df['placed'].mean()*100:.1f}%**"
)
st.markdown("---")

# ── Section 1: Three threshold cliff charts ────────────────────────────────────
st.markdown("### The Three Eligibility Thresholds")
st.markdown(
    """<div class="insight-box">
    Students must meet <strong>all three thresholds</strong> to be placed.
    Below each threshold, placement rate = <strong>0%</strong>.
    The charts below show the precise cliff-edge effect.
    </div>""",
    unsafe_allow_html=True,
)

t1, t2, t3 = st.columns(3)
with t1:
    st.plotly_chart(
        threshold_cliff_chart(df, "coding_skills", 5,
                              "Coding Skills (1–10)", "Coding Score"),
        use_container_width=True,
    )
with t2:
    st.plotly_chart(
        threshold_cliff_chart(df, "aptitude_score", 60,
                              "Aptitude Score (40–99)", "Aptitude Band"),
        use_container_width=True,
    )
with t3:
    st.plotly_chart(
        threshold_cliff_chart(df, "cgpa", 6.5,
                              "CGPA (5.5–9.8)", "CGPA Band"),
        use_container_width=True,
    )

st.markdown("---")

# ── Section 2: Threshold pass distribution ────────────────────────────────────
st.markdown("### How Many Students Clear All Thresholds?")
c1, c2 = st.columns([1.4, 1])
with c1:
    st.plotly_chart(threshold_progress_bar(df), use_container_width=True)
with c2:
    thr_counts = df["thresholds_met"].value_counts().sort_index()
    n = len(df)
    st.markdown("**Breakdown by thresholds met:**")
    labels_ = ["None met","1 of 3 met","2 of 3 met","All 3 met (eligible)"]
    for i, lbl in enumerate(labels_):
        cnt = int(thr_counts.get(i, 0))
        st.write(f"- **{lbl}:** {cnt:,} ({cnt/n*100:.1f}%)")

st.markdown("---")

# ── Section 3: Segment analysis ───────────────────────────────────────────────
st.markdown("### Placement Rate by Academic Segment")
st.caption("Degree and branch affect placement rate within only a 3 pp range — they are weak standalone predictors.")

col_d, col_b = st.columns(2)
with col_d:
    st.plotly_chart(segment_bar(df, "degree", "By Degree"), use_container_width=True)
with col_b:
    st.plotly_chart(segment_bar(df, "branch", "By Branch"), use_container_width=True)

st.markdown("---")

# ── Section 4: Degree × Branch heatmap ────────────────────────────────────────
st.markdown("### Degree × Branch Placement Rate Matrix")
st.caption("BE + DS (36.2%) and BSc + AI (35.2%) are the best-performing combinations in this dataset.")
st.plotly_chart(heatmap_degree_branch(df), use_container_width=True)

st.markdown("---")

# ── Section 5: Root causes pie ────────────────────────────────────────────────
st.markdown("### Why Are Students Not Placed? Root Cause Breakdown")
st.caption(f"Applies to {int((df['placed']==0).sum()):,} not-placed students in filtered cohort.")
cc1, cc2 = st.columns([1, 1])
with cc1:
    st.plotly_chart(root_cause_pie(df), use_container_width=True)
with cc2:
    np_df = df[df["placed"] == 0]
    rc = np_df["root_cause"].value_counts().reset_index()
    rc.columns = ["Cause", "Count"]
    rc["Share (%)"] = (rc["Count"] / len(np_df) * 100).round(1)
    st.markdown("**Root cause detail table:**")
    st.dataframe(rc, hide_index=True, use_container_width=True)
    st.markdown(
        """<div class="warn-box">
        <strong>Key takeaway:</strong> Low coding skills is the <em>single largest barrier</em> —
        affecting 29.4% of not-placed students as the sole failure factor,
        and involved in 57% of all non-placements.
        </div>""",
        unsafe_allow_html=True,
    )
