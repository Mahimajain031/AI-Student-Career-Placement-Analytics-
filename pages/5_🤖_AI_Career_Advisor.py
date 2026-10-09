# pages/5_🤖_AI_Career_Advisor.py
"""AI Career Advisor – rule-based, data-driven career guidance."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.theme import KPI_CSS, PLACED_COLOR, UNPLACED_COLOR, AMBER_COLOR, GREEN_COLOR, PLOTLY_LAYOUT
from utils.data_loader import load_data, CODING_THRESH, APT_THRESH, CGPA_THRESH

st.set_page_config(page_title="AI Career Advisor · Analytics",
                   page_icon="🤖", layout="wide")
st.markdown(KPI_CSS, unsafe_allow_html=True)

df_all = load_data()
placed = df_all[df_all["placed"] == 1]

st.markdown("## 🤖 AI Career Advisor")
st.markdown(
    "Personalised, data-driven improvement recommendations grounded in the dataset. "
    "Advice is generated from the student profile entered in the **Student Assessment** page."
)
st.markdown("---")

# ── Get profile from session state ────────────────────────────────────────────
profile = st.session_state.get("student_profile", None)

if profile is None:
    st.info("👈 Please enter a student profile on the **Student Assessment** page first, then return here.")
    st.stop()

cgpa_v   = profile["cgpa"]
apt_v    = profile["aptitude_score"]
coding_v = profile["coding_skills"]

coding_ok = coding_v >= CODING_THRESH
apt_ok    = apt_v    >= APT_THRESH
cgpa_ok   = cgpa_v   >= CGPA_THRESH
eligible  = coding_ok and apt_ok and cgpa_ok

# ── Show current profile summary ──────────────────────────────────────────────
st.markdown("### Current Profile")
p1, p2, p3, p4 = st.columns(4)
p1.metric("CGPA",          f"{cgpa_v:.1f}",  delta=f"{cgpa_v - CGPA_THRESH:.1f} vs threshold")
p2.metric("Aptitude",      f"{apt_v}",        delta=f"{apt_v - APT_THRESH} vs threshold")
p3.metric("Coding Skills", f"{coding_v}",     delta=f"{coding_v - CODING_THRESH} vs threshold")
p4.metric("Eligibility",
          "✅ Eligible" if eligible else "❌ Not Eligible",
          delta=None)

st.markdown("---")

# ── Priority action cards ─────────────────────────────────────────────────────
st.markdown("### 📋 Prioritised Improvement Plan")
st.caption(
    "Recommendations are ranked by statistical impact on placement. "
    "Only factors with a statistically significant relationship (p < 0.001) are prioritised."
)

actions = []

# --- Coding skills ---
if not coding_ok:
    gap     = CODING_THRESH - coding_v
    urgency = "high"
    actions.append({
        "priority": 1,
        "urgency":  urgency,
        "title":    f"🚨 Priority 1 — Improve Coding Skills (current: {coding_v}, need: ≥ {CODING_THRESH})",
        "body": (
            f"Your coding skills score of **{coding_v}** is below the eligibility threshold of **{CODING_THRESH}**. "
            f"You need to improve by **{gap} point(s)**. This is the **strongest predictor** of placement "
            f"(r = 0.46, p < 0.001) and the most common reason students are not placed. "
            f"\n\n**Suggested actions:**\n"
            f"- Practise data structures and algorithms daily (LeetCode easy → medium)\n"
            f"- Complete at least 2 coding mini-projects to demonstrate application\n"
            f"- Take a structured online course in your primary programming language\n"
            f"- Target: reach score **{CODING_THRESH}** to unlock placement eligibility"
        ),
    })
elif coding_v < 8:
    actions.append({
        "priority": len(actions) + 2,
        "urgency":  "low",
        "title":    f"✅ Coding Skills Met — Aim Higher (current: {coding_v})",
        "body": (
            f"You meet the coding threshold. The median coding score of placed students is **8**. "
            f"Reaching 8+ strengthens your position relative to peers.\n\n"
            f"**Suggested actions:**\n"
            f"- Attempt medium-to-hard algorithmic problems\n"
            f"- Contribute to an open-source project"
        ),
    })

# --- Aptitude ---
if not apt_ok:
    gap = APT_THRESH - apt_v
    actions.append({
        "priority": 2 if coding_ok else 2,
        "urgency":  "high" if not coding_ok and not apt_ok else "medium",
        "title":    f"⚠️  Priority — Improve Aptitude Score (current: {apt_v}, need: ≥ {APT_THRESH})",
        "body": (
            f"Your aptitude score of **{apt_v}** is below the threshold of **{APT_THRESH}**. "
            f"You need to improve by **{gap} point(s)**. Aptitude is the **second strongest predictor** "
            f"(r = 0.39, p < 0.001). The average aptitude score of placed students is **79.6**."
            f"\n\n**Suggested actions:**\n"
            f"- Practise quantitative aptitude questions daily (30–45 min)\n"
            f"- Focus on number series, percentages, time & work, logical reasoning\n"
            f"- Take 2–3 full mock aptitude tests per week\n"
            f"- Target: reach **{APT_THRESH}** within 4–6 weeks of consistent practice"
        ),
    })
elif apt_v < 80:
    actions.append({
        "priority": len(actions) + 2,
        "urgency":  "low",
        "title":    f"✅ Aptitude Met — Aim for 80+ (current: {apt_v})",
        "body": (
            f"You meet the aptitude threshold. The median of placed students is **80**. "
            f"Scoring 80+ puts you comfortably above the minimum.\n\n"
            f"**Suggested actions:**\n"
            f"- Continue with occasional timed practice tests\n"
            f"- Work on verbal reasoning alongside quant"
        ),
    })

# --- CGPA ---
if not cgpa_ok:
    gap = CGPA_THRESH - cgpa_v
    actions.append({
        "priority": 3 if (coding_ok or apt_ok) else 3,
        "urgency":  "medium",
        "title":    f"📚 Priority — Raise CGPA (current: {cgpa_v:.1f}, need: ≥ {CGPA_THRESH})",
        "body": (
            f"Your CGPA of **{cgpa_v:.1f}** is below the threshold of **{CGPA_THRESH}**. "
            f"You need to improve by **{gap:.1f} points** (r = 0.27, p < 0.001). "
            f"While CGPA is the third-ranked predictor, it is a hard gate — no student below 6.5 "
            f"is placed in this dataset regardless of other scores."
            f"\n\n**Suggested actions:**\n"
            f"- Identify your lowest-scoring subjects and seek targeted support\n"
            f"- Consistently attend and submit all coursework on time\n"
            f"- Form study groups for technical subjects\n"
            f"- A semester-on-semester improvement plan is more realistic than a sudden jump"
        ),
    })
elif cgpa_v < 8.0:
    actions.append({
        "priority": len(actions) + 2,
        "urgency":  "low",
        "title":    f"✅ CGPA Met — Target 8.0+ (current: {cgpa_v:.1f})",
        "body": (
            f"You meet the CGPA threshold. The median CGPA of placed students is **8.13**. "
            f"Improving from {cgpa_v:.1f} to 8.0+ is achievable and strengthens your overall profile.\n\n"
            f"**Suggested actions:**\n"
            f"- Focus on core technical subjects for the highest ROI\n"
            f"- Back-calculate which scores you need to hit your target CGPA"
        ),
    })

# --- All thresholds met ---
if eligible:
    actions.insert(0, {
        "priority": 0,
        "urgency":  "ok",
        "title":    "🌟 All Eligibility Thresholds Met",
        "body": (
            f"Your profile meets all three placement eligibility thresholds. "
            f"Based on the dataset, students with this profile are placed.\n\n"
            f"**To maximise your opportunities:**\n"
            f"- Continue strengthening coding skills (placed median: 8, yours: {coding_v})\n"
            f"- Maintain CGPA trajectory (placed median: 8.13, yours: {cgpa_v:.1f})\n"
            f"- Build a strong project portfolio and GitHub presence\n"
            f"- Prepare for technical interviews — the eligibility threshold is a screening gate, "
            f"not a guarantee of selection in any specific company"
        ),
    })

# Render action cards
card_class = {"high": "action-high", "medium": "action-medium",
              "low":  "action-low",  "ok":     "action-low"}
for action in sorted(actions, key=lambda x: x["priority"]):
    cls = card_class.get(action["urgency"], "action-medium")
    st.markdown(
        f'<div class="action-card {cls}">'
        f'<strong style="font-size:14px;">{action["title"]}</strong>'
        f"</div>",
        unsafe_allow_html=True,
    )
    with st.expander("See details and suggested actions →", expanded=(action["urgency"] == "high")):
        st.markdown(action["body"])

st.markdown("---")

# ── Progress-to-threshold visualisation ───────────────────────────────────────
st.markdown("### Progress to Eligibility Thresholds")

def progress_bar_chart(label, current, threshold, lo, hi, color):
    pct_curr  = min((current - lo) / (hi - lo) * 100, 100)
    pct_thresh = (threshold - lo) / (hi - lo) * 100
    fig = go.Figure()
    # background bar
    fig.add_trace(go.Bar(x=[100], y=[label], orientation="h",
                         marker_color="#f3f4f6", showlegend=False,
                         hoverinfo="skip"))
    # progress bar
    fig.add_trace(go.Bar(x=[pct_curr], y=[label], orientation="h",
                         marker_color=color, name=label,
                         hovertemplate=f"{label}: {current} ({pct_curr:.0f}% of range)<extra></extra>"))
    # threshold line
    fig.add_vline(x=pct_thresh, line_dash="dash", line_color=AMBER_COLOR, line_width=2,
                  annotation_text=f"Threshold={threshold}", annotation_position="top right",
                  annotation_font_size=10)
    fig.update_layout(
        barmode="overlay", height=90,
        margin=dict(l=10, r=80, t=10, b=10),
        xaxis=dict(range=[0, 110], showticklabels=False),
        yaxis=dict(showticklabels=True),
        showlegend=False,
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(size=12),
    )
    return fig

for lbl, curr, thresh, lo, hi, clr in [
    ("Coding Skills",  coding_v, CODING_THRESH, 1,   10, PLACED_COLOR if coding_ok else UNPLACED_COLOR),
    ("Aptitude Score", apt_v,    APT_THRESH,    40,  99, PLACED_COLOR if apt_ok    else UNPLACED_COLOR),
    ("CGPA",           cgpa_v,   CGPA_THRESH,   5.5, 9.8, PLACED_COLOR if cgpa_ok  else UNPLACED_COLOR),
]:
    st.plotly_chart(progress_bar_chart(lbl, curr, thresh, lo, hi, clr), use_container_width=True)

st.markdown("---")

# ── Benchmark table ────────────────────────────────────────────────────────────
st.markdown("### Benchmark vs Placed Student Percentiles")
bench = pd.DataFrame({
    "Feature":           ["CGPA", "Aptitude Score", "Coding Skills"],
    "Your Score":        [f"{cgpa_v:.1f}", f"{apt_v}", f"{coding_v}"],
    "Placed 25th %ile":  [f"{placed['cgpa'].quantile(0.25):.1f}",
                          f"{placed['aptitude_score'].quantile(0.25):.0f}",
                          f"{placed['coding_skills'].quantile(0.25):.0f}"],
    "Placed Median":     [f"{placed['cgpa'].median():.1f}",
                          f"{placed['aptitude_score'].median():.0f}",
                          f"{placed['coding_skills'].median():.0f}"],
    "Placed 75th %ile":  [f"{placed['cgpa'].quantile(0.75):.1f}",
                          f"{placed['aptitude_score'].quantile(0.75):.0f}",
                          f"{placed['coding_skills'].quantile(0.75):.0f}"],
    "Threshold":         [f"≥ {CGPA_THRESH}", f"≥ {APT_THRESH}", f"≥ {CODING_THRESH}"],
    "Status":            [
        "✅ Pass" if cgpa_ok   else f"❌ Need +{CGPA_THRESH - cgpa_v:.1f}",
        "✅ Pass" if apt_ok    else f"❌ Need +{APT_THRESH - apt_v}",
        "✅ Pass" if coding_ok else f"❌ Need +{CODING_THRESH - coding_v}",
    ],
})
st.dataframe(bench, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown(
    """<div class="warn-box">
    <strong>Important disclaimer:</strong> This advisor is entirely rule-based and draws on statistical
    patterns in the 12,000-student training dataset. It does <em>not</em> predict placement at any specific
    company. Placement eligibility in real recruitment also depends on soft skills, interview performance,
    available roles, and company-specific criteria not captured in this dataset.
    Advice about communication skills, internships, projects and certifications is supplementary — these
    features show no statistically significant relationship with placement in this dataset (p &gt; 0.05).
    </div>""",
    unsafe_allow_html=True,
)
