"""
PulseGuard Scoring API
======================
G4 XGBoost Champion on synthetic Home Credit schema.
Platt-calibrated probability → score band → SHAP top-3 reasons.

DISCLAIMER
----------
ASSISTIVE_ONLY | HUMAN_REVIEW_REQUIRED | NOT_FINAL_DECISION
This endpoint is a portfolio demonstration. It does NOT make credit decisions.
All outputs require human review before any action. No real borrower data is used.

Run locally:
    uvicorn app:app --reload --port 8080

Docker / Cloud Run:
    docker build -t pulseguard-api .
    docker run -p 8080:8080 pulseguard-api
"""
from __future__ import annotations

import os
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ── Artifact paths ─────────────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
_MODEL_DIR = os.path.join(_BASE, "outputs", "models")

# Load at startup — fail fast if any artifact is missing
try:
    _preprocessor     = joblib.load(os.path.join(_MODEL_DIR, "preprocessor.pkl"))
    _calibrated_model = joblib.load(os.path.join(_MODEL_DIR, "champion_calibrated.pkl"))
    _booster = xgb.Booster()
    _booster.load_model(os.path.join(_MODEL_DIR, "champion_xgb.json"))
except FileNotFoundError as e:
    raise RuntimeError(
        f"Model artifact missing: {e}\n"
        "Run `python3 scripts/train_champion.py` first to generate artifacts."
    )

# ── Feature definitions (must match src/feature_pipeline.py exactly) ───────────
NUMERIC_COLS = [
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",               # ~50% missing OK
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",            # ~1% missing OK
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",              # use 365243 for unemployed
    "REGION_POPULATION_RELATIVE",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",
    "DEF_30_CNT_SOCIAL_CIRCLE",   # ~3% missing OK
    "DEF_60_CNT_SOCIAL_CIRCLE",   # ~3% missing OK
    "OBS_30_CNT_SOCIAL_CIRCLE",
    "FLAG_DOCUMENT_3",
    "HOUR_APPR_PROCESS_START",
    "LIVE_REGION_NOT_WORK_REGION",
    "REGION_RATING_CLIENT",
]

CATEGORICAL_COLS = [
    "CODE_GENDER",
    "NAME_INCOME_TYPE",
    "NAME_CONTRACT_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS",
    "FLAG_OWN_CAR",
    "FLAG_OWN_REALTY",
    "ORGANIZATION_TYPE",
]

# ColumnTransformer output order: numeric block first, then categorical
FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS   # 28 features total

# Score-band thresholds (PD-semantic, from G7 threshold policy)
GREEN_MAX = 0.20
AMBER_MAX = 0.40


# ── Request schema ─────────────────────────────────────────────────────────────

class ApplicantFeatures(BaseModel):
    """
    28-feature input for PulseGuard scoring. Mirrors the synthetic Home Credit schema.
    Fields marked Optional accept null/missing values; the preprocessor imputes medians.
    """
    # ── Numeric ───────────────────────────────────────────────────────────────
    EXT_SOURCE_2: Optional[float] = Field(
        None, description="External credit bureau score 2 (range 0–1; higher = lower risk)"
    )
    EXT_SOURCE_3: Optional[float] = Field(
        None, description="External credit bureau score 3 (~50% missing in real data)"
    )
    AMT_CREDIT: float = Field(..., description="Loan credit amount (e.g. 450000)")
    AMT_INCOME_TOTAL: float = Field(..., description="Annual income (e.g. 135000)")
    AMT_ANNUITY: float = Field(..., description="Loan annuity (e.g. 20250)")
    AMT_GOODS_PRICE: Optional[float] = Field(
        None, description="Price of goods financed (~1% missing)"
    )
    DAYS_BIRTH: int = Field(
        ..., description="Days before application, negative (e.g. -15000 ≈ 41 years old)"
    )
    DAYS_EMPLOYED: int = Field(
        ..., description="Days before application, negative; use 365243 if unemployed"
    )
    REGION_POPULATION_RELATIVE: float = Field(
        0.019, description="Normalised regional population"
    )
    DAYS_REGISTRATION: float = Field(
        -3000.0, description="Days since last registration change (negative)"
    )
    DAYS_ID_PUBLISH: int = Field(-2000, description="Days since ID was changed (negative)")
    CNT_CHILDREN: int = Field(0, description="Number of children")
    CNT_FAM_MEMBERS: float = Field(2.0, description="Number of family members")
    DEF_30_CNT_SOCIAL_CIRCLE: Optional[float] = Field(
        None, description="Defaults (30 DPD) in social circle (~3% missing)"
    )
    DEF_60_CNT_SOCIAL_CIRCLE: Optional[float] = Field(
        None, description="Defaults (60 DPD) in social circle (~3% missing)"
    )
    OBS_30_CNT_SOCIAL_CIRCLE: float = Field(0.0, description="Observations in social circle (30 DPD)")
    FLAG_DOCUMENT_3: int = Field(0, description="Document 3 provided (0/1)")
    HOUR_APPR_PROCESS_START: int = Field(10, description="Hour application started (0–23)")
    LIVE_REGION_NOT_WORK_REGION: int = Field(0, description="Lives in different region than work (0/1)")
    REGION_RATING_CLIENT: int = Field(2, description="Region risk rating (1=low, 3=high)")

    # ── Categorical ───────────────────────────────────────────────────────────
    CODE_GENDER: str = Field("M", description="M or F")
    NAME_INCOME_TYPE: str = Field(
        "Working",
        description="Working | Commercial associate | Pensioner | State servant | Unemployed"
    )
    NAME_CONTRACT_TYPE: str = Field(
        "Cash loans", description="Cash loans | Revolving loans"
    )
    NAME_EDUCATION_TYPE: str = Field(
        "Secondary / secondary special",
        description="Secondary / secondary special | Higher education | Incomplete higher | Lower secondary"
    )
    NAME_FAMILY_STATUS: str = Field(
        "Married",
        description="Married | Single / not married | Civil marriage | Widow"
    )
    FLAG_OWN_CAR: str = Field("N", description="Y or N")
    FLAG_OWN_REALTY: str = Field("Y", description="Y or N")
    ORGANIZATION_TYPE: str = Field(
        "Business Entity Type 3",
        description="Employer organisation type (e.g. Business Entity Type 3, School, Government)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "EXT_SOURCE_2": 0.55,
                "EXT_SOURCE_3": None,
                "AMT_CREDIT": 450000,
                "AMT_INCOME_TOTAL": 135000,
                "AMT_ANNUITY": 20250,
                "AMT_GOODS_PRICE": 450000,
                "DAYS_BIRTH": -14600,
                "DAYS_EMPLOYED": -2000,
                "REGION_POPULATION_RELATIVE": 0.019,
                "DAYS_REGISTRATION": -3000,
                "DAYS_ID_PUBLISH": -2000,
                "CNT_CHILDREN": 0,
                "CNT_FAM_MEMBERS": 2,
                "DEF_30_CNT_SOCIAL_CIRCLE": None,
                "DEF_60_CNT_SOCIAL_CIRCLE": None,
                "OBS_30_CNT_SOCIAL_CIRCLE": 2,
                "FLAG_DOCUMENT_3": 1,
                "HOUR_APPR_PROCESS_START": 10,
                "LIVE_REGION_NOT_WORK_REGION": 0,
                "REGION_RATING_CLIENT": 2,
                "CODE_GENDER": "F",
                "NAME_INCOME_TYPE": "Working",
                "NAME_CONTRACT_TYPE": "Cash loans",
                "NAME_EDUCATION_TYPE": "Higher education",
                "NAME_FAMILY_STATUS": "Married",
                "FLAG_OWN_CAR": "N",
                "FLAG_OWN_REALTY": "Y",
                "ORGANIZATION_TYPE": "Business Entity Type 3"
            }
        }


