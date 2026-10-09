# utils/charts.py
"""Reusable Plotly chart builders for the placement analytics dashboard."""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.theme import (
    PLACED_COLOR, UNPLACED_COLOR, AMBER_COLOR, GREEN_COLOR,
    PURPLE_COLOR, PALETTE, PLOTLY_LAYOUT, MUTED_COLOR, BORDER_COLOR,
    TEXT_COLOR, SURFACE_COLOR,
)


def _apply_layout(fig: go.Figure, title: str = "", height: int = 360) -> go.Figure:
    layout = dict(**PLOTLY_LAYOUT, height=height)
    if title:
        layout["title"] = dict(text=title, font=dict(size=14, color=TEXT_COLOR),
                               x=0, xanchor="left", pad=dict(l=0))
    fig.update_layout(**layout)
    return fig


# ── Overview ─────────────────────────────────────────────────────────────────

def placement_donut(df: pd.DataFrame) -> go.Figure:
    placed_n = int(df["placed"].sum())
    total    = len(df)
    not_n    = total - placed_n
    fig = go.Figure(go.Pie(
        labels=["Placed", "Not Placed"],
        values=[placed_n, not_n],
        hole=0.62,
        marker_colors=[PLACED_COLOR, UNPLACED_COLOR],
        textinfo="percent",
        textfont_size=13,
        hovertemplate="%{label}: %{value:,} students (%{percent})<extra></extra>",
    ))
    rate = placed_n / total * 100
    fig.add_annotation(
        text=f"<b>{rate:.1f}%</b><br><span style='font-size:11px;color:{MUTED_COLOR}'>Placed</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=20, color=TEXT_COLOR),
        align="center",
    )
    return _apply_layout(fig, height=300)


