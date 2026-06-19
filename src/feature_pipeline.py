"""
G4 — Feature Pipeline
PulseGuard · Model-Ready Feature Engineering

Transforms the calibrated synthetic_home_credit_like dataset into model-ready
feature arrays. Fit preprocessing on train only; apply to val/test without refitting.

Excluded from training features (hard rule — no injected leakage):
  - SK_ID_CURR          (applicant ID)
  - TARGET              (label)
  - SPLIT               (data split marker)
  - APPLICATION_DATE    (outcome timestamp)
  - FEATURE_TIMESTAMP_EXT_SOURCE_2   (synthetic timestamp)
  - FEATURE_TIMESTAMP_INJECTED_LEAK  (synthetic timestamp)
  - EXTERNAL_BUREAU_QUERY_RESULT__INJECTED  (injected leakage feature — G3 FAIL)
  - EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC (FOIR input, not model feature)

Training features: 20 numeric + 8 categorical = 28 total

Usage:
  from src.feature_pipeline import build_features, NUMERIC_COLS, CATEGORICAL_COLS
  X_train, y_train, preprocessor = build_features(df_train, fit=True)
  X_val,   y_val,   _            = build_features(df_val,   fit=False, preprocessor=preprocessor)
"""

from __future__ import annotations  # Python 3.9 compat: enables X | Y type hint syntax

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


# ── Column definitions ─────────────────────────────────────────────────────────

# Columns explicitly excluded from model features
EXCLUDED_COLS = [
    "SK_ID_CURR",
    "TARGET",
    "SPLIT",
    "APPLICATION_DATE",
    "FEATURE_TIMESTAMP_EXT_SOURCE_2",
    "FEATURE_TIMESTAMP_INJECTED_LEAK",
    "EXTERNAL_BUREAU_QUERY_RESULT__INJECTED",   # G3 leakage FAIL — hard excluded
    "EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC",  # FOIR input — not a model feature
]

# Numeric features (may have missing values — imputed with median)
NUMERIC_COLS = [
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",                # 50% missing → median impute
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",             # ~1% missing → median impute
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",               # sentinel 365243 for unemployed; retained as-is
    "REGION_POPULATION_RELATIVE",
    "DAYS_REGISTRATION",
    "DAYS_ID_PUBLISH",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",
    "DEF_30_CNT_SOCIAL_CIRCLE",    # ~3% missing → median impute
    "DEF_60_CNT_SOCIAL_CIRCLE",    # ~3% missing → median impute
    "OBS_30_CNT_SOCIAL_CIRCLE",
    "FLAG_DOCUMENT_3",
    "HOUR_APPR_PROCESS_START",
    "LIVE_REGION_NOT_WORK_REGION",
    "REGION_RATING_CLIENT",
]

# Categorical features (ordinal encoded; unknown categories → "UNKNOWN")
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

FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS   # 28 features total

# Feature metadata for audit trail
FEATURE_METADATA = {
    "n_numeric":           len(NUMERIC_COLS),
    "n_categorical":       len(CATEGORICAL_COLS),
    "n_total":             len(FEATURE_COLS),
    "numeric_cols":        NUMERIC_COLS,
    "categorical_cols":    CATEGORICAL_COLS,
    "excluded_cols":       EXCLUDED_COLS,
    "leakage_excluded":    ["EXTERNAL_BUREAU_QUERY_RESULT__INJECTED"],
    "synthetic_excluded":  ["EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC"],
    "imputation_strategy": "median for numeric; most_frequent for categorical",
    "encoding_strategy":   "OrdinalEncoder (unknown categories → -1)",
    "scaling":             "None — XGBoost is scale-invariant",
    "data_type":           "synthetic_home_credit_like",
    "calibrated_dgp_intercept": -4.20703,
}


def build_preprocessor() -> ColumnTransformer:
    """Build (unfitted) sklearn ColumnTransformer for numeric + categorical features."""
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1,
            dtype=np.float64,
        )),
    ])
    preprocessor = ColumnTransformer([
        ("numeric",      numeric_pipeline,      NUMERIC_COLS),
        ("categorical",  categorical_pipeline,  CATEGORICAL_COLS),
    ], remainder="drop")
    return preprocessor


def build_features(
    df: pd.DataFrame,
    fit: bool = True,
    preprocessor: ColumnTransformer | None = None,
) -> tuple[np.ndarray, np.ndarray | None, ColumnTransformer]:
    """
    Transform df into model-ready (X, y) arrays.

    Parameters
    ----------
    df          : DataFrame containing at minimum FEATURE_COLS columns.
    fit         : If True, fit a new preprocessor on df (use for train set only).
    preprocessor: Pre-fitted ColumnTransformer. Required if fit=False.

    Returns
    -------
    X           : np.ndarray, shape (n_samples, 28)
    y           : np.ndarray of int8, shape (n_samples,) — None if TARGET absent
    preprocessor: Fitted ColumnTransformer (new if fit=True, same if fit=False)
    """
    if fit:
        preprocessor = build_preprocessor()
        X = preprocessor.fit_transform(df[FEATURE_COLS])
    else:
        if preprocessor is None:
            raise ValueError("preprocessor must be provided when fit=False")
        X = preprocessor.transform(df[FEATURE_COLS])

    y = df["TARGET"].to_numpy(dtype=np.int8) if "TARGET" in df.columns else None
    return X, y, preprocessor


def get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """Return feature names in the same order as the X columns output."""
    return NUMERIC_COLS + CATEGORICAL_COLS
