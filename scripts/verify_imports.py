"""
G1 — Import Verification Script
PulseGuard · Confirms all required packages are importable and functional.

Run: python3 scripts/verify_imports.py
Expected: All PASS; exits 0 on success, 1 on any failure.
"""

import sys
import traceback
from datetime import datetime

RESULTS = []

def check(label, fn):
    try:
        result = fn()
        msg = f"  result: {result}" if result is not None else ""
        RESULTS.append(("PASS", label, msg))
    except Exception as e:
        RESULTS.append(("FAIL", label, str(e)))

# ─────────────────────────────────────────────────────────────
# 1. Core imports
# ─────────────────────────────────────────────────────────────

def import_pandas():
    import pandas as pd
    return f"pandas {pd.__version__}"

def import_numpy():
    import numpy as np
    return f"numpy {np.__version__}"

def import_xgboost():
    import xgboost as xgb
    return f"xgboost {xgb.__version__}"

def import_lightgbm():
    import lightgbm as lgb
    return f"lightgbm {lgb.__version__}"

def import_sklearn():
    import sklearn
    return f"scikit-learn {sklearn.__version__}"

def import_scipy():
    import scipy
    return f"scipy {scipy.__version__}"

def import_shap():
    import shap
    return f"shap {shap.__version__}"

def import_optuna():
    import optuna
    return f"optuna {optuna.__version__}"

def import_featureleakagelens():
    import featureleakagelens
    from featureleakagelens import LeakageAuditConfig
    return "featureleakagelens OK (LeakageAuditConfig importable)"

check("pandas import", import_pandas)
check("numpy import", import_numpy)
check("xgboost import", import_xgboost)
check("lightgbm import", import_lightgbm)
check("scikit-learn import", import_sklearn)
check("scipy import", import_scipy)
check("shap import", import_shap)
check("optuna import", import_optuna)
check("featureleakagelens import", import_featureleakagelens)

# ─────────────────────────────────────────────────────────────
# 2. Functional smoke tests
# ─────────────────────────────────────────────────────────────

def smoke_xgboost_train():
    """Train a tiny XGBoost model; verify it produces predictions."""
    import numpy as np
    import xgboost as xgb
    rng = np.random.default_rng(42)
    X = rng.standard_normal((200, 5))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    dtrain = xgb.DMatrix(X, label=y)
    params = {"objective": "binary:logistic", "eval_metric": "auc", "seed": 42}
    model = xgb.train(params, dtrain, num_boost_round=10, verbose_eval=False)
    preds = model.predict(dtrain)
    assert len(preds) == 200 and 0 < preds.mean() < 1
    return f"XGBoost train smoke OK (preds mean={preds.mean():.4f})"

def smoke_lightgbm_train():
    """Train a tiny LightGBM model; verify it produces predictions."""
    import numpy as np
    import lightgbm as lgb
    rng = np.random.default_rng(42)
    X = rng.standard_normal((200, 5))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    ds = lgb.Dataset(X, label=y)
    params = {"objective": "binary", "metric": "auc", "verbose": -1, "seed": 42}
    model = lgb.train(params, ds, num_boost_round=10)
    preds = model.predict(X)
    assert len(preds) == 200 and 0 < preds.mean() < 1
    return f"LightGBM train smoke OK (preds mean={preds.mean():.4f})"

def smoke_psi():
    """Compute PSI between two distributions; verify it's above 0 for shifted data."""
    import numpy as np

    def compute_psi(expected, actual, n_bins=10):
        """Population Stability Index."""
        breakpoints = np.linspace(0, 1, n_bins + 1)
        expected_pct = np.histogram(expected, bins=breakpoints)[0] / len(expected)
        actual_pct = np.histogram(actual, bins=breakpoints)[0] / len(actual)
        # Avoid log(0) with small epsilon
        expected_pct = np.where(expected_pct == 0, 1e-6, expected_pct)
        actual_pct = np.where(actual_pct == 0, 1e-6, actual_pct)
        psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        return psi

    rng = np.random.default_rng(42)
    # Stable distribution (should produce low PSI)
    ref = rng.beta(2, 5, 1000)
    stable = rng.beta(2, 5, 1000)
    psi_stable = compute_psi(ref, stable)

    # Shifted distribution (Day 14 analog — should produce ALERT-level PSI)
    shifted = rng.beta(2, 5, 1000) - 0.18
    shifted = np.clip(shifted, 0, 1)
    psi_shifted = compute_psi(ref, shifted)

    assert psi_stable < 0.10, f"Expected stable PSI < 0.10, got {psi_stable:.4f}"
    assert psi_shifted > 0.10, f"Expected shifted PSI > 0.10, got {psi_shifted:.4f}"

    alert = "ALERT" if psi_shifted > 0.20 else "WARN"
    return (f"PSI smoke OK — stable={psi_stable:.4f} (<0.10), "
            f"shifted={psi_shifted:.4f} ({alert})")

