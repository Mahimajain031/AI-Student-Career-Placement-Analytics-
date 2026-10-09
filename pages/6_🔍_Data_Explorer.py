# pages/6_🔍_Data_Explorer.py
"""Data Explorer – filtered, sortable view of the full dataset with export."""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.theme import KPI_CSS, kpi_card, PLACED_COLOR, SURFACE_COLOR
from utils.data_loader import load_data, apply_filters

st.set_page_config(page_title="Data Explorer · Analytics",
                   page_icon="🔍", layout="wide")
st.markdown(KPI_CSS, unsafe_allow_html=True)

df_all = load_data()

st.markdown("## 🔍 Data Explorer")
st.markdown("Filter, sort and download any slice of the cleaned dataset.")
st.markdown("---")

# ── Sidebar / column-level filters ────────────────────────────────────────────
filters = st.session_state.get("filters", {
    "degree": sorted(df_all["degree"].unique().tolist()),
    "branch": sorted(df_all["branch"].unique().tolist()),
    "gender": sorted(df_all["gender"].unique().tolist()),
    "age":    (20, 24),
    "placed_status": "All",
})
df_base = apply_filters(df_all, filters)

with st.expander("🎛️ Additional Column Filters", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        cgpa_range = st.slider("CGPA range", 5.5, 9.8,
                               (float(df_base["cgpa"].min()), float(df_base["cgpa"].max())), step=0.1)
        coding_range = st.slider("Coding Skills range", 1, 10,
                                 (int(df_base["coding_skills"].min()), int(df_base["coding_skills"].max())))
    with c2:
        apt_range = st.slider("Aptitude Score range", 40, 99,
                              (int(df_base["aptitude_score"].min()), int(df_base["aptitude_score"].max())))
        backlog_range = st.slider("Backlogs range", 0, 3,
                                  (int(df_base["backlogs"].min()), int(df_base["backlogs"].max())))
    with c3:
        intern_range = st.slider("Internships range", 0, 3,
                                 (int(df_base["internships"].min()), int(df_base["internships"].max())))
        cert_range = st.slider("Certifications range", 0, 5,
                               (int(df_base["certifications"].min()), int(df_base["certifications"].max())))

# Apply column-level filters
df_view = df_base.copy()
df_view = df_view[
    (df_view["cgpa"].between(*cgpa_range)) &
    (df_view["coding_skills"].between(*coding_range)) &
    (df_view["aptitude_score"].between(*apt_range)) &
    (df_view["backlogs"].between(*backlog_range)) &
    (df_view["internships"].between(*intern_range)) &
    (df_view["certifications"].between(*cert_range))
]

# ── Summary KPIs ──────────────────────────────────────────────────────────────
n_total  = len(df_view)
n_placed = int(df_view["placed"].sum())
rate     = n_placed / n_total * 100 if n_total > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.markdown(kpi_card("Rows in View", f"{n_total:,}", "after all filters"), unsafe_allow_html=True)
k2.markdown(kpi_card("Placed", f"{n_placed:,}", f"{rate:.1f}%", PLACED_COLOR), unsafe_allow_html=True)
k3.markdown(kpi_card("Not Placed", f"{n_total - n_placed:,}", f"{100-rate:.1f}%"), unsafe_allow_html=True)
k4.markdown(kpi_card("Mean CGPA", f"{df_view['cgpa'].mean():.2f}" if n_total else "—", "in filtered view"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Column chooser ────────────────────────────────────────────────────────────
display_cols = ["student_id","gender","age","degree","branch","cgpa","backlogs",
                "internships","certifications","coding_skills","communication_skills",
                "aptitude_score","projects","placed"]
sel_cols = st.multiselect("Choose columns to display",
                          options=display_cols,
                          default=display_cols)

# ── Colour-code placed column ──────────────────────────────────────────────────
display_df = df_view[sel_cols].reset_index(drop=True)

def style_placed(val):
    if val == 1:
        return "background-color: #d1fae5; color: #065f46; font-weight:600;"
    elif val == 0:
        return "background-color: #fee2e2; color: #991b1b;"
    return ""

styled = display_df.copy()
if "placed" in sel_cols:
    st.dataframe(
        display_df.style.applymap(style_placed, subset=["placed"]),
        hide_index=True,
        use_container_width=True,
        height=420,
    )
else:
    st.dataframe(display_df, hide_index=True, use_container_width=True, height=420)

# ── Download ──────────────────────────────────────────────────────────────────
csv_bytes = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Current View as CSV",
    data=csv_bytes,
    file_name="placement_data_filtered.csv",
    mime="text/csv",
    use_container_width=False,
)

st.markdown("---")

# ── On-demand histogram ───────────────────────────────────────────────────────
st.markdown("### Quick Distribution View")
num_cols = ["cgpa","aptitude_score","coding_skills","communication_skills",
            "internships","certifications","projects","backlogs","age"]
hist_col = st.selectbox("Select a column to plot its distribution:", num_cols)

if n_total > 0:
    hcol_a, hcol_b = st.columns(2)
    with hcol_a:
        fig = px.histogram(
            df_view, x=hist_col, color="placed",
            color_discrete_map={1: PLACED_COLOR, 0: "#ef4444"},
            nbins=20,
            barmode="overlay",
            labels={"placed": "Placed", hist_col: hist_col.replace("_", " ").title()},
            title=f"Distribution of {hist_col.replace('_',' ').title()} by Placement Status",
            template="plotly_white",
        )
        fig.update_layout(height=320, margin=dict(l=40, r=20, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)
    with hcol_b:
        stats_df = df_view.groupby("placed")[hist_col].describe().round(2)
        stats_df.index = stats_df.index.map({1: "Placed", 0: "Not Placed"})
        st.markdown(f"**{hist_col.replace('_',' ').title()} — Summary Statistics**")
        st.dataframe(stats_df, use_container_width=True)
else:
    st.warning("No data matches the current filters.")

st.markdown("---")
st.caption(
    "Source: student_placement_clean.csv · 12,000 students · "
    "Computed columns (coding_pass, apt_pass, etc.) are excluded from this view."
)
