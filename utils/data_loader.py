# utils/data_loader.py
"""Data loading, caching, computed columns, and filter helpers."""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

DATA_PATH = Path(__file__).parent.parent / "student_placement_clean.csv"

# ── Verified thresholds (100 % accuracy on 12,000-row dataset) ───────────────
CODING_THRESH  = 5
APT_THRESH     = 60
CGPA_THRESH    = 6.5


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load CSV and add all computed columns once per session."""
    df = pd.read_csv(DATA_PATH)

    # -- dtype clean-up -------------------------------------------------------
    df["placed"]               = df["placed"].astype(int)
    df["coding_skills"]        = df["coding_skills"].astype(int)
    df["communication_skills"] = df["communication_skills"].astype(int)
    df["aptitude_score"]       = df["aptitude_score"].astype(int)
    df["backlogs"]             = df["backlogs"].astype(int)
    df["internships"]          = df["internships"].astype(int)
    df["certifications"]       = df["certifications"].astype(int)
    df["projects"]             = df["projects"].astype(int)
    df["age"]                  = df["age"].astype(int)
    df["cgpa"]                 = df["cgpa"].astype(float)

    # -- placement threshold flags --------------------------------------------
    df["coding_pass"] = (df["coding_skills"] >= CODING_THRESH).astype(int)
    df["apt_pass"]    = (df["aptitude_score"] >= APT_THRESH).astype(int)
    df["cgpa_pass"]   = (df["cgpa"]           >= CGPA_THRESH).astype(int)
    df["thresholds_met"] = df["coding_pass"] + df["apt_pass"] + df["cgpa_pass"]

    # placement_rule perfectly matches placed in this dataset
    df["placement_rule"] = (
        (df["coding_skills"] >= CODING_THRESH) &
        (df["aptitude_score"] >= APT_THRESH) &
        (df["cgpa"]           >= CGPA_THRESH)
    ).astype(int)

    # -- CGPA bands -----------------------------------------------------------
    cgpa_bins   = [5.4, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 9.81]
    cgpa_labels = ["5.5–6.0","6.0–6.5","6.5–7.0","7.0–7.5","7.5–8.0",
                   "8.0–8.5","8.5–9.0","9.0–9.5","9.5–9.8"]
    df["cgpa_band"] = pd.cut(df["cgpa"], bins=cgpa_bins,
                             labels=cgpa_labels, right=False)

    # -- Aptitude bands -------------------------------------------------------
    apt_bins   = [39, 50, 60, 70, 80, 90, 100]
    apt_labels = ["40–50","50–60","60–70","70–80","80–90","90–99"]
    df["apt_band"] = pd.cut(df["aptitude_score"], bins=apt_bins,
                            labels=apt_labels, right=False)

    # -- root cause of non-placement (for not-placed students) ----------------
    conditions = [
        ( (df["coding_skills"]<CODING_THRESH) & (df["aptitude_score"]>=APT_THRESH) & (df["cgpa"]>=CGPA_THRESH), "Only Coding < 5"),
        ( (df["coding_skills"]>=CODING_THRESH) & (df["aptitude_score"]<APT_THRESH) & (df["cgpa"]>=CGPA_THRESH), "Only Aptitude < 60"),
        ( (df["coding_skills"]>=CODING_THRESH) & (df["aptitude_score"]>=APT_THRESH) & (df["cgpa"]<CGPA_THRESH), "Only CGPA < 6.5"),
        ( (df["coding_skills"]<CODING_THRESH) & (df["aptitude_score"]<APT_THRESH) & (df["cgpa"]>=CGPA_THRESH),  "Coding + Aptitude Fail"),
        ( (df["coding_skills"]<CODING_THRESH) & (df["aptitude_score"]>=APT_THRESH) & (df["cgpa"]<CGPA_THRESH),  "Coding + CGPA Fail"),
        ( (df["coding_skills"]>=CODING_THRESH) & (df["aptitude_score"]<APT_THRESH) & (df["cgpa"]<CGPA_THRESH),  "Aptitude + CGPA Fail"),
        ( (df["coding_skills"]<CODING_THRESH) & (df["aptitude_score"]<APT_THRESH) & (df["cgpa"]<CGPA_THRESH),   "All Three Fail"),
    ]
    df["root_cause"] = "Placed"
    for mask, label in conditions:
        df.loc[mask & (df["placed"] == 0), "root_cause"] = label

    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filter dict to dataframe."""
    out = df.copy()
    if filters.get("degree"):
        out = out[out["degree"].isin(filters["degree"])]
    if filters.get("branch"):
        out = out[out["branch"].isin(filters["branch"])]
    if filters.get("gender"):
        out = out[out["gender"].isin(filters["gender"])]
    if filters.get("age"):
        lo, hi = filters["age"]
        out = out[(out["age"] >= lo) & (out["age"] <= hi)]
    if filters.get("placed_status") and filters["placed_status"] != "All":
        val = 1 if filters["placed_status"] == "Placed" else 0
        out = out[out["placed"] == val]
    return out


def get_filter_defaults(df: pd.DataFrame) -> dict:
    return {
        "degree":        sorted(df["degree"].unique().tolist()),
        "branch":        sorted(df["branch"].unique().tolist()),
        "gender":        sorted(df["gender"].unique().tolist()),
        "age":           (int(df["age"].min()), int(df["age"].max())),
        "placed_status": "All",
    }


def placement_rate(df: pd.DataFrame) -> float:
    return df["placed"].mean() * 100 if len(df) > 0 else 0.0


def threshold_pass_rates(df: pd.DataFrame) -> dict:
    n = len(df)
    return {
        "coding": df["coding_pass"].sum() / n * 100 if n else 0,
        "apt":    df["apt_pass"].sum()    / n * 100 if n else 0,
        "cgpa":   df["cgpa_pass"].sum()   / n * 100 if n else 0,
    }


def student_percentile(df: pd.DataFrame, col: str, val: float) -> float:
    """Return percentile rank of val within col across all 12k students."""
    return (df[col] < val).mean() * 100