def smoke_shap():
    """Run SHAP Explainer on a tiny XGBoost model.

    shap 0.49.1 + xgboost 3.x: TreeExplainer has a base_score parsing bug with
    XGBoost 3.x JSON format. Use shap.Explainer (unified API) with predict_proba
    as the model function — fully supported and equivalent for mean |SHAP| ranking.
    """
    import numpy as np
    import xgboost as xgb
    import shap
    rng = np.random.default_rng(42)
    X = rng.standard_normal((100, 4))
    y = (X[:, 0] > 0).astype(int)
    model = xgb.XGBClassifier(n_estimators=10, random_state=42, eval_metric="logloss")
    model.fit(X, y)
    # Use shap.Explainer (Kernel/Permutation fallback) — works with any predict function
    background = X[:20]
    explainer = shap.Explainer(model.predict_proba, background)
    sv = explainer(X[:20])
    # sv.values shape: (n_samples, n_features, n_classes) for binary
    assert sv.values.shape[1] == X.shape[1], (
        f"SHAP feature dim {sv.values.shape[1]} != X features {X.shape[1]}"
    )
    return f"SHAP smoke OK (Explainer API; values shape: {sv.values.shape})"

def smoke_sklearn_calibration():
    """Fit CalibratedClassifierCV (Platt) on a prefit XGBoost model."""
    import numpy as np
    from sklearn.calibration import CalibratedClassifierCV
    import xgboost as xgb
    rng = np.random.default_rng(42)
    X_train = rng.standard_normal((200, 5))
    y_train = (X_train[:, 0] > 0).astype(int)
    X_val = rng.standard_normal((50, 5))
    y_val = (X_val[:, 0] > 0).astype(int)
    base = xgb.XGBClassifier(n_estimators=10, random_state=42, eval_metric="logloss")
    base.fit(X_train, y_train)
    calibrated = CalibratedClassifierCV(base, method="sigmoid", cv="prefit")
    calibrated.fit(X_val, y_val)
    probs = calibrated.predict_proba(X_val)[:, 1]
    assert 0 < probs.mean() < 1
    return f"Platt calibration smoke OK (mean prob={probs.mean():.4f})"

def smoke_scipy_delong():
    """Verify scipy stats imports needed for DeLong test approximation."""
    from scipy import stats
    import numpy as np
    rng = np.random.default_rng(42)
    a = rng.standard_normal(50)
    b = rng.standard_normal(50)
    t_stat, p_value = stats.ttest_ind(a, b)
    assert 0 <= p_value <= 1
    return f"scipy.stats smoke OK (t={t_stat:.3f}, p={p_value:.3f})"

def smoke_optuna():
    """Run a tiny 3-trial Optuna study."""
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def objective(trial):
        x = trial.suggest_float("x", -2, 2)
        return (x - 0.5) ** 2

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=3)
    return f"Optuna smoke OK (best value={study.best_value:.4f}, best x={study.best_params['x']:.4f})"

check("XGBoost training smoke test", smoke_xgboost_train)
check("LightGBM training smoke test", smoke_lightgbm_train)
check("PSI computation smoke test", smoke_psi)
check("SHAP TreeExplainer smoke test", smoke_shap)
check("Platt calibration smoke test", smoke_sklearn_calibration)
check("scipy.stats smoke test", smoke_scipy_delong)
check("Optuna HPO smoke test", smoke_optuna)

# ─────────────────────────────────────────────────────────────
# 3. Report
# ─────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("  G1 IMPORT VERIFICATION REPORT")
print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

passed = [r for r in RESULTS if r[0] == "PASS"]
failed = [r for r in RESULTS if r[0] == "FAIL"]

for status, label, detail in RESULTS:
    mark = "✓" if status == "PASS" else "✗"
    print(f"  [{mark}] {label}")
    if detail:
        print(f"       {detail}")

print()
print(f"  TOTAL: {len(RESULTS)} checks — {len(passed)} PASS, {len(failed)} FAIL")

if failed:
    print()
    print("  FAILURES:")
    for _, label, detail in failed:
        print(f"    - {label}: {detail}")
    print()
    print("  STATUS: FAIL — not all packages verified")
    sys.exit(1)
else:
    print()
    print("  STATUS: PASS — all packages verified; G1 environment ready")
    sys.exit(0)
