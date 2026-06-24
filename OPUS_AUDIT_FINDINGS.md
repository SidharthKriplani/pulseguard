# PulseGuard — Opus 4.8 Audit Findings

**Auditor:** Claude Opus 4.8 (high-effort, 8-pass)
**Date:** 2026-06-23
**Scope:** `pulseguard/` only. Per handoff: champion frozen, evidence JSONs frozen, no retune.
**Method:** Every headline number reproduced from `lgb_mono_champion.txt` against the real
61,503-row test split in `g9a_splits.pkl` (lightgbm 4.6.0, sklearn 1.7.2, numpy 2.2.6).

---

## 0. Verdict

The model is real and the headline AUC is solid. **But the calibration story told across the
defense doc, the PDF, and the handoff is factually wrong, and it is wrong in a way that is
internally self-contradictory.** Two other governance-grade issues (a stale "CatBoost is my
champion" prep section, and an imputation leak) also survive into shippable material. None of
this requires retuning — all fixes are documentation/code-hygiene — but they matter because the
whole point of PulseGuard is governance integrity.

Severity tally: **3 HIGH, 1 HIGH(architectural), 2 MEDIUM, 3 LOW.**

---

## 1. Reproduced ground truth (the numbers that are actually true)

All on the locked champion + the real test split. RAW metrics match the frozen artifact to six
decimals, which confirms the model file and split are the genuine GP2 champion.

| Metric | RAW (uncalibrated) | **Platt** (val-fit) | **Isotonic** (served `iso_x/iso_y`) | Frozen artifact |
|---|---|---|---|---|
| AUC | 0.776858 | 0.776858 | 0.776398 | 0.776858 |
| PR-AUC | 0.262773 | — | 0.255768 | 0.262773 |
| Brier | 0.174458 | 0.066833 | 0.066790 | 0.066833 |
| **ECE (test)** | 0.294812 | **0.003396** | **0.001938** | 0.003396 (`ece_platt`) |
| ECE (val) | — | 0.005086 | — | 0.005086 |

Champion structure verified: **140 features, 279 trees**. `iso_x`/`iso_y` shape **(134,)**,
range [0.0026, 0.970], `iso_y` monotone non-decreasing on [0,1]. ✓

**The single most important fact:** `ECE = 0.0034` is the **Platt** number. The served calibrator
is **isotonic**, and isotonic's real test ECE is **0.0019** — better than what's advertised. The
project has been quoting Platt's ECE under an "isotonic" label.

---

## 2. HIGH findings

### F1 — `ECE=0.0034` is misattributed to isotonic everywhere
`0.003396` is reproducibly the **Platt** test ECE (logistic, C=1e6, val-fit — reproduced to six
decimals). The served isotonic calibrator gives **0.001938**. Yet the cover page, exec summary,
resume bullets, and Section 8 of both the PDF and the markdown say *"isotonic … ECE=0.0034."*
That sentence pairs the served calibrator's name with the other calibrator's number. Either
number is defensible; the pairing is not.
*Locations:* PDF `build_defense_pdf_v5.py` L113/146/396/787/812; defense MD L626; model card L66/83.

### F2 — The "calibration forensics" anecdote cites the wrong file and is almost certainly false
Both docs claim: *"Forensic inspection of `champion_calibrated.pkl` confirmed `cal['selected'] =
'isotonic'`."* That artifact is **not** the GP2 LightGBM champion's calibrator. It is the **G4
XGBoost demo's** `CalibratedClassifierCV`, built with `method="sigmoid"` (Platt) in
`train_champion.py` L169. Evidence: the pickle **requires `xgboost` to unpickle** (it failed to
load without it in this audit), it is a `CalibratedClassifierCV` object, not a dict, so it has no
`['selected']` key, and it was built sigmoid-only so it could never report isotonic. The
"diverged by up to 0.53 during Cloud Run" story is attached to this same wrong artifact.
*Locations:* PDF L402; defense MD L263, L628–630.

### F3 — The defense markdown asserts BOTH calibrators as "the one selected"
`PULSEGUARD_INTERVIEW_DEFENSE_COMPLETE.md` contradicts itself:
- **Isotonic selected:** Section 8 (L253–263) and Q (L626–630).
- **Platt selected / isotonic excluded:** overview L26, table L121 ("Isotonic excluded"), L222,
  L231/237, L462, L480, and the resume/elevator bullets L516–540, L842–856.
- **Failure #6 (L441) states the *opposite* of Section 8 verbatim:** *"Isotonic excluded from
  comparison; Platt selected … Platt is the correct calibrator."*

A reader (or interviewer reading over a shoulder) will catch this in seconds. The PDF v5 is the
mostly-isotonic version; the MD is half-converted. The two deliverables disagree with each other.

### F4 — `06_CLAIM_BOUNDARY.md` still tells the candidate to claim CatBoost is the champion
The "G9A safe interview answers" block is unmarked as superseded:
- L360: *"What is your champion model?" → "**CatBoost** with Platt … which is **production-quality**."*
- L372: *"CatBoost is champion; LightGBM is governance alternative."*

This is the exact claim the handoff lists as **forbidden (#9)**, sitting in the file whose job is
to prevent forbidden claims. It is gate-scoped (G9A, pre-GP2) but carries no "SUPERSEDED BY GP2"
banner, and "production-quality" is loose language for a portfolio project. The GP2-correct
boundary exists later in the same file (L437+), so the file holds both the right and wrong answer.

---

## 3. HIGH (architectural) finding

### F5 — The GP2 champion cannot be regenerated from committed code
No committed script trains `lgb_mono_champion.txt`, writes `iso_x/iso_y.npy`, or produces the
`gold_pass2_*` artifacts. What's in the repo:
- `train_champion.py` — is the **G4 XGBoost demo** trainer (synthetic data, Platt). The handoff
  Section 5 mislabels it as *"Optuna HPO + calibration + champion selection."*
- `g9a_model_tournament.py` — hard-codes `/sessions/modest-magical-johnson/mnt/pulseguard/...`
  absolute paths and will not run in any other environment.

So the headline model and its entire evidence chain are outputs of an ephemeral session with no
committed, runnable producer. For a governance project this is the biggest structural gap: the
artifacts are trustworthy (they reproduce), but they are not *reproducible*.

---

## 4. MEDIUM findings

### F6 — Imputation leak: medians fit on the full dataset before the split
`g9a_feature_engineering.py` L325 runs `df.fillna(df.median(numeric_only=True))` **before** the
train/val/test split at L348. The imputation statistic therefore sees val+test rows. This
contradicts the stated *"imputation train-only"* discipline and the *"leakage 10/10 PASS"*
headline — and the GP1 leakage audit's 10 checks do **not** include imputation provenance, so the
leak was never in scope. `feature_medians.json` (served by `app.py`) are these full-data medians,
labeled "training medians." **Metric impact is negligible** (medians over 307k rows barely move),
but it is a real leak and a claim inconsistency. Since the champion is frozen, the honest fix is
to **document it as a known limitation**, not refit.

### F7 — Docs disagree on what the live endpoint actually serves
- `README.md` L212/L302: endpoint serves the **LightGBM champion** (AUC=0.7769) with isotonic —
  matches committed `app.py` + `Dockerfile` (native `.txt` booster + numpy interp, no sklearn).
- Defense MD L774/L1263 and claim boundary L630: endpoint serves the **G4 XGBoost demo**
  (AUC=0.6261) and *"champion could not be deployed (sklearn version lock)."*

The committed code **is** the isotonic-numpy workaround the handoff files under "future fix," so
the "could not deploy" narrative is stale at the code level. At most one description of the live
Cloud Run revision is correct. Needs reconciliation + a redeploy/verify of the live revision.

---

## 5. LOW findings

- **F8 — GP2 artifacts disagree on calibrator, independent of any "doc error."**
  `gold_pass2_calibration_report.json` says `selected_calibrator: isotonic`; the final test report
  says `Platt`. The selection rests on `ece_isotonic = 0.0` on val — a degenerate value (isotonic
  scored on the data it was fit on). The valid justification for isotonic is its **test** ECE
  (0.0019 < 0.0034), which this audit confirms. Keep isotonic, but justify it by test, not val.
- **F9 — Minor inconsistencies.** `gold_pass3_shap_reason_code_report.json` champion field reads
  `LightGBM_monotonic_platt`. G9A SHAP top feature was `EXT_SOURCE_3`; GP3 reports `EXT_SOURCE_MEAN`
  (different sample/run — note only). `OPUS_AUDIT_HANDOFF.md` is **untracked** (not committed),
  despite the prior session's "committed locally" note.

---

## 6. What is solid (verified PASS)

- Champion: 140 feat / 279 trees; AUC **0.776858** reproduced exactly; iso arrays valid + monotone.
- Served isotonic calibration is genuinely **better** than advertised (test ECE 0.0019).
- SHAP: `EXT_SOURCE_MEAN` rank-1 at **0.509755** (≈0.510 ✓); top-5 features 30/30 bootstrap-stable ✓.
- GP5: challenger has 172 features; `MONO_172 = MONO_140 + [0]*32` ✓; embeddings aligned to splits
  (184506/61502/61503 × 32) ✓; negative result (AUC 0.7264, champion retained) honestly handled ✓.
- RAG: `ABSTAIN_THRESHOLD = 0.25`, `abstain = top_score < THRESHOLD` ✓. LLM assistant is
  `ASSISTIVE_ONLY`, `decision_authority='HUMAN_UNDERWRITER'`, hard "never make/override decisions,"
  ABSTAIN on OOD ✓ — no approve/reject path found.
- `app.py` + `feature_pipeline.py` both have `from __future__ import annotations`; app loads the
  champion via native LightGBM booster (no pickle, no sklearn lock) ✓.
- Defense PDF rebuilds cleanly from `build_defense_pdf_v5.py` (relative paths) → **38 pages** ✓.
- GP1 leakage 10/10 within its scope; group leakage 0 ID overlap ✓.

---

## 7. Recommended fixes (all permitted under the freeze)

| # | Fix | Files |
|---|---|---|
| A | Standardize ONE calibration story: **served = isotonic, test ECE = 0.0019** (audit-recomputed); **frozen GP2 report scored Platt, ECE = 0.0034**; AUC = 0.7769 (note isotonic 0.7764 due to interp ties). | defense MD, PDF generator, model card |
| B | Replace the `champion_calibrated.pkl` / `cal['selected']` forensics anecdote with the accurate account (it's the G4 XGBoost demo's sigmoid calibrator; served arrays are the GP2 isotonic). | defense MD L263/628, PDF L402 |
| C | Reconcile defense MD internal contradiction — fix failure #6 + L121/462/480/516–540 to match Section 8. | defense MD |
| D | Banner or remove the G9A "CatBoost is my champion / production-quality" answers in the claim boundary. | `06_CLAIM_BOUNDARY.md` |
| E | Reconcile deployment narrative (README vs defense/claim-boundary) and verify what Cloud Run actually serves. | defense MD, claim boundary, README |
| F | Document full-data median imputation as a known minor leak (do NOT refit — champion is frozen). | model card, defense limitations |
| G | Commit a GP2 repro script (or a REPRODUCIBILITY note); fix `g9a_model_tournament.py` hardcoded path; commit the handoff + this findings file. | scripts, repo |

**Decision needed before I touch shippable docs:** these rewrites change the project's stated
headline number (ECE attribution) and remove a forensics story that appears in the PDF, the MD,
and the resume bullets. I want your call on scope before editing.

---

## 8. Resolution log (applied 2026-06-23, all fixes A–G, "show both" framing)

Calibration is now stated **one consistent way** everywhere candidate-facing: **served = isotonic,
test ECE 0.0019 (audit-recomputed); frozen GP2 single-shot report = Platt, test ECE 0.0034; AUC
0.7769.** The false `champion_calibrated.pkl` `cal['selected']` forensics anecdote is removed from
every doc and replaced with the reproducible side-by-side reconciliation.

| Fix | Files changed | Status |
|---|---|---|
| A — standardize calibration (side-by-side) | defense MD, PDF generator (+rebuilt, 38pp), model card, resume pack, GP checkpoint, README, claim boundary | ✅ |
| B — remove false pkl forensics anecdote | defense MD §8/§30/Q12, PDF §25/§30, resume pack | ✅ |
| C — reconcile defense-MD self-contradiction (failure #6 etc.) | defense MD | ✅ |
| D — supersede stale CatBoost-champion answers + strike "production-quality" | claim boundary (top banner + G9A banner + rows) | ✅ |
| E — reconcile deployment (committed app.py serves champion via native booster + numpy isotonic) | defense MD, PDF, claim boundary (incl. endpoint table), README already correct | ✅ |
| F — document full-data median imputation as a known minor leak (not refit; champion frozen) | model card limitations | ✅ |
| G — portability + repro | fixed hardcoded `/sessions/...` paths in `g9a_feature_engineering.py`, `g9a_model_tournament.py`, `g9a_fe_runner.sh`; removed the build-breaking `import pandas as pd as pd_tmp` syntax bug in the tournament script; added `docs/REPRODUCIBILITY_NOTE.md` | ✅ |

**Re-verification after all edits:** champion still loads (140 feat / 279 trees); Platt test
ECE=0.003396, isotonic test ECE=0.001938, AUC=0.776858 reproduce exactly; PDF rebuilds at 38 pages;
grep sweep confirms every remaining `0.0034` is explicitly labeled Platt/frozen-report or is
G4/G6/RiskFrame historical. Frozen artifacts in `outputs/evidence/` and `lgb_mono_champion.txt`
were **not** modified.

**Not done (cannot, from this environment):** the git commit. The `.git` lock files in the
iCloud-synced folder are permission-protected and the sandbox cannot remove them. Run the commit
from your own terminal (commands provided in chat).

**Still open for you (judgment calls, not auto-applied):** (1) verify/redeploy the live Cloud Run
revision so it matches committed `app.py`; (2) reconstruct + commit the GP2 trainer to close the
reproducibility gap (F5); (3) internal G0_*/G9A_* gate-history docs were left as-is (accurate for
their era) — banner them too if you want zero stale wording anywhere.
