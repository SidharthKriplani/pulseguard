# SESSION_STATE — PulseGuard (read this FIRST on resume)

**Last updated:** 2026-06-23 (Opus 4.8 audit + doc-correction session)
**Why this file exists:** so a fresh chat can resume mid-stream without re-deriving context.
**Read order on cold start:** this file → `OPUS_AUDIT_FINDINGS.md` → `00_CONTROL_TOWER.md` → `docs/REPRODUCIBILITY_NOTE.md`.

---

## 1. One-line state

PulseGuard is GOLD-checkpointed (89.3%), champion **frozen**. A high-effort Opus audit (2026-06-23)
found the **calibration story was wrong and self-contradictory**, corrected it across every
candidate-facing doc, fixed two code bugs, and added reproducibility docs. **All file changes are
saved to the folder but NOT yet git-committed** (sandbox can't remove the `.git` lock; user must
commit from their own terminal).

---

## 2. The corrected calibration truth (memorize this — it's the crux)

Reproduced exactly this session from `outputs/models/lgb_mono_champion.txt` on the real 61,503-row
test split in `outputs/data/g9a_splits.pkl`:

| Calibrator | Where it lives | Test ECE | Test Brier | AUC |
|---|---|---|---|---|
| **Isotonic** | **SERVED** by `app.py` (`iso_x.npy`/`iso_y.npy`, numpy interp) | **0.0019** (audit-recomputed) | 0.0668 | 0.7764 |
| Platt | What the FROZEN GP2 single-shot report scored | 0.0034 | 0.0668 | 0.7769 |
| (raw, uncalibrated) | — | 0.295 | — | 0.7769 |

- "ECE=0.0034" is **Platt's** number, not isotonic's. Served isotonic is **0.0019**.
- AUC headline 0.7769 = raw/Platt (rank-based); served isotonic is 0.7764 (interp ties). Quoting 0.7769 for discrimination is fine.
- The old "`champion_calibrated.pkl` → `cal['selected']='isotonic']` forensics" anecdote is **FALSE** — that pkl is the unrelated **G4 XGBoost demo's** sigmoid calibrator (needs `xgboost` to unpickle). Removed everywhere.
- 0.0019 is **audit-recomputed**, NOT in the frozen `outputs/evidence/` JSONs (those say Platt 0.0034). Always label it "audit-recomputed."

Re-verify any time with the script in `docs/REPRODUCIBILITY_NOTE.md` (expect Platt 0.003396 / iso 0.001938 / AUC 0.776858).

---

## 3. What this session changed (all saved to disk)

Fixes A–G applied per `OPUS_AUDIT_FINDINGS.md` §8. Files touched:

- `docs/PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md` — calibration standardized (side-by-side), §8/§30/Q12/failure-#6 reconciled, false forensics removed, deployment reconciled.
- `scripts/build_defense_pdf_v5.py` — same corrections; **PDF rebuilt → `docs/defense/PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf` (38 pages)**.
- `docs/PULSEGUARD_MODEL_CARD.md` — isotonic served + imputation-leak limitation added.
- `docs/PULSEGUARD_RESUME_OPPORTUNITY_PACK.md` + `docs/PULSEGUARD_GOLD_CHECKPOINT.md` — calibration wording corrected.
- `README.md` — 8 calibration refs corrected (badge, hero, tables, JSON sample, blurb).
- `06_CLAIM_BOUNDARY.md` — top authoritative banner, G9A CatBoost answers superseded, deployment + endpoint table reconciled.
- `scripts/g9a_feature_engineering.py`, `scripts/g9a_model_tournament.py`, `scripts/g9a_fe_runner.sh` — hardcoded `/sessions/...` paths → repo-root-relative.
- `scripts/g9a_model_tournament.py` — removed build-breaking `import pandas as pd as pd_tmp`.
- NEW: `OPUS_AUDIT_FINDINGS.md`, `docs/REPRODUCIBILITY_NOTE.md`, this `SESSION_STATE.md`.
- Frozen artifacts (`outputs/evidence/*.json`, `lgb_mono_champion.txt`, iso arrays) — **NOT modified**.

---

## 4. Immediate next action (do this first on resume)

**Commit is pending.** From the user's own terminal (sandbox lacks perms on `.git` locks):

```bash
cd ~/Documents/Professional/GitHub/beastmax\ \(5\)/pulseguard
rm -f .git/HEAD.lock .git/index.lock
git add -A
git commit -m "audit(opus): correct calibration story (isotonic served 0.0019 / Platt frozen 0.0034), remove false pkl forensics, reconcile deployment + CatBoost claims, fix hardcoded paths + tournament syntax bug, add findings + reproducibility + session-state notes"
git push
```

Verify after: `git -c core.fsmonitor=false status` should be clean.

---

## 5. Open threads (not auto-applied — user's judgment)

1. **Live Cloud Run revision unverified.** Committed `app.py` serves the champion (native booster + numpy isotonic), but the live endpoint may still be the older G4 XGBoost demo (AUC 0.6261). Hit `https://pulseguard-api-98058433335.us-central1.run.app` and redeploy if it returns 0.62. Until then, don't claim the live endpoint returns champion numbers.
2. **GP2 trainer not committed (reproducibility gap F5).** `lgb_mono_champion.txt`, `iso_x/iso_y.npy`, and `gold_pass2_*` artifacts have no committed producer script (`train_champion.py` is the G4 demo). Reconstruct + commit the GP2 Optuna/calibration script to make the champion regenerable, not just verifiable.
3. **Imputation leak (F6) — accepted, documented.** `df.fillna(df.median())` runs on the full dataset before the split (`g9a_feature_engineering.py` L325 / `g9a_fe_runner.sh`). Negligible metric impact; documented in model card as a known minor leak. Refit would change the frozen champion, so left as-is.
4. **Internal gate docs still stale (cosmetic).** `docs/G0_*` and `docs/G9A_FULL_MODERN_MODEL_TOURNAMENT.md` still say "CatBoost champion / production-quality / Platt selected." Accurate for their era, but the repo is **public** — banner them as superseded if you expect interviewers to browse the GitHub repo. (Candidate-facing docs are already fully consistent.)

---

## 6. Interview-safety verdict (from the audit)

With threads 1–4 owned honestly, **nothing left is false or disqualifying.** Real risks to manage in-room, not content errors:
- Lead with the calibration reconciliation ("report said Platt, code serves isotonic — I caught it by reading the served artifact") — strength if you say it first, gotcha if they find it.
- Don't present 0.0019 as a frozen-evidence number (it's audit-recomputed).
- Don't claim the live endpoint returns champion numbers until redeployed/verified.
- Be ready for "show me the GP2 training script" (thread 2).

---

## 7. Hard constraints (unchanged — never violate)

Champion frozen (LightGBM_monotonic, 140 feat/279 trees). Do not retune, do not change champion, do
not modify `outputs/evidence/` JSONs or `lgb_mono_champion.txt`. Home Credit = primary; Taiwan =
legacy appendix; LendingClub = dropped. LLM = ASSISTIVE_ONLY. No production/regulatory/fairness-cert
claims. Always `cd` into the repo before terminal commands.
