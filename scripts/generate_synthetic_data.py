"""
G3 — Synthetic Data Generator
PulseGuard · Home Credit Schema Synthetic Fallback

Produces a synthetic dataset matching the Home Credit Default Risk schema.
Used when the real Kaggle dataset is unavailable.

Dataset label: synthetic_home_credit_like
Run: python3 scripts/generate_synthetic_data.py [--n-rows 50000] [--seed 42]

Key properties matched to Home Credit:
  - 8% default rate (TARGET = 1)
  - EXT_SOURCE_2 and EXT_SOURCE_3 as top predictors
  - Correct missingness patterns
  - Logistic DGP ensures non-trivial AUC (model learns but isn't perfect)

All SYNTHETIC fields are labeled with __SYNTHETIC suffix or documented below.
This dataset is NOT from Kaggle and does NOT represent real borrowers.

DGP Calibration history:
  G3   intercept = -2.8     → actual default_rate ≈ 26%  (KNOWN BUG — documented in G3)
  G3.1 intercept = -4.20703 → actual default_rate ≈ 7.9–8.2% (CALIBRATED)
       Binary search on N=200,000; verified on N=50,000 across seeds 42–46.
       All seeds in [7%, 9%] acceptance range. Mean default_rate ≈ 8.05%.
"""

import argparse
import os
import numpy as np
import pandas as pd


DATASET_LABEL = "synthetic_home_credit_like"
DATASET_SOURCE = "synthetic_home_credit_like"