# ── Response schema ────────────────────────────────────────────────────────────

class ScoreResponse(BaseModel):
    pd_score:    float = Field(..., description="Calibrated probability of default (Platt sigmoid, ECE=0.004)")
    band:        str   = Field(..., description="GREEN (<20% PD) | AMBER (20–40%) | RED (≥40%)")
    top_reasons: list[str] = Field(..., description="Top-3 SHAP drivers (from underlying XGBoost booster)")
    disclaimer:  str   = Field(..., description="Regulatory constraint notice")


# ── FastAPI application ────────────────────────────────────────────────────────

app = FastAPI(
    title="PulseGuard Scoring API",
    description=(
        "G4 XGBoost champion (synthetic Home Credit schema) with Platt calibration. "
        "**ASSISTIVE_ONLY** — outputs require human review; no credit decision is automated."
    ),
    version="1.0.0",
)


@app.get("/health", tags=["ops"])
def health():
    """Liveness probe for Cloud Run / load balancer."""
    return {
        "status":    "ok",
        "model":     "G4_XGBoost_Platt_Sigmoid",
        "dataset":   "synthetic_home_credit_like",
        "n_features": len(FEATURE_COLS),
        "auc_test":  0.6261,
        "ece_test":  0.00386,
    }


@app.post("/score", response_model=ScoreResponse, tags=["scoring"])
def score(features: ApplicantFeatures):
    """
    Score one applicant. Returns calibrated PD, score band, and top-3 SHAP reasons.

    **Hard constraint**: output is ASSISTIVE_ONLY. The LLM/model never approves or
    rejects an applicant. A human officer must review before any action.
    """
    # ── 1. Build DataFrame in correct column order ─────────────────────────────
    row = features.model_dump()
    df  = pd.DataFrame([row])[FEATURE_COLS]

    # ── 2. Preprocess (impute + ordinal-encode) ────────────────────────────────
    try:
        X = _preprocessor.transform(df)          # shape (1, 28)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Preprocessing failed — check categorical values: {exc}"
        )

    # ── 3. Calibrated probability ──────────────────────────────────────────────
    pd_score = float(_calibrated_model.predict_proba(X)[0, 1])

    # ── 4. Score band ──────────────────────────────────────────────────────────
    if pd_score < GREEN_MAX:
        band = "GREEN"
    elif pd_score < AMBER_MAX:
        band = "AMBER"
    else:
        band = "RED"

    # ── 5. SHAP top-3 (raw XGBoost booster, pred_contribs) ────────────────────
    # Note: SHAP is from the uncalibrated booster (log-odds space).
    # Direction and ranking remain correct; magnitude reflects raw score contribution.
    dmat     = xgb.DMatrix(X)
    contribs = _booster.predict(dmat, pred_contribs=True)[0]  # shape (29,); last = bias
    shap_map = {feat: float(val) for feat, val in zip(FEATURE_COLS, contribs[:-1])}
    top3     = sorted(shap_map.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]

    def _fmt_reason(feat: str, shap_val: float) -> str:
        direction = "increased" if shap_val > 0 else "decreased"
        return f"{feat} {direction} default risk (SHAP={shap_val:+.4f})"

    top_reasons = [_fmt_reason(f, v) for f, v in top3]

    return ScoreResponse(
        pd_score=round(pd_score, 4),
        band=band,
        top_reasons=top_reasons,
        disclaimer=(
            "ASSISTIVE_ONLY | HUMAN_REVIEW_REQUIRED | NOT_FINAL_DECISION — "
            "This output is for analytical review only. No credit decision is made "
            "by this system. A qualified officer must review before any action."
        ),
    )
