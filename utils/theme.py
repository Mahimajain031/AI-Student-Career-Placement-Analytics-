# utils/theme.py
"""Shared colour palette and Plotly layout defaults."""

# ── Colour palette ──────────────────────────────────────────────────────────
PLACED_COLOR    = "#3b82d4"   # blue  – placed / positive
UNPLACED_COLOR  = "#ef4444"   # red   – not placed / gap / fail
AMBER_COLOR     = "#f59e0b"   # amber – borderline / moderate
GREEN_COLOR     = "#10b981"   # green – strong / pass
PURPLE_COLOR    = "#8b5cf6"   # purple – accent
SURFACE_COLOR   = "#f7f8fa"   # card background
BORDER_COLOR    = "#e5e7eb"
TEXT_COLOR      = "#1f2328"
MUTED_COLOR     = "#57606a"

PALETTE = [PLACED_COLOR, UNPLACED_COLOR, AMBER_COLOR, GREEN_COLOR,
           PURPLE_COLOR, "#f97316", "#06b6d4", "#84cc16"]

# ── Plotly figure defaults ───────────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_white"

PLOTLY_LAYOUT = dict(
    template=PLOTLY_TEMPLATE,
    font=dict(family="-apple-system, Segoe UI, sans-serif", size=12, color=TEXT_COLOR),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor=BORDER_COLOR,
        font_size=12,
    ),
)

# ── KPI card CSS (injected once) ─────────────────────────────────────────────
KPI_CSS = """
<style>
.kpi-card {
    background: #f7f8fa;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 18px 20px 14px;
    text-align: center;
}
.kpi-label {
    font-size: 12px;
    color: #57606a;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 30px;
    font-weight: 700;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 12px;
    color: #57606a;
    margin-top: 4px;
}
.badge-pass {
    background: #d1fae5;
    color: #065f46;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 700;
}
.badge-fail {
    background: #fee2e2;
    color: #991b1b;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 700;
}
.badge-warn {
    background: #fef3c7;
    color: #92400e;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 700;
}
.insight-box {
    background: #eff6ff;
    border-left: 4px solid #3b82d4;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 13px;
    margin: 8px 0;
}
.warn-box {
    background: #fefce8;
    border-left: 4px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 13px;
    margin: 8px 0;
}
.action-card {
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.action-high   { background: #fee2e2; border-left: 4px solid #ef4444; }
.action-medium { background: #fef3c7; border-left: 4px solid #f59e0b; }
.action-low    { background: #d1fae5; border-left: 4px solid #10b981; }
</style>
"""


def kpi_card(label: str, value: str, sub: str = "", color: str = TEXT_COLOR) -> str:
    """Return HTML for a single KPI card."""
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value" style="color:{color};">{value}</div>'
        + (f'<div class="kpi-sub">{sub}</div>' if sub else "")
        + "</div>"
    )
