# app.py  –  Main entry point for the Streamlit dashboard
"""
AI-Powered Student Career & Placement Analytics
Run with:  streamlit run app.py
"""

import streamlit as st
from utils.theme import KPI_CSS
from utils.data_loader import load_data, get_filter_defaults

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Student Placement Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject shared CSS ─────────────────────────────────────────────────────────
st.markdown(KPI_CSS, unsafe_allow_html=True)

# ── Load data once ────────────────────────────────────────────────────────────
df_all = load_data()

# ── Session-state defaults ────────────────────────────────────────────────────
if "filters" not in st.session_state:
    st.session_state["filters"] = get_filter_defaults(df_all)

if "student_profile" not in st.session_state:
    st.session_state["student_profile"] = {
        "cgpa": 7.5,
        "aptitude_score": 65,
        "coding_skills": 5,
        "communication_skills": 6,
        "internships": 1,
        "certifications": 2,
        "projects": 2,
        "backlogs": 1,
        "degree": "BTech",
        "branch": "CS",
        "gender": "Male",
        "age": 21,
    }

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/graduation-cap.png",
        width=52,
    )
    st.markdown("## 🎓 Placement Analytics")
    st.markdown("---")

    st.markdown("### 🔍 Global Filters")
    st.caption("Applied to all aggregate pages")

    degree_opts = sorted(df_all["degree"].unique().tolist())
    branch_opts = sorted(df_all["branch"].unique().tolist())
    gender_opts = sorted(df_all["gender"].unique().tolist())

    sel_degree = st.multiselect(
        "Degree", degree_opts,
        default=st.session_state["filters"]["degree"],
        key="f_degree",
    )
    sel_branch = st.multiselect(
        "Branch", branch_opts,
        default=st.session_state["filters"]["branch"],
        key="f_branch",
    )
    sel_gender = st.multiselect(
        "Gender", gender_opts,
        default=st.session_state["filters"]["gender"],
        key="f_gender",
    )
    age_min, age_max = int(df_all["age"].min()), int(df_all["age"].max())
    sel_age = st.slider(
        "Age Range", age_min, age_max,
        value=(age_min, age_max),
        key="f_age",
    )
    sel_status = st.selectbox(
        "Placement Status", ["All", "Placed", "Not Placed"],
        index=0, key="f_status",
    )

    # persist filters to session state
    st.session_state["filters"] = {
        "degree":        sel_degree if sel_degree else degree_opts,
        "branch":        sel_branch if sel_branch else branch_opts,
        "gender":        sel_gender if sel_gender else gender_opts,
        "age":           sel_age,
        "placed_status": sel_status,
    }

    st.markdown("---")
    # quick stats for filtered set
    from utils.data_loader import apply_filters
    df_f = apply_filters(df_all, st.session_state["filters"])
    n_total  = len(df_f)
    n_placed = int(df_f["placed"].sum())
    rate     = n_placed / n_total * 100 if n_total else 0
    st.markdown(
        f"**Filtered cohort:** {n_total:,} students  \n"
        f"**Placed:** {n_placed:,} &nbsp;|&nbsp; **Rate:** {rate:.1f}%"
    )
    st.markdown("---")
    st.caption("Dataset: 12,000 Indian engineering students · 2025")

# ── Landing / Home page ───────────────────────────────────────────────────────
st.markdown("## 🎓 AI-Powered Student Career & Placement Analytics")
st.markdown(
    "Use the **sidebar navigation** to explore the six analytical pages. "
    "Global filters on the left apply to all aggregate views."
)

cols = st.columns(3)
pages = [
    ("📊", "Overview",           "Headline KPIs and the core placement story"),
    ("🎯", "Placement Insights", "Threshold analysis, segment breakdowns & root causes"),
    ("📉", "Skill Gap Analysis", "Feature-level comparison of placed vs not-placed students"),
    ("🧑‍🎓", "Student Assessment","Enter a student profile and check placement eligibility"),
    ("🤖", "AI Career Advisor",  "Personalised, data-driven improvement recommendations"),
    ("🔍", "Data Explorer",      "Filter, browse and download any slice of the dataset"),
]
for i, (icon, name, desc) in enumerate(pages):
    with cols[i % 3]:
        st.markdown(
            f"""<div class="kpi-card" style="text-align:left; margin-bottom:12px;">
            <div style="font-size:26px;">{icon}</div>
            <div style="font-weight:700; font-size:14px; margin:6px 0 4px;">{name}</div>
            <div style="font-size:12px; color:#57606a;">{desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption(
    "All insights are grounded in the cleaned 12,000-student dataset. "
    "No synthetic data or unsupported claims are used. "
    "The placement eligibility rule (coding ≥ 5 · aptitude ≥ 60 · CGPA ≥ 6.5) "
    "achieves 100% accuracy on this dataset and is presented descriptively, not as a guarantee."
)
