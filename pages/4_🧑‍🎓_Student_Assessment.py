# pages/4_🧑‍🎓_Student_Assessment.py
"""Student Assessment – per-student eligibility check and gap report."""

import streamlit as st
import pandas as pd
import numpy as np
from utils.theme import KPI_CSS, kpi_card, GREEN_COLOR, UNPLACED_COLOR, AMBER_COLOR, PLACED_COLOR
from utils.data_loader import (
    load_data, CODING_THRESH, APT_THRESH, CGPA_THRESH, student_percentile,
)
from utils.charts import gauge_chart, student_radar

st.set_page_config(page_title="Student Assessment · Analytics",
                   page_icon="🧑‍🎓", layout="wide")
st.markdown(KPI_CSS, unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
df_all  = load_data()
placed  = df_all[df_all["placed"] == 1]

st.markdown("## 🧑‍🎓 Student Assessment")
st.markdown(
    "Enter a student's profile below. The tool checks placement eligibility "
    "against the three data-verified thresholds and shows where the student "
    "stands relative to placed peers."
)
st.markdown("---")

# ── Input form ────────────────────────────────────────────────────────────────
st.markdown("### Enter Student Profile")
st.caption("All fields use the same scale as the dataset.")

# Pre-fill from session state if available
sp = st.session_state.get("student_profile", {})

with st.form("student_form"):
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Academic**")
        cgpa  = st.slider("CGPA", 5.5, 9.8, float(sp.get("cgpa", 7.5)), step=0.1)
        aptitude = st.slider("Aptitude Score", 40, 99, int(sp.get("aptitude_score", 65)))
        coding   = st.slider("Coding Skills (1–10)", 1, 10, int(sp.get("coding_skills", 5)))
        backlogs = st.slider("Backlogs (0–3)", 0, 3, int(sp.get("backlogs", 1)))

    with col_b:
        st.markdown("**Skills & Activities**")
        comm    = st.slider("Communication Skills (1–10)", 1, 10, int(sp.get("communication_skills", 6)))
        interns = st.slider("Internships (0–3)", 0, 3, int(sp.get("internships", 1)))
        certs   = st.slider("Certifications (0–5)", 0, 5, int(sp.get("certifications", 2)))
        projects = st.slider("Projects (0–5)", 0, 5, int(sp.get("projects", 2)))

    with col_c:
        st.markdown("**Background**")
        degree = st.selectbox("Degree", ["BE","BTech","BCA","BSc"],
                              index=["BE","BTech","BCA","BSc"].index(sp.get("degree","BTech")))
        branch = st.selectbox("Branch", ["CS","IT","DS","AI","Electrical","Mechanical"],
                              index=["CS","IT","DS","AI","Electrical","Mechanical"].index(sp.get("branch","CS")))
        gender = st.selectbox("Gender", ["Male","Female"],
                              index=["Male","Female"].index(sp.get("gender","Male")))
        age    = st.slider("Age", 20, 24, int(sp.get("age", 21)))

    submitted = st.form_submit_button("🔍 Assess Placement Eligibility", use_container_width=True)

if submitted:
    # Persist to session state
    st.session_state["student_profile"] = {
        "cgpa": cgpa, "aptitude_score": aptitude, "coding_skills": coding,
        "backlogs": backlogs, "communication_skills": comm, "internships": interns,
        "certifications": certs, "projects": projects,
        "degree": degree, "branch": branch, "gender": gender, "age": age,
    }

# Always show results using current profile values (not just on submit)
profile = st.session_state.get("student_profile", {
    "cgpa": 7.5, "aptitude_score": 65, "coding_skills": 5,
    "backlogs": 1, "communication_skills": 6, "internships": 1,
    "certifications": 2, "projects": 2,
    "degree": "BTech", "branch": "CS", "gender": "Male", "age": 21,
})
if submitted:
    profile = {
        "cgpa": cgpa, "aptitude_score": aptitude, "coding_skills": coding,
        "backlogs": backlogs, "communication_skills": comm, "internships": interns,
        "certifications": certs, "projects": projects,
        "degree": degree, "branch": branch, "gender": gender, "age": age,
    }
    st.session_state["student_profile"] = profile

cgpa_v   = profile["cgpa"]
apt_v    = profile["aptitude_score"]
coding_v = profile["coding_skills"]

coding_ok = coding_v >= CODING_THRESH
apt_ok    = apt_v    >= APT_THRESH
cgpa_ok   = cgpa_v   >= CGPA_THRESH
eligible  = coding_ok and apt_ok and cgpa_ok

st.markdown("---")
st.markdown("### Assessment Results")

# ── Eligibility banner ────────────────────────────────────────────────────────
if eligible:
    st.markdown(
        """<div style="background:#d1fae5; border:1px solid #10b981; border-radius:10px;
        padding:18px 22px; text-align:center; margin-bottom:16px;">
        <span style="font-size:28px;">✅</span><br>
        <strong style="font-size:18px; color:#065f46;">PLACEMENT ELIGIBLE</strong><br>
        <span style="color:#057a5a; font-size:13px;">
        All three eligibility thresholds are met. Based on dataset analysis,
        students with this profile are placed in the training data.
        </span></div>""",
        unsafe_allow_html=True,
    )
else:
    fails = []
    if not coding_ok: fails.append(f"Coding Skills ({coding_v} &lt; {CODING_THRESH})")
    if not apt_ok:    fails.append(f"Aptitude Score ({apt_v} &lt; {APT_THRESH})")
    if not cgpa_ok:   fails.append(f"CGPA ({cgpa_v:.1f} &lt; {CGPA_THRESH})")
    fail_str = " · ".join(fails)
    st.markdown(
        f"""<div style="background:#fee2e2; border:1px solid #ef4444; border-radius:10px;
        padding:18px 22px; text-align:center; margin-bottom:16px;">
        <span style="font-size:28px;">❌</span><br>
        <strong style="font-size:18px; color:#991b1b;">NOT CURRENTLY ELIGIBLE</strong><br>
        <span style="color:#7f1d1d; font-size:13px;">
        Threshold(s) not met: {fail_str}
        </span></div>""",
        unsafe_allow_html=True,
    )

# ── Threshold badges + gauges ──────────────────────────────────────────────────
b1, b2, b3 = st.columns(3)
badge = lambda ok, label: (
    f'<div style="text-align:center;"><span class="badge-{"pass" if ok else "fail"}">'
    f'{"✅" if ok else "❌"} {label}</span></div>'
)
b1.markdown(badge(coding_ok, f"Coding ≥ {CODING_THRESH} · yours: {coding_v}"), unsafe_allow_html=True)
b2.markdown(badge(apt_ok,    f"Aptitude ≥ {APT_THRESH} · yours: {apt_v}"),     unsafe_allow_html=True)
b3.markdown(badge(cgpa_ok,   f"CGPA ≥ {CGPA_THRESH} · yours: {cgpa_v:.1f}"),  unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(gauge_chart(coding_v, CODING_THRESH, "Coding Skills", 1, 10),  use_container_width=True)
with g2:
    st.plotly_chart(gauge_chart(apt_v,    APT_THRESH,    "Aptitude Score", 40, 99), use_container_width=True)
with g3:
    st.plotly_chart(gauge_chart(cgpa_v,   CGPA_THRESH,   "CGPA", 5.5, 9.8),        use_container_width=True)

st.markdown("---")

# ── Radar: student vs placed average ──────────────────────────────────────────
st.markdown("### Your Profile vs Placed Student Average")

feat_ranges = {
    "CGPA":           (5.5, 9.8),
    "Aptitude":       (40,  99),
    "Coding":         (1,   10),
    "Comm. Skills":   (1,   10),
    "Internships":    (0,   3),
    "Certifications": (0,   5),
    "Projects":       (0,   5),
    "Backlogs (inv)": (0,   3),
}
raw_keys = ["cgpa","aptitude_score","coding_skills","communication_skills",
            "internships","certifications","projects","backlogs"]

student_norm = {}
placed_norm  = {}
for label, (lo, hi), key in zip(feat_ranges.keys(), feat_ranges.values(), raw_keys):
    rng = hi - lo
    sv = profile.get(key, lo)
    pv = placed[key].mean()
    if key == "backlogs":
        student_norm[label] = round(max(0, min(1, 1 - (sv - lo) / rng)), 3)
        placed_norm[label]  = round(max(0, min(1, 1 - (pv - lo) / rng)), 3)
    else:
        student_norm[label] = round(max(0, min(1, (sv - lo) / rng)), 3)
        placed_norm[label]  = round(max(0, min(1, (pv - lo) / rng)), 3)

rc1, rc2 = st.columns([1.2, 1])
with rc1:
    st.plotly_chart(student_radar(student_norm, placed_norm), use_container_width=True)

with rc2:
    st.markdown("**Peer Percentiles (vs all 12,000 students):**")
    for feat_label, key in [("CGPA", "cgpa"), ("Aptitude Score", "aptitude_score"), ("Coding Skills", "coding_skills")]:
        pct = student_percentile(df_all, key, profile[key])
        bar_color = GREEN_COLOR if pct >= 50 else (AMBER_COLOR if pct >= 30 else UNPLACED_COLOR)
        st.markdown(f"**{feat_label}: {profile[key]:.1f}**")
        st.progress(int(pct), text=f"Top {100-pct:.0f}% · better than {pct:.0f}% of all students")

st.markdown("---")

# ── Placed student benchmark table ────────────────────────────────────────────
st.markdown("### Benchmark: You vs Placed Students")
bench = {
    "Metric":           ["CGPA", "Aptitude Score", "Coding Skills", "Comm. Skills", "Internships"],
    "Your Value":       [cgpa_v, apt_v, coding_v, profile["communication_skills"], profile["internships"]],
    "Placed 25th %ile": [placed["cgpa"].quantile(0.25), placed["aptitude_score"].quantile(0.25),
                         placed["coding_skills"].quantile(0.25), placed["communication_skills"].quantile(0.25),
                         placed["internships"].quantile(0.25)],
    "Placed Median":    [placed["cgpa"].median(), placed["aptitude_score"].median(),
                         placed["coding_skills"].median(), placed["communication_skills"].median(),
                         placed["internships"].median()],
    "Placed 75th %ile": [placed["cgpa"].quantile(0.75), placed["aptitude_score"].quantile(0.75),
                         placed["coding_skills"].quantile(0.75), placed["communication_skills"].quantile(0.75),
                         placed["internships"].quantile(0.75)],
}
bench_df = pd.DataFrame(bench)
st.dataframe(bench_df, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption(
    "⚠️ This assessment is descriptive and based on patterns in the 12,000-student training dataset. "
    "It is not a guarantee of placement or non-placement in any real recruitment process."
)