def generate(n: int = 50_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # ── Core credit bureau scores ──────────────────────────────────────────
    EXT_SOURCE_2 = rng.beta(2, 5, n).astype(np.float32)          # range [0,1]; higher = lower risk
    EXT_SOURCE_3 = rng.beta(1.5, 4, n).astype(np.float32)
    # ~50% missing in Home Credit
    EXT_SOURCE_3[rng.random(n) < 0.50] = np.nan

    # ── Financial fields ───────────────────────────────────────────────────
    AMT_CREDIT       = np.exp(rng.normal(13.0, 0.5, n)).clip(45_000, 4_000_000).astype(np.float32)
    AMT_INCOME_TOTAL = np.exp(rng.normal(11.0, 0.7, n)).clip(25_000, 1_200_000).astype(np.float32)
    AMT_ANNUITY      = (AMT_CREDIT * rng.uniform(0.03, 0.06, n)).astype(np.float32)
    AMT_GOODS_PRICE  = (AMT_CREDIT * rng.uniform(0.90, 1.05, n)).astype(np.float32)
    # ~1% missing
    AMT_GOODS_PRICE[rng.random(n) < 0.01] = np.nan

    # ── Demographics ───────────────────────────────────────────────────────
    DAYS_BIRTH = rng.integers(-25_000, -6_570, n).astype(np.int32)   # age 18–68

    employed_mask = rng.random(n) > 0.20                              # 80% employed
    DAYS_EMPLOYED = np.where(
        employed_mask,
        rng.integers(-10_000, -1, n),
        365_243                                                        # sentinel for unemployed
    ).astype(np.int32)

    CODE_GENDER       = rng.choice(['F', 'M'], n, p=[0.65, 0.35])
    NAME_INCOME_TYPE  = rng.choice(
        ['Working', 'Commercial associate', 'Pensioner', 'State servant', 'Unemployed'],
        n, p=[0.50, 0.20, 0.15, 0.10, 0.05]
    )
    NAME_CONTRACT_TYPE = rng.choice(
        ['Cash loans', 'Revolving loans'], n, p=[0.90, 0.10]
    )
    NAME_EDUCATION_TYPE = rng.choice(
        ['Secondary / secondary special', 'Higher education',
         'Incomplete higher', 'Lower secondary'],
        n, p=[0.60, 0.30, 0.07, 0.03]
    )
    NAME_FAMILY_STATUS = rng.choice(
        ['Married', 'Single / not married', 'Civil marriage', 'Widow'],
        n, p=[0.65, 0.20, 0.10, 0.05]
    )
    REGION_RATING_CLIENT = rng.choice([1, 2, 3], n, p=[0.20, 0.60, 0.20]).astype(np.int8)
    FLAG_OWN_CAR    = rng.choice(['Y', 'N'], n, p=[0.35, 0.65])
    FLAG_OWN_REALTY = rng.choice(['Y', 'N'], n, p=[0.70, 0.30])
    CNT_CHILDREN    = np.minimum(rng.poisson(0.4, n), 5).astype(np.int32)
    CNT_FAM_MEMBERS = np.clip(CNT_CHILDREN + 1 + rng.binomial(1, 0.65, n), 1, 7).astype(np.float32)

    REGION_POPULATION_RELATIVE = np.exp(rng.normal(-5, 0.5, n)).clip(3e-4, 0.072).astype(np.float32)
    DAYS_REGISTRATION = rng.uniform(-25_000, -0.5, n).astype(np.float32)
    DAYS_ID_PUBLISH   = rng.integers(-7_000, 0, n).astype(np.int32)

    DEF_30_CNT = rng.poisson(0.4, n).astype(np.float32)
    DEF_30_CNT[rng.random(n) < 0.03] = np.nan
    DEF_60_CNT = rng.poisson(0.2, n).astype(np.float32)
    DEF_60_CNT[rng.random(n) < 0.03] = np.nan
    OBS_30_CNT = rng.poisson(3.0, n).astype(np.float32)

    FLAG_DOCUMENT_3           = rng.binomial(1, 0.71, n).astype(np.int8)
    HOUR_APPR_PROCESS_START   = rng.integers(7, 21, n).astype(np.int8)
    LIVE_REGION_NOT_WORK_REGION = rng.binomial(1, 0.15, n).astype(np.int8)
    ORGANIZATION_TYPE = rng.choice(
        ['Business Entity Type 3', 'Self-employed', 'Other'],
        n, p=[0.25, 0.18, 0.57]
    )

    # ── Logistic DGP for TARGET ────────────────────────────────────────────
    # Ensures non-trivial AUC; EXT_SOURCE_2 is top predictor.
    # G3.1 CALIBRATION: intercept updated from -2.8 (26% rate) to -4.20703 (~8% rate).
    # Binary search on N=200,000; verified on N=50,000 across 5 seeds (mean=8.05%, std=0.11%).
    ext3_imp = np.where(np.isnan(EXT_SOURCE_3), float(np.nanmedian(EXT_SOURCE_3)), EXT_SOURCE_3)
    logit = (
        -4.20703
        + 1.2 * (1.0 - EXT_SOURCE_2)
        + 0.9 * (1.0 - ext3_imp)
        + 0.4 * (AMT_CREDIT / 1e6)
        - 0.3 * (AMT_INCOME_TOTAL / 1e5)
        + 0.7 * (DAYS_EMPLOYED == 365_243).astype(float)
        + 0.3 * (REGION_RATING_CLIENT == 3).astype(float)
    )
    prob   = 1.0 / (1.0 + np.exp(-logit))
    TARGET = rng.binomial(1, prob).astype(np.int8)

    # ── Synthetic FOIR input (not in Home Credit) ──────────────────────────
    # EXISTING_OBLIGATIONS_MONTHLY: 5–25% of income; labeled SYNTHETIC
    EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC = (
        rng.uniform(0.05, 0.25, n) * AMT_INCOME_TOTAL
    ).astype(np.float32)

    # ── Assemble DataFrame ─────────────────────────────────────────────────
    df = pd.DataFrame({
        'SK_ID_CURR':                         np.arange(100_002, 100_002 + n, dtype=np.int64),
        'TARGET':                             TARGET,
        'EXT_SOURCE_2':                       EXT_SOURCE_2,
        'EXT_SOURCE_3':                       EXT_SOURCE_3,
        'AMT_CREDIT':                         AMT_CREDIT,
        'AMT_INCOME_TOTAL':                   AMT_INCOME_TOTAL,
        'AMT_ANNUITY':                        AMT_ANNUITY,
        'AMT_GOODS_PRICE':                    AMT_GOODS_PRICE,
        'DAYS_BIRTH':                         DAYS_BIRTH,
        'DAYS_EMPLOYED':                      DAYS_EMPLOYED,
        'CODE_GENDER':                        CODE_GENDER,
        'NAME_INCOME_TYPE':                   NAME_INCOME_TYPE,
        'NAME_CONTRACT_TYPE':                 NAME_CONTRACT_TYPE,
        'NAME_EDUCATION_TYPE':                NAME_EDUCATION_TYPE,
        'NAME_FAMILY_STATUS':                 NAME_FAMILY_STATUS,
        'REGION_RATING_CLIENT':               REGION_RATING_CLIENT,
        'FLAG_OWN_CAR':                       FLAG_OWN_CAR,
        'FLAG_OWN_REALTY':                    FLAG_OWN_REALTY,
        'REGION_POPULATION_RELATIVE':         REGION_POPULATION_RELATIVE,
        'DAYS_REGISTRATION':                  DAYS_REGISTRATION,
        'DAYS_ID_PUBLISH':                    DAYS_ID_PUBLISH,
        'CNT_CHILDREN':                       CNT_CHILDREN,
        'CNT_FAM_MEMBERS':                    CNT_FAM_MEMBERS,
        'DEF_30_CNT_SOCIAL_CIRCLE':           DEF_30_CNT,
        'DEF_60_CNT_SOCIAL_CIRCLE':           DEF_60_CNT,
        'OBS_30_CNT_SOCIAL_CIRCLE':           OBS_30_CNT,
        'FLAG_DOCUMENT_3':                    FLAG_DOCUMENT_3,
        'HOUR_APPR_PROCESS_START':            HOUR_APPR_PROCESS_START,
        'LIVE_REGION_NOT_WORK_REGION':        LIVE_REGION_NOT_WORK_REGION,
        'ORGANIZATION_TYPE':                  ORGANIZATION_TYPE,
        'EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC': EXISTING_OBLIGATIONS_MONTHLY__SYNTHETIC,
    })

    default_rate = TARGET.mean()
    print(f"[generate_synthetic_data] Generated {n:,} rows | default_rate={default_rate:.4f} | label={DATASET_LABEL}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic Home Credit-like dataset")
    parser.add_argument("--n-rows", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str,
                        default="data/synthetic_home_credit_like.csv")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df = generate(n=args.n_rows, seed=args.seed)
    df.to_csv(args.out, index=False)
    print(f"[generate_synthetic_data] Saved → {args.out}")
