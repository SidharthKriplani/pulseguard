# PulseGuard — Reproducibility Note

**Added:** 2026-06-23 (Opus audit, Fix G)
**Purpose:** State exactly what can be regenerated from committed code, where the gap is, and how the frozen champion was independently verified.

---

## Runnable from committed code

| Stage | Script | Produces |
|---|---|---|
| Feature engineering (7-table spine + 60/20/20 split) | `scripts/g9a_fe_runner.sh` (paths now derive from repo root) | `outputs/data/g9a_splits.pkl`, aggregates, `g9a_feature_factory_report.json` |
| 12-model baseline tournament | `scripts/g9a_model_tournament.py` (paths fixed; dead `import pandas as pd as pd_tmp` removed) | `g9a_model_tournament_report.json`, tournament probas |
| G4 XGBoost demo (synthetic, for Cloud Run) | `scripts/train_champion.py` | `champion_xgb.json`, `champion_calibrated.pkl` (sigmoid CalibratedClassifierCV), `g4_*` reports |
| GP5 LSTM challenger | `notebooks/GP5_LSTM_encoder.ipynb` + `scripts/gp5_preprocess_sequences.py` + `scripts/gp5_augment_and_retrain.py` | `lgb_gp5_172_challenger.txt`, embeddings |
| Defense PDF | `scripts/build_defense_pdf_v5.py` | `docs/defense/PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf` |

## Known gap (do not overstate reproducibility)

The **GP2 champion pipeline has no committed producer script.** `lgb_mono_champion.txt`, the isotonic
arrays (`iso_x.npy` / `iso_y.npy`), and the `gold_pass2_*` evidence artifacts were generated in an
ephemeral working session whose Optuna-HPO + calibration + champion-selection script was never
committed. `train_champion.py` is the G4 XGBoost **demo** trainer, not this pipeline. Until the GP2
trainer is reconstructed and committed, the champion is **verifiable but not regenerable** from the repo.

## Independent verification (audit, 2026-06-23)

The frozen champion + the committed `g9a_splits.pkl` test split reproduce the headline metrics exactly,
which is why the artifacts are trusted despite the gap above:

```bash
cd "<repo root>"
python3 - <<'PY'
import pickle, numpy as np, lightgbm as lgb
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.linear_model import LogisticRegression
s = pickle.load(open('outputs/data/g9a_splits.pkl','rb'))
Xv,yv = s['X_val'].values,  s['y_val'].values
Xte,yte = s['X_test'].values, s['y_test'].values
bst = lgb.Booster(model_file='outputs/models/lgb_mono_champion.txt')
assert bst.num_feature()==140 and bst.num_trees()==279
rv, rte = bst.predict(Xv), bst.predict(Xte)
def ece(p,y,nb=10):
    e=0.0
    for i in range(nb):
        lo,hi=i/nb,(i+1)/nb
        m=(p>=lo)&(p<hi) if i<nb-1 else (p>=lo)&(p<=hi)
        if m.sum(): e+=abs(p[m].mean()-y[m].mean())*m.sum()/len(y)
    return e
# Platt (frozen GP2 report's calibrator): LogisticRegression C=1e6 on val
pte = LogisticRegression(C=1e6).fit(rv.reshape(-1,1),yv).predict_proba(rte.reshape(-1,1))[:,1]
# Isotonic (served): numpy interp over iso_x/iso_y
ix,iy = np.load('outputs/models/iso_x.npy'), np.load('outputs/models/iso_y.npy')
cte = np.interp(rte, ix, iy)
print('RAW   AUC=%.6f PR=%.6f ECE=%.6f' % (roc_auc_score(yte,rte), average_precision_score(yte,rte), ece(rte,yte)))
print('PLATT AUC=%.6f Brier=%.6f ECE=%.6f' % (roc_auc_score(yte,pte), brier_score_loss(yte,pte), ece(pte,yte)))
print('ISO   AUC=%.6f Brier=%.6f ECE=%.6f' % (roc_auc_score(yte,cte), brier_score_loss(yte,cte), ece(cte,yte)))
PY
```

Expected (matches the frozen artifact to six decimals):

```
RAW   AUC=0.776858 PR=0.262773 ECE=0.294812
PLATT AUC=0.776858 Brier=0.066833 ECE=0.003396   <- the frozen GP2 single-shot test report
ISO   AUC=0.776398 Brier=0.066790 ECE=0.001938   <- the calibrator actually served by app.py
```

**Takeaway:** AUC=0.7769 is solid. The served isotonic calibrator's test ECE is **0.0019**; the frozen
report's **0.0034** is the Platt variant. `champion_calibrated.pkl` is the unrelated G4 XGBoost demo
calibrator (requires `xgboost` to unpickle) — it is not evidence about the GP2 champion's calibration.
