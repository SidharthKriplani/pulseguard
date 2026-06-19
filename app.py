"""
PulseGuard Scoring API
======================
GP2 LightGBM_monotonic champion on Home Credit Default Risk (307,511 applicants,
140 features across 7 tables). Isotonic calibration via numpy interp — zero sklearn
dependency at serve time, no Python version lock.

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

import json
import os
from typing import Optional

import lightgbm as lgb
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ── Artifacts ──────────────────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
_MODEL_DIR = os.path.join(_BASE, "outputs", "models")

try:
    # Native LightGBM booster — version-agnostic, no sklearn wrapper
    _booster = lgb.Booster(model_file=os.path.join(_MODEL_DIR, "lgb_mono_champion.txt"))

    # Isotonic calibration lookup as numpy arrays (extracted from sklearn object)
    # np.interp(raw_prob, _ISO_X, _ISO_Y) exactly replicates IsotonicRegression.predict()
    _ISO_X = np.load(os.path.join(_MODEL_DIR, "iso_x.npy"))
    _ISO_Y = np.load(os.path.join(_MODEL_DIR, "iso_y.npy"))

    # Training medians for all 140 features — used to impute cross-table aggregations
    # JSON structure: {"features": [...], "medians": {name: value, ...}}
    with open(os.path.join(_MODEL_DIR, "feature_medians.json")) as _f:
        _med_data = json.load(_f)

    _FEATURE_NAMES: list[str] = _med_data["features"]          # training order
    _MEDIANS: dict[str, float] = _med_data["medians"]          # name → median

except FileNotFoundError as e:
    raise RuntimeError(
        f"Model artifact missing: {e}\n"
        "Expected: outputs/models/lgb_mono_champion.txt, iso_x.npy, iso_y.npy, feature_medians.json"
    )

# ── Score-band thresholds ──────────────────────────────────────────────────────
_GREEN_MAX = 0.20
_AMBER_MAX = 0.40


def _calibrate(raw_prob: float) -> float:
    """Isotonic calibration: piecewise-linear interp, pure numpy, no sklearn."""
    return float(np.interp(raw_prob, _ISO_X, _ISO_Y))


# ── Request schema ─────────────────────────────────────────────────────────────

class ApplicantFeatures(BaseModel):
    """
    Application-level features for GP2 LightGBM scoring.
    Cross-table history (bureau, installments, POS, credit card) is
    imputed with training-set medians — safe for single-row inference.
    """
    # Core financials (required)
    AMT_CREDIT: float = Field(..., description="Loan amount (e.g. 514822)")
    AMT_INCOME_TOTAL: float = Field(..., description="Annual income (e.g. 148500)")
    AMT_ANNUITY: float = Field(..., description="Loan annuity payment (e.g. 24930)")
    DAYS_BIRTH: int = Field(..., description="Days before application, negative (e.g. -14600 ≈ 40 yrs)")
    DAYS_EMPLOYED: int = Field(..., description="Days employed, negative; 365243 = unemployed/not applicable")

    # Optional financials
    AMT_GOODS_PRICE: Optional[float] = Field(None, description="Price of goods financed")
    OWN_CAR_AGE: Optional[float] = Field(None, description="Age of owned car in years")

    # Household
    CNT_CHILDREN: int = Field(0, description="Number of children")
    CNT_FAM_MEMBERS: float = Field(2.0, description="Number of family members")

    # External credit scores — top predictive features; all optional
    EXT_SOURCE_1: Optional[float] = Field(None, description="External bureau score 1 (0–1, higher=lower risk)")
    EXT_SOURCE_2: Optional[float] = Field(None, description="External bureau score 2 (0–1, higher=lower risk)")
    EXT_SOURCE_3: Optional[float] = Field(None, description="External bureau score 3 (~50% missing in population)")

    # Temporal
    DAYS_REGISTRATION: float = Field(-3000.0, description="Days since last registration change (negative)")
    DAYS_ID_PUBLISH: int = Field(-2000, description="Days since ID last changed (negative)")

    # Location / region
    REGION_RATING_CLIENT: int = Field(2, description="Region risk rating (1=low, 2=medium, 3=high)")
    REGION_POPULATION_RELATIVE: float = Field(0.019, description="Normalised regional population density")
    LIVE_REGION_NOT_WORK_REGION: int = Field(0, description="Lives in different region than works (0/1)")
    REG_CITY_NOT_LIVE_CITY: int = Field(0, description="Registered city ≠ living city (0/1)")

    # Contact flags
    FLAG_EMP_PHONE: int = Field(1, description="Work phone provided (0/1)")
    FLAG_WORK_PHONE: int = Field(0, description="Work phone alternative (0/1)")
    FLAG_PHONE: int = Field(1, description="Home phone provided (0/1)")

    # Social circle
    OBS_30_CNT_SOCIAL_CIRCLE: float = Field(0.0, description="Observations in social circle (30-day DPD window)")
    DEF_30_CNT_SOCIAL_CIRCLE: Optional[float] = Field(None, description="Defaults in social circle (30-day DPD)")
    DEF_60_CNT_SOCIAL_CIRCLE: Optional[float] = Field(None, description="Defaults in social circle (60-day DPD)")

    # Application metadata
    HOUR_APPR_PROCESS_START: int = Field(10, description="Hour application started (0–23)")
    FLAG_DOCUMENT_3: int = Field(0, description="Document 3 provided (0/1)")

    class Config:
        json_schema_extra = {
            "example": {
                "AMT_CREDIT": 406597,
                "AMT_INCOME_TOTAL": 202500,
                "AMT_ANNUITY": 24700,
                "AMT_GOODS_PRICE": 351000,
                "DAYS_BIRTH": -9461,
                "DAYS_EMPLOYED": -637,
                "CNT_CHILDREN": 0,
                "CNT_FAM_MEMBERS": 1,
                "EXT_SOURCE_2": 0.5117,
                "REGION_RATING_CLIENT": 2,
                "FLAG_EMP_PHONE": 1,
                "FLAG_WORK_PHONE": 0,
                "FLAG_PHONE": 1,
                "OBS_30_CNT_SOCIAL_CIRCLE": 2,
                "HOUR_APPR_PROCESS_START": 10,
                "FLAG_DOCUMENT_3": 0,
            }
        }


# ── Response schema ────────────────────────────────────────────────────────────

class ScoreResponse(BaseModel):
    pd_score: float = Field(..., description="Calibrated probability of default")
    band: str = Field(..., description="GREEN (<20% PD) | AMBER (20–40%) | RED (≥40%)")
    top_reasons: list[str] = Field(..., description="Top-5 SHAP drivers from LightGBM booster")
    disclaimer: str = Field(..., description="Regulatory constraint notice")


# ── FastAPI app ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="PulseGuard Scoring API",
    description=(
        "GP2 LightGBM_monotonic champion (Home Credit Default Risk · 307,511 applicants · "
        "140 features · 7 tables). Isotonic calibration. "
        "**ASSISTIVE_ONLY** — all outputs require human review."
    ),
    version="2.0.0",
)


@app.get("/health", tags=["ops"])
def health():
    """Liveness probe for Cloud Run / load balancer."""
    return {
        "status": "ok",
        "model": "lgb_mono_champion",
        "dataset": "home_credit_default_risk",
        "n_features": 140,
        "auc_test": 0.7769,
        "ece_test": 0.0034,
        "calibration": "isotonic",
        "version": "2.0.0",
    }


@app.post("/score", response_model=ScoreResponse, tags=["scoring"])
def score(features: ApplicantFeatures):
    """
    Score one applicant. Returns calibrated PD, score band, and top-5 SHAP reasons.

    Hard constraint: ASSISTIVE_ONLY. The model never approves or rejects an applicant.
    A qualified human officer must review all outputs before any action is taken.
    """
    raw = features.model_dump()

    # ── 1. Start with all 140 training medians ─────────────────────────────────
    fv: dict[str, float] = dict(_MEDIANS)

    # ── 2. Override with provided raw features ─────────────────────────────────
    _direct = [
        "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY",
        "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION", "DAYS_ID_PUBLISH",
        "CNT_FAM_MEMBERS", "REGION_RATING_CLIENT", "REGION_POPULATION_RELATIVE",
        "LIVE_REGION_NOT_WORK_REGION", "REG_CITY_NOT_LIVE_CITY",
        "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "FLAG_PHONE",
        "OBS_30_CNT_SOCIAL_CIRCLE", "HOUR_APPR_PROCESS_START", "FLAG_DOCUMENT_3",
    ]
    for k in _direct:
        if raw.get(k) is not None:
            fv[k] = float(raw[k])

    # Optional nullable fields
    for k in ("AMT_GOODS_PRICE", "OWN_CAR_AGE",
              "DEF_30_CNT_SOCIAL_CIRCLE", "DEF_60_CNT_SOCIAL_CIRCLE"):
        if raw.get(k) is not None:
            fv[k] = float(raw[k])

    # EXT_SOURCE — track which were supplied for mean/std computation
    ext_vals: list[float] = []
    for k in ("EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"):
        if raw.get(k) is not None:
            fv[k] = float(raw[k])
            ext_vals.append(float(raw[k]))

    # ── 3. Compute derived features (override their medians) ───────────────────
    emp = fv["DAYS_EMPLOYED"]
    flag_anomaly = 1.0 if int(emp) == 365243 else 0.0
    fv["FLAG_EMPLOYED_ANOMALY"] = flag_anomaly

    fv["CREDIT_TO_INCOME"]  = fv["AMT_CREDIT"]   / (fv["AMT_INCOME_TOTAL"] + 1.0)
    fv["ANNUITY_TO_INCOME"] = fv["AMT_ANNUITY"]  / (fv["AMT_INCOME_TOTAL"] + 1.0)
    fv["CREDIT_TO_GOODS"]   = fv["AMT_CREDIT"]   / (fv["AMT_GOODS_PRICE"]  + 1.0)
    fv["CREDIT_TO_ANNUITY"] = fv["AMT_ANNUITY"]  / (fv["AMT_CREDIT"]       + 1.0)
    fv["AGE_YEARS"]         = -fv["DAYS_BIRTH"]  / 365.0
    fv["INCOME_PER_PERSON"] = fv["AMT_INCOME_TOTAL"] / (fv["CNT_FAM_MEMBERS"] + 1.0)

    if not flag_anomaly:
        fv["EMPLOYED_YEARS"] = -emp / 365.0
    # else: keep training median for EMPLOYED_YEARS

    if ext_vals:
        fv["EXT_SOURCE_MEAN"] = float(np.mean(ext_vals))
        fv["EXT_SOURCE_STD"]  = float(np.std(ext_vals)) if len(ext_vals) > 1 else 0.0

    # BEHAVIORAL_RISK_SCORE and all cross-table features stay at training medians.

    # ── 4. Assemble 140-feature vector in exact training order ─────────────────
    X = np.array([[fv[f] for f in _FEATURE_NAMES]], dtype=np.float64)

    # ── 5. Score ───────────────────────────────────────────────────────────────
    raw_prob = float(_booster.predict(X)[0])
    pd_score = _calibrate(raw_prob)

    # ── 6. Band ────────────────────────────────────────────────────────────────
    if pd_score < _GREEN_MAX:
        band = "GREEN"
    elif pd_score < _AMBER_MAX:
        band = "AMBER"
    else:
        band = "RED"

    # ── 7. SHAP — LightGBM pred_contrib (shape: n_features + 1; last = bias) ──
    contribs = _booster.predict(X, pred_contrib=True)[0]
    shap_map = {feat: float(v) for feat, v in zip(_FEATURE_NAMES, contribs[:-1])}
    top5 = sorted(shap_map.items(), key=lambda kv: abs(kv[1]), reverse=True)[:5]

    def _fmt(feat: str, val: float) -> str:
        arrow = "↑ risk" if val > 0 else "↓ risk"
        return f"{feat}: {arrow} (SHAP={val:+.4f})"

    return ScoreResponse(
        pd_score=round(pd_score, 4),
        band=band,
        top_reasons=[_fmt(f, v) for f, v in top5],
        disclaimer=(
            "ASSISTIVE_ONLY | HUMAN_REVIEW_REQUIRED | NOT_FINAL_DECISION — "
            "Output is for analytical review only. No credit decision is made "
            "by this system. A qualified officer must review before any action."
        ),
    )