def correlation_bar(corr_data: dict) -> go.Figure:
    """Horizontal bar of point-biserial correlations sorted by |r|."""
    items = sorted(corr_data.items(), key=lambda x: abs(x[1]))
    labels = [i[0] for i in items]
    values = [i[1] for i in items]
    colors = [PLACED_COLOR if v > 0 else UNPLACED_COLOR for v in values]
    fig = go.Figure(go.Bar(
        y=labels, x=values, orientation="h",
        marker_color=colors,
        text=[f"{v:+.3f}" for v in values],
        textposition="outside",
        hovertemplate="%{y}: r = %{x:.4f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=BORDER_COLOR, line_width=1)
    fig.update_xaxes(range=[-0.15, 0.55], title_text="Correlation (r)")
    return _apply_layout(fig, title="Feature Correlation with Placement", height=340)


def segment_bar(df: pd.DataFrame, col: str, title: str) -> go.Figure:
    grp = df.groupby(col)["placed"].agg(["mean", "count"]).reset_index()
    grp["rate"] = grp["mean"] * 100
    grp = grp.sort_values("rate", ascending=True)
    fig = go.Figure(go.Bar(
        y=grp[col].astype(str), x=grp["rate"], orientation="h",
        marker_color=PLACED_COLOR,
        text=[f"{v:.1f}%" for v in grp["rate"]],
        textposition="outside",
        customdata=grp["count"],
        hovertemplate="%{y}: %{x:.1f}% placed (n=%{customdata:,})<extra></extra>",
    ))
    fig.update_xaxes(range=[0, min(grp["rate"].max() * 1.3, 100)],
                     title_text="Placement Rate (%)")
    return _apply_layout(fig, title=title, height=280)


# ── Placement Insights ───────────────────────────────────────────────────────

def threshold_cliff_chart(df: pd.DataFrame, col: str,
                           threshold: float, title: str,
                           x_label: str) -> go.Figure:
    """Bar chart showing the binary cliff at the given threshold."""
    if col == "cgpa":
        bins   = [5.4, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 9.81]
        labels = ["5.5–6.0","6.0–6.5","6.5–7.0","7.0–7.5","7.5–8.0",
                  "8.0–8.5","8.5–9.0","9.0–9.5","9.5–9.8"]
        df2 = df.copy()
        df2["band"] = pd.cut(df2[col], bins=bins, labels=labels, right=False)
        grp = df2.groupby("band", observed=True)["placed"].mean().reset_index()
        grp["rate"] = grp["placed"] * 100
        x_vals = grp["band"].astype(str)
        y_vals = grp["rate"]
        colors = [UNPLACED_COLOR if float(lbl.split("–")[0].replace("–","-")) < threshold
                  else PLACED_COLOR for lbl in x_vals]
    elif col == "aptitude_score":
        bins   = [39, 50, 60, 70, 80, 90, 100]
        labels = ["40–50","50–60","60–70","70–80","80–90","90–99"]
        df2 = df.copy()
        df2["band"] = pd.cut(df2[col], bins=bins, labels=labels, right=False)
        grp = df2.groupby("band", observed=True)["placed"].mean().reset_index()
        grp["rate"] = grp["placed"] * 100
        x_vals = grp["band"].astype(str)
        y_vals = grp["rate"]
        colors = [UNPLACED_COLOR if int(lbl.split("–")[0]) < threshold
                  else PLACED_COLOR for lbl in x_vals]
    else:  # coding_skills (integer 1-10)
        grp = df.groupby(col)["placed"].mean().reset_index()
        grp["rate"] = grp["placed"] * 100
        x_vals = grp[col].astype(str)
        y_vals = grp["rate"]
        colors = [UNPLACED_COLOR if int(v) < threshold else PLACED_COLOR for v in x_vals]

    fig = go.Figure(go.Bar(
        x=x_vals, y=y_vals,
        marker_color=colors,
        text=[f"{v:.0f}%" for v in y_vals],
        textposition="outside",
        hovertemplate=f"{x_label}: %{{x}}<br>Placement Rate: %{{y:.1f}}%<extra></extra>",
    ))
    # Add a threshold annotation as a shape (categorical x-axis requires shape, not add_vline)
    if col == "coding_skills":
        # find the bar index for threshold
        x_list = list(x_vals)
        try:
            thresh_idx = x_list.index(str(int(threshold)))
            fig.add_vrect(
                x0=thresh_idx - 0.5, x1=thresh_idx - 0.5,
                line_dash="dash", line_color=AMBER_COLOR, line_width=0,
            )
            fig.add_annotation(
                x=str(int(threshold)), y=65,
                text=f"Threshold ≥ {int(threshold)}",
                showarrow=False, font=dict(color=AMBER_COLOR, size=11),
                xanchor="left",
            )
        except (ValueError, IndexError):
            pass
    fig.update_yaxes(range=[0, 70], title_text="Placement Rate (%)")
    fig.update_xaxes(title_text=x_label)
    return _apply_layout(fig, title=title, height=320)


def heatmap_degree_branch(df: pd.DataFrame) -> go.Figure:
    ct = df.groupby(["degree","branch"])["placed"].mean().mul(100).round(1).unstack()
    fig = go.Figure(go.Heatmap(
        z=ct.values,
        x=ct.columns.tolist(),
        y=ct.index.tolist(),
        colorscale=[[0,"#fee2e2"],[0.5,"#fef3c7"],[1,"#d1fae5"]],
        zmin=20, zmax=40,
        text=[[f"{v:.1f}%" for v in row] for row in ct.values],
        texttemplate="%{text}",
        textfont=dict(size=12),
        hovertemplate="Degree: %{y}<br>Branch: %{x}<br>Rate: %{z:.1f}%<extra></extra>",
        showscale=True,
        colorbar=dict(title="Rate %", thickness=12),
    ))
    fig.update_xaxes(title_text="Branch")
    fig.update_yaxes(title_text="Degree")
    return _apply_layout(fig, title="Placement Rate: Degree × Branch (%)", height=280)


def root_cause_pie(df: pd.DataFrame) -> go.Figure:
    np_df = df[df["placed"] == 0]
    rc = np_df["root_cause"].value_counts().reset_index()
    rc.columns = ["cause", "count"]
    fig = go.Figure(go.Pie(
        labels=rc["cause"], values=rc["count"],
        marker_colors=[UNPLACED_COLOR, AMBER_COLOR, PURPLE_COLOR,
                       "#f97316", "#06b6d4", "#84cc16", "#ec4899"],
        textinfo="percent",
        hovertemplate="%{label}: %{value:,} students (%{percent})<extra></extra>",
    ))
    return _apply_layout(fig, title="Root Causes of Non-Placement", height=320)


# ── Skill Gap ────────────────────────────────────────────────────────────────

def skill_gap_bar(df: pd.DataFrame) -> go.Figure:
    placed    = df[df["placed"] == 1]
    not_placed = df[df["placed"] == 0]
    feats = ["aptitude_score","coding_skills","cgpa","internships",
             "certifications","projects","communication_skills","backlogs"]
    labels  = ["Aptitude Score","Coding Skills","CGPA","Internships",
               "Certifications","Projects","Comm. Skills","Backlogs"]
    gaps = [placed[f].mean() - not_placed[f].mean() for f in feats]
    order = sorted(range(len(gaps)), key=lambda i: gaps[i])
    fig = go.Figure(go.Bar(
        y=[labels[i] for i in order],
        x=[gaps[i]   for i in order],
        orientation="h",
        marker_color=[PLACED_COLOR if gaps[i] > 0.05 else
                      (UNPLACED_COLOR if gaps[i] < -0.05 else MUTED_COLOR)
                      for i in order],
        text=[f"{gaps[i]:+.3f}" for i in order],
        textposition="outside",
        hovertemplate="%{y}: gap = %{x:+.3f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=BORDER_COLOR, line_width=1)
    fig.update_xaxes(title_text="Placed Mean − Not-Placed Mean (raw units)")
    return _apply_layout(fig, title="Skill Gap: Placed vs Not Placed", height=340)


def skill_radar(placed_means: dict, unplaced_means: dict) -> go.Figure:
    categories = list(placed_means.keys())
    p_vals = list(placed_means.values())
    n_vals = list(unplaced_means.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=p_vals + [p_vals[0]], theta=categories + [categories[0]],
        fill="toself", name="Placed",
        line_color=PLACED_COLOR, fillcolor=f"rgba(59,130,212,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=n_vals + [n_vals[0]], theta=categories + [categories[0]],
        fill="toself", name="Not Placed",
        line_color=UNPLACED_COLOR, fillcolor=f"rgba(239,68,68,0.10)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin",)},
        height=360,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def box_plot_split(df: pd.DataFrame, col: str, title: str) -> go.Figure:
    placed_vals    = df[df["placed"] == 1][col]
    not_placed_vals = df[df["placed"] == 0][col]
    fig = go.Figure()
    fig.add_trace(go.Box(
        y=placed_vals, name="Placed",
        marker_color=PLACED_COLOR, boxmean=True,
        hovertemplate=f"{col}: %{{y}}<extra>Placed</extra>",
    ))
    fig.add_trace(go.Box(
        y=not_placed_vals, name="Not Placed",
        marker_color=UNPLACED_COLOR, boxmean=True,
        hovertemplate=f"{col}: %{{y}}<extra>Not Placed</extra>",
    ))
    fig.update_yaxes(title_text=col)
    return _apply_layout(fig, title=title, height=320)


def scatter_apt_vs_coding(df: pd.DataFrame) -> go.Figure:
    sample = df.sample(min(2000, len(df)), random_state=42)
    placed_s    = sample[sample["placed"] == 1]
    not_placed_s = sample[sample["placed"] == 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=not_placed_s["aptitude_score"], y=not_placed_s["coding_skills"],
        mode="markers", name="Not Placed",
        marker=dict(color=UNPLACED_COLOR, size=5, opacity=0.5),
        hovertemplate="Aptitude: %{x}<br>Coding: %{y}<extra>Not Placed</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=placed_s["aptitude_score"], y=placed_s["coding_skills"],
        mode="markers", name="Placed",
        marker=dict(color=PLACED_COLOR, size=5, opacity=0.6),
        hovertemplate="Aptitude: %{x}<br>Coding: %{y}<extra>Placed</extra>",
    ))
    fig.add_vline(x=60, line_dash="dash", line_color=AMBER_COLOR, line_width=1.5,
                  annotation_text="Aptitude=60", annotation_position="top right")
    fig.add_hline(y=5, line_dash="dash", line_color=AMBER_COLOR, line_width=1.5,
                  annotation_text="Coding=5", annotation_position="bottom right")
    fig.update_xaxes(title_text="Aptitude Score")
    fig.update_yaxes(title_text="Coding Skills")
    return _apply_layout(fig, title="Aptitude vs Coding Skills (sample n=2,000)", height=380)


# ── Student Assessment ───────────────────────────────────────────────────────

def gauge_chart(value: float, threshold: float, label: str,
                lo: float, hi: float) -> go.Figure:
    pct = min((value - lo) / (hi - lo), 1.0)
    thresh_pct = (threshold - lo) / (hi - lo)
    color = GREEN_COLOR if value >= threshold else (
        AMBER_COLOR if value >= threshold * 0.85 else UNPLACED_COLOR
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title=dict(text=label, font=dict(size=13)),
        number=dict(font=dict(size=24, color=color)),
        gauge=dict(
            axis=dict(range=[lo, hi], tickwidth=1, tickcolor=BORDER_COLOR),
            bar=dict(color=color, thickness=0.25),
            bgcolor="white",
            borderwidth=1,
            bordercolor=BORDER_COLOR,
            steps=[
                dict(range=[lo, threshold], color="#fee2e2"),
                dict(range=[threshold, hi], color="#d1fae5"),
            ],
            threshold=dict(
                line=dict(color=AMBER_COLOR, width=3),
                thickness=0.75, value=threshold,
            ),
        ),
    ))
    return _apply_layout(fig, height=220)


def student_radar(student_vals: dict, placed_avg: dict) -> go.Figure:
    cats = list(student_vals.keys())
    sv   = list(student_vals.values())
    pv   = list(placed_avg.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=sv + [sv[0]], theta=cats + [cats[0]],
        fill="toself", name="Your Profile",
        line_color=PURPLE_COLOR, fillcolor="rgba(139,92,246,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=pv + [pv[0]], theta=cats + [cats[0]],
        fill="toself", name="Placed Avg",
        line_color=PLACED_COLOR, fillcolor="rgba(59,130,212,0.10)",
        line_dash="dash",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("margin",)},
        height=340,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def threshold_progress_bar(df: pd.DataFrame) -> go.Figure:
    """Stacked bar showing % of students passing 0/1/2/3 thresholds."""
    counts = df["thresholds_met"].value_counts().sort_index()
    total  = len(df)
    fig = go.Figure()
    colors_ = [UNPLACED_COLOR, AMBER_COLOR, "#f97316", GREEN_COLOR]
    labels_ = ["0 thresholds met","1 threshold met","2 thresholds met","All 3 met (Eligible)"]
    for n in range(4):
        cnt = int(counts.get(n, 0))
        fig.add_trace(go.Bar(
            name=labels_[n], x=["Students"],
            y=[cnt / total * 100],
            marker_color=colors_[n],
            text=[f"{cnt/total*100:.1f}%"],
            textposition="inside",
            hovertemplate=f"{labels_[n]}: {cnt:,} students ({cnt/total*100:.1f}%)<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 105], title_text="% of Students")
    return _apply_layout(fig, title="Threshold Pass Distribution", height=260)
