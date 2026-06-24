"""
PulseGuard Interview Defense — Master Pack v5
Comprehensive PDF covering all 30 sections, Q&As, failures, GP5, calibration forensics.
Target: 40-60 pages, well-balanced.
"""

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'defense')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, 'PULSEGUARD_Defense_Master_Pack_v5_COMPLETE.pdf')

# ── Styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()
NAVY   = colors.HexColor('#0A2342')
BLUE   = colors.HexColor('#1B5299')
TEAL   = colors.HexColor('#0D7377')
LBLUE  = colors.HexColor('#E8F0FE')
LGRAY  = colors.HexColor('#F5F5F5')
DGRAY  = colors.HexColor('#555555')
WHITE  = colors.white

def S(name, **kw):
    s = ParagraphStyle(name, parent=base['Normal'], **kw)
    return s

COVER_TITLE  = S('CoverTitle',  fontSize=28, textColor=WHITE,      alignment=TA_CENTER, leading=34, spaceAfter=8)
COVER_SUB    = S('CoverSub',    fontSize=13, textColor=colors.HexColor('#BDD5EA'), alignment=TA_CENTER, leading=18)
COVER_BADGE  = S('CoverBadge',  fontSize=10, textColor=NAVY,       alignment=TA_CENTER)

H1           = S('H1',  fontSize=14, textColor=WHITE,  fontName='Helvetica-Bold',
                  backColor=NAVY, borderPad=5, leading=18, spaceBefore=14, spaceAfter=6)
H2           = S('H2',  fontSize=11, textColor=NAVY,   fontName='Helvetica-Bold',
                  leading=15, spaceBefore=10, spaceAfter=4)
H3           = S('H3',  fontSize=10, textColor=BLUE,   fontName='Helvetica-Bold',
                  leading=13, spaceBefore=7, spaceAfter=3)
BODY         = S('Body', fontSize=9,  textColor=DGRAY,  leading=13, spaceAfter=5, alignment=TA_JUSTIFY)
BULLET       = S('Bullet', fontSize=9, textColor=DGRAY,  leading=13, spaceAfter=3,
                  leftIndent=14, firstLineIndent=-10)
CODE         = S('Code', fontSize=8,  fontName='Courier', textColor=colors.HexColor('#333333'),
                  backColor=LGRAY, leading=11, spaceAfter=4, leftIndent=10)
QHEAD        = S('QHead', fontSize=9, fontName='Helvetica-Bold', textColor=TEAL,
                  spaceBefore=7, spaceAfter=2, leading=12)
ANS          = S('Ans',  fontSize=9,  textColor=DGRAY,  leading=13, spaceAfter=6,
                  leftIndent=12, alignment=TA_JUSTIFY)
LABEL        = S('Label', fontSize=8, textColor=DGRAY, leading=11, spaceAfter=2)
CAPTION      = S('Caption', fontSize=8, textColor=DGRAY, alignment=TA_CENTER, leading=10, spaceAfter=4)

# ── Helpers ───────────────────────────────────────────────────────────────────
def p(text, style=BODY):
    return Paragraph(text, style)

def h1(text):
    return Paragraph(text, H1)

def h2(text):
    return Paragraph(text, H2)

def h3(text):
    return Paragraph(text, H3)

def sp(h=4):
    return Spacer(1, h)

def hr():
    return HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceAfter=4)

def pb():
    return PageBreak()

def b(text):
    return Paragraph(f'<bullet>•</bullet> {text}', BULLET)

def tbl(data, col_widths=None, header=True):
    """Build a styled table. data[0] is header row."""
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    styles = [
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR',  (0, 0), (-1, 0), WHITE),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LGRAY]),
        ('GRID',       (0, 0), (-1, -1), 0.3, colors.HexColor('#CCCCCC')),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
    ]
    t.setStyle(TableStyle(styles))
    return t

def qa(q, a):
    return [p(q, QHEAD), p(a, ANS), sp(2)]

# ── Cover Page ────────────────────────────────────────────────────────────────
def cover():
    W, H = A4
    # Blue rectangle drawn via a one-cell table spanning full width
    cover_tbl = Table(
        [[Paragraph('PulseGuard', COVER_TITLE)],
         [Paragraph('Credit-Risk Model Governance Portfolio', COVER_SUB)],
         [Paragraph('Interview Defense Master Pack v5', COVER_SUB)],
         [sp(8)],
         [Paragraph('LightGBM + Isotonic Calibration &nbsp;|&nbsp; AUC=0.7769 &nbsp;|&nbsp; test ECE=0.0019', COVER_SUB)],
         [Paragraph('307,511 applicants &nbsp;|&nbsp; 140 features &nbsp;|&nbsp; 7 relational tables &nbsp;|&nbsp; 57.4M rows', COVER_SUB)],
         [sp(8)],
         [Paragraph('GOLD checkpoint 89.3% &nbsp;|&nbsp; All claims artifact-traced', COVER_SUB)],
         [sp(16)],
         [Paragraph('Sidharth Kriplani &nbsp;|&nbsp; 2026', COVER_SUB)],
        ],
        colWidths=[17*cm]
    )
    cover_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ROWSPAN', (0, 0), (0, -1), 1),
    ]))
    return [cover_tbl, pb()]

# ── Section 1: Project Identity ───────────────────────────────────────────────
def sec1():
    return [
        h1('1. Project Identity & Honest Framing'),
        h2('What PulseGuard Is'),
        p('PulseGuard is a <b>credit-risk model governance portfolio project</b>. It demonstrates the complete ML governance lifecycle on the Home Credit Default Risk public dataset: raw multi-table data ingestion, feature engineering across 7 relational tables, leakage-audited splits, a 12-model baseline tournament, Optuna HPO, isotonic calibration, 9-component composite champion selection, score-band policy, SHAP reason codes, fairness proxy audit, drift/PSI monitoring, and a local BM25+LLM governance assistant.'),
        h2('What PulseGuard Is NOT'),
        b('A production lending system or regulatory-compliant credit scoring deployment'),
        b('A legally certified adverse action notice generator'),
        b('A model approved for underwriting in any jurisdiction'),
        b('A system trained on real bank customer data'),
        b('A fairness-certified model under ECOA or equivalent regulation'),
        sp(4),
        h2('Strongest Safe One-Liner'),
        p('"End-to-end credit-risk governance stack: tuned LightGBM on 307k Home Credit applicants, calibrated PD scores (test ECE=0.0019, served isotonic), score-band policy, SHAP reason codes stable across 30 bootstrap resamples, fairness proxy audit, and a local RAG/LLM governance assistant — all under ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED constraints."'),
        h2('Why This Is Governance, Not Just a Model'),
        p('The model is only one layer. PulseGuard also produces: champion selection rationale (composite score, not AUC alone), calibrated probabilities with ECE documentation, score-band policy with semantic justification, SHAP reason codes with stability evidence, a fairness skeleton, drift monitoring baseline, RAG/LLM assistant with hard ASSISTIVE_ONLY constraints, and a full evidence ledger mapping every claim to a file.'),
        h2('Label Legend'),
        tbl([
            ['Label', 'Meaning'],
            ['[IMPLEMENTED]', 'Code exists, runs, and produces a verified artifact or measured output'],
            ['[PARTIALLY VERIFIED]', 'Code runs but validation is limited by public data, proxy fields, or sample constraints'],
            ['[SIMULATED]', 'Deliberately scenario-based or synthetic — e.g. cost matrix, policy demo'],
            ['[FUTURE]', 'Not built; explicitly absent or deferred'],
        ], [4*cm, 12.5*cm]),
        pb()
    ]

# ── Section 2: Dataset ────────────────────────────────────────────────────────
def sec2():
    return [
        h1('2. Dataset & Scope'),
        h2('Home Credit Default Risk (PRIMARY)  [IMPLEMENTED]'),
        tbl([
            ['Field', 'Value'],
            ['Source', 'Kaggle — Home Credit Default Risk public competition'],
            ['Applicants', '307,511'],
            ['Default rate', '8.07%  (scale_pos_weight = 11.39)'],
            ['Total rows', '57.4M across 7 side-tables'],
            ['Geography', 'Single Eastern European portfolio'],
            ['Timestamps', 'None — out-of-time split not possible'],
            ['Split', 'Stratified random 60/20/20, seed=42, DR preserved across all splits'],
        ], [5*cm, 11.5*cm]),
        sp(6),
        h2('Tables Used'),
        tbl([
            ['Table', 'Rows', 'Signal Domain'],
            ['application_train.csv', '307,511', 'Core applicant fields — base table'],
            ['bureau.csv', '1.7M', 'Credit bureau history per applicant'],
            ['bureau_balance.csv', '27.3M', 'Monthly bureau balance snapshots'],
            ['previous_application.csv', '1.67M', 'Prior Home Credit applications'],
            ['installments_payments.csv', '13.6M', 'Instalment payment history'],
            ['credit_card_balance.csv', '3.84M', 'Revolving credit card monthly snapshots'],
            ['POS_CASH_balance.csv', '10.0M', 'POS loan / cash advance history'],
        ], [5.5*cm, 3*cm, 8*cm]),
        sp(6),
        h2('Why Home Credit Is the Better Primary Spine'),
        b('10x more applicants than Taiwan Default (307k vs 30k)'),
        b('7 relational side-tables enable deep feature engineering (instalment ratios, bureau aggregates, POS DPD)'),
        b('Real external credit bureau signals (EXT_SOURCE_1/2/3) as primary risk drivers'),
        b('8.07% base rate matches real consumer-loan portfolios (vs 22% for Taiwan credit cards)'),
        b('SHA256 provenance verified — reproducible public download'),
        h2('Public-Data Limitations'),
        b('No temporal ordering — out-of-time split not possible'),
        b('Approved applicants only — reject inference unaddressed (MNAR selection bias)'),
        b('Single geography — no cross-market generalisation claim'),
        b('No real protected-class labels — fairness audit limited to proxies'),
        b('No income field — FOIR is a proxy (credit amount / goods price)'),
        pb()
    ]

# ── Section 3: Architecture ───────────────────────────────────────────────────
def sec3():
    return [
        h1('3. Architecture Overview'),
        tbl([
            ['Stage', 'Description', 'Status', 'Artifact'],
            ['Data audit', '8-table row counts, DR, scale_pos_weight, temporal feasibility', '[IMPLEMENTED]', 'g9a_home_credit_data_audit.json'],
            ['Feature factory', '140 features from 7 tables: ratios, aggregates, composites', '[IMPLEMENTED]', 'g9a_feature_factory_report.json'],
            ['Leakage audit', '10/10 checks: TARGET exclusion, val-only fit, no test contamination', '[IMPLEMENTED]', 'gold_pass1_leakage_audit.json'],
            ['Train/val/test split', 'Stratified 60/20/20, seed=42, DR=0.0807 preserved', '[IMPLEMENTED]', 'g9a_splits.pkl'],
            ['Baseline tournament', '12 models, 2 hard-failures, provisional champion CatBoost', '[IMPLEMENTED]', 'g9a_model_tournament_report.json'],
            ['Hyperparameter tuning', 'Optuna TPE, 5 models, validation-only, 4-8 trials', '[IMPLEMENTED]', 'gold_pass2_tuning_trace.json'],
            ['Calibration', 'Isotonic regression, val-only fit; numpy serving (no sklearn)', '[IMPLEMENTED]', 'gold_pass2_calibration_report.json'],
            ['Champion selection', '9-component composite; LightGBM_mono wins', '[IMPLEMENTED]', 'gold_pass2_champion_selection_report.json'],
            ['Final test evaluation', 'Single evaluation on 61,503-row test set', '[IMPLEMENTED]', 'gold_pass2_final_untouched_test_report.json'],
            ['Score bands', 'GREEN/AMBER/RED; PD-semantic; cost-sensitive', '[IMPLEMENTED]', 'gold_pass3_threshold_scoreband_report.json'],
            ['SHAP reason codes', 'pred_contrib; 20 global + 4 local cases; ECOA drafts', '[IMPLEMENTED]', 'gold_pass3_shap_reason_code_report.json'],
            ['Reason-code stability', '30 bootstraps; top-5 features 30/30 stable', '[IMPLEMENTED]', 'gold_pass3_reason_code_stability.json'],
            ['Fairness/proxy audit', 'Age, income, employment, region proxy groups', '[PARTIALLY VERIFIED]', 'gold_pass3_fairness_proxy_audit.json'],
            ['Drift/PSI baseline', 'val-vs-test PSI=0.0002; feature PSI STABLE', '[PARTIALLY VERIFIED]', 'gold_pass3_drift_vintage_stress.json'],
            ['RAG/LLM governance', '6-case BM25+LLM demo, abstain, ASSISTIVE_ONLY', '[SIMULATED]', 'gold_pass3_rag_llm_demo_report.json'],
            ['GP5 LSTM experiment', '1-layer LSTM encoder on installments; challenger AUC=0.7264', '[IMPLEMENTED]', 'gp5_augment_and_retrain.py'],
        ], [3.5*cm, 5.5*cm, 3*cm, 4.5*cm]),
        pb()
    ]

# ── Section 4: Feature Engineering ───────────────────────────────────────────
def sec4():
    return [
        h1('4. Feature Engineering  [IMPLEMENTED]'),
        p('140 features engineered from 7 source tables after constant/near-zero-variance removal. All imputation and transformations fit on train only and applied to val/test.'),
        h2('Application Table — Core Ratio Features'),
        tbl([
            ['Feature', 'Definition', 'Monotone'],
            ['CREDIT_TO_INCOME', 'Total credit / reported income (FOIR proxy)', '-'],
            ['CREDIT_TO_GOODS', 'Credit amount / goods price (LTV proxy)', '-'],
            ['CREDIT_TO_ANNUITY', 'Credit amount / annual instalment (repayment capacity)', '-'],
            ['ANNUITY_TO_INCOME', 'Proposed annual repayment / income (DSR)', '-'],
            ['AGE_YEARS', 'Applicant age in years', '-1 (older = lower risk)'],
            ['EMPLOYED_YEARS', 'Employment tenure in years (sentinel fix applied)', '-1'],
            ['FLAG_EMPLOYED_ANOMALY', 'Binary: DAYS_EMPLOYED=365243 (not employed)', '-'],
        ], [4.5*cm, 8*cm, 4*cm]),
        sp(4),
        h2('Bureau Aggregates (bureau + bureau_balance)'),
        tbl([
            ['Feature', 'Definition', 'Monotone'],
            ['BUREAU_ACTIVE_COUNT', 'Number of active bureau credit lines', '-'],
            ['BUREAU_OVERDUE_RATIO', 'Overdue accounts / total accounts', '+1'],
            ['BUREAU_AMT_OVERDUE', 'Total outstanding overdue balance', '+1'],
            ['BB_DPD_RATIO_MEAN', 'Mean DPD ratio across bureau balance records', '+1'],
        ], [4.5*cm, 8*cm, 4*cm]),
        sp(4),
        h2('Previous Application + Instalment + Credit Card + POS Features'),
        tbl([
            ['Feature', 'Source Table', 'Monotone'],
            ['PREV_REFUSAL_RATE', 'previous_application', '+1'],
            ['PREV_AMT_CREDIT_MEAN', 'previous_application', '-'],
            ['INST_LATE_RATIO', 'installments_payments (rank-4 SHAP)', '+1'],
            ['CC_DPD_RATIO', 'credit_card_balance', '+1'],
            ['CC_ATM_RATIO', 'credit_card_balance', '-'],
            ['POS_IS_DPD_RATIO', 'POS_CASH_balance', '+1'],
        ], [5*cm, 5.5*cm, 6*cm]),
        sp(4),
        h2('Composite Feature'),
        p('BEHAVIORAL_RISK_SCORE = 0.4 x INST_LATE_RATIO + 0.3 x CC_DPD_RATIO + 0.2 x POS_IS_DPD_RATIO + 0.1 x BUREAU_OVERDUE_RATIO'),
        p('Remaining ~120 features: one-hot encoded categoricals (NAME_CONTRACT_TYPE, CODE_GENDER, etc.), raw numeric fields from application_train (AMT_GOODS_PRICE, EXT_SOURCE_1/2/3, OWN_CAR_AGE, etc.), and additional aggregates from side-tables. All passed through LightGBM which handles missing values natively.'),
        h2('Leakage Controls'),
        b('TARGET excluded from all feature sets — confirmed by 10/10 pre-tuning leakage audit'),
        b('Post-outcome bureau fields reviewed; DAYS_DECISION in side-tables controlled'),
        b('Group leakage: 0 SK_ID_CURR overlap between train and test (confirmed by GP1 audit check #5)'),
        b('Calibrator fit on val only — never on train, never on test'),
        pb()
    ]

# ── Section 5: Model Tournament ───────────────────────────────────────────────
def sec5():
    return [
        h1('5. Model Tournament'),
        h2('Baseline Tournament — G9A  [IMPLEMENTED]'),
        p('12 models run with near-default hyperparameters as a pre-tuning audit. Purpose: establish competitive ordering and confirm leakage-free pipeline, not find the best model.'),
        tbl([
            ['Model', 'Val AUC', 'Status'],
            ['CatBoost + Platt', '0.7716', 'Provisional baseline champion'],
            ['XGBoost + Platt', '0.7703', 'Contender'],
            ['LightGBM_base + Platt', '0.7203', 'BUG: early stopping fires at iteration 1 with scale_pos_weight=11.39'],
            ['LightGBM_monotonic + Platt', '0.7203', 'Same bug as LightGBM_base'],
            ['Random Forest', '0.70', 'REJECTED — insufficient AUC on 140-feature space'],
            ['Logistic Regression', '0.65', 'REJECTED — linear boundary insufficient'],
            ['TabNet', 'HARD_FAIL', 'CPU ~6 min/epoch; estimated 400-800h on 184k rows'],
            ['sklearn GBM', 'HARD_FAIL', 'Wall-time exceeded on CPU sandbox'],
        ], [5.5*cm, 2.5*cm, 8.5*cm]),
        sp(6),
        h2('Tuned Tournament — Gold Pass 2  [IMPLEMENTED]'),
        p('5 models tuned with Optuna TPE. LightGBM early-stopping bug fixed: n_estimators treated as a search parameter (200-1000 range), early stopping removed.'),
        tbl([
            ['Model', 'Val AUC', 'Composite Score', 'Role'],
            ['LightGBM_monotonic', '0.7734', '0.7312', 'CHAMPION + GOVERNANCE'],
            ['XGBoost_monotonic', '0.7699', '0.7294', 'Contender'],
            ['LightGBM_base', '0.7724', '0.6811', 'Contender (no governance premium)'],
            ['CatBoost', '0.7708', '0.6802', 'Contender (no monotone constraints)'],
            ['XGBoost', '0.7704', '0.6801', 'Contender'],
        ], [5*cm, 2.5*cm, 3*cm, 5.5*cm]),
        sp(6),
        h2('Early Stopping Bug — Root Cause'),
        p('With eval_metric="auc" and early_stopping_rounds=50 on scale_pos_weight=11.39 imbalanced data, the first tree dominates AUC improvement. Subsequent marginal gains fall below tolerance. Training halts at 1-9 trees. Model looks normal but is severely undertrained. Fix: remove early stopping; treat n_estimators as Optuna hyperparameter.'),
        pb()
    ]

# ── Section 6: Hyperparameter Tuning ─────────────────────────────────────────
def sec6():
    return [
        h1('6. Hyperparameter Tuning  [IMPLEMENTED]'),
        tbl([
            ['Field', 'Value'],
            ['Algorithm', 'Optuna Tree-structured Parzen Estimator (TPE)'],
            ['Seed', '42'],
            ['Budget', '35-second wall-clock per model (CPU-only sandbox, 44s bash limit)'],
            ['Trial counts', 'LightGBM_base: 6  |  LightGBM_mono: 5  |  CatBoost: 8  |  XGBoost: 4  |  XGBoost_mono: 4'],
            ['Champion selection', 'Validation set only — test set never touched during HPO'],
            ['Calibration', 'Fit on val only — after HPO, before test evaluation'],
            ['Test evaluation', 'Exactly once, after champion locked'],
        ], [4.5*cm, 12*cm]),
        sp(6),
        h2('Search Space (LightGBM_monotonic)'),
        tbl([
            ['Hyperparameter', 'Range', 'Best Value'],
            ['n_estimators', '200-1000', 'Best trial value (see tuning_trace.json)'],
            ['num_leaves', '31-255', 'TPE-selected'],
            ['learning_rate', '0.01-0.3 (log)', 'TPE-selected'],
            ['max_depth', '3-12', 'TPE-selected'],
            ['subsample', '0.5-1.0', 'TPE-selected'],
            ['colsample_bytree', '0.5-1.0', 'TPE-selected'],
            ['reg_lambda (L2)', '1e-3 to 10 (log)', 'TPE-selected'],
            ['reg_alpha (L1)', '1e-3 to 10 (log)', 'TPE-selected'],
            ['min_child_samples', '10-100', 'TPE-selected'],
        ], [5*cm, 3.5*cm, 7.5*cm]),
        sp(4),
        p('<b>Interview note:</b> Trial counts (4-8) are lower than the 100-trial plan in the tuning spec. CPU sandbox with 44s bash limit is the constraint. The planning document specifies 100 trials; actual counts are documented in gold_pass2_tuning_trace.json. Results represent a reasonable local optimum. On GPU with 100 trials: estimated 0.001-0.003 further AUC improvement.'),
        pb()
    ]

# ── Section 7: Champion Model ─────────────────────────────────────────────────
def sec7():
    return [
        h1('7. Champion Model  [IMPLEMENTED]'),
        h2('LightGBM with Monotone Constraints + Isotonic Calibration'),
        tbl([
            ['Field', 'Value'],
            ['Model family', 'LightGBM Gradient Boosted Trees (leaf-wise growth, histogram splits)'],
            ['Variant', '15 monotone constraints — 12 at +1 (risk-increasing), 3 at -1 (risk-decreasing)'],
            ['Calibration', 'Isotonic regression (val-only fit), served as numpy interp — zero sklearn dependency'],
            ['Composite score', '0.7312 (9-component selection)'],
        ], [4.5*cm, 12*cm]),
        sp(6),
        h2('Performance Metrics'),
        tbl([
            ['Metric', 'Val', 'Test (Final, Untouched)', 'Interpretation'],
            ['AUC', '0.7734', '0.7769', 'P(defaulter ranks above non-defaulter)'],
            ['PR-AUC', '0.2661', '0.2628', '3.3x random baseline at 8% DR'],
            ['KS', '0.4121', '0.4141', 'Max CDF separation; >0.40 is strong'],
            ['ECE', '0.0051', '0.0019 / 0.0034', 'served isotonic / Platt (frozen report)'],
            ['Brier', '-', '0.0668', 'Mean squared error of probability predictions'],
        ], [2.5*cm, 2*cm, 4.5*cm, 7.5*cm]),
        sp(6),
        h2('9-Component Composite Score Breakdown'),
        tbl([
            ['Component', 'Weight', 'LightGBM_mono', 'CatBoost'],
            ['Val AUC (normalised)', '25%', '0.7734', '0.7708'],
            ['Val PR-AUC (normalised)', '15%', '0.2661', '0.2578'],
            ['KS statistic', '15%', '0.4121', '0.4094'],
            ['ECE (inverted)', '15%', '0.0051', '0.0098'],
            ['Explainability (SHAP+mono)', '10%', '1.00', '0.50'],
            ['Adverse-reason readiness', '5%', '1.00', '0.50'],
            ['Inference latency', '5%', 'fast', 'slower'],
            ['Calibration method quality', '5%', 'isotonic', 'platt only'],
            ['Governance premium (monotone)', '5%', 'YES', 'NO'],
            ['COMPOSITE SCORE', '100%', '0.7312', '0.6802'],
        ], [6*cm, 1.8*cm, 3.5*cm, 3.5*cm]),
        sp(4),
        h2('Why Monotone Constraints Matter'),
        p('Monotone constraints guarantee directional interpretability auditable without per-applicant SHAP. A credit officer can verify: "for any two applicants identical in all features except BUREAU_OVERDUE_RATIO, the one with the higher ratio will always receive a higher predicted default probability." This is an SR 26-2-aligned interpretability property. Cost: some split flexibility. In practice, LightGBM_mono AUC (0.7734) exceeds LightGBM_base (0.7724) — constraints act as effective regularisation on the 140-feature space.'),
        pb()
    ]

# ── Section 8: Calibration ────────────────────────────────────────────────────
def sec8():
    return [
        h1('8. Calibration  [IMPLEMENTED]'),
        tbl([
            ['Step', 'Detail'],
            ['Calibrator', 'IsotonicRegression(out_of_bounds="clip") — piecewise-monotone interpolation'],
            ['Fit data', 'Validation set only'],
            ['Platt', 'Also evaluated (val-fit); frozen GP2 test report scored Platt at ECE=0.0034'],
            ['Test ECE', '0.0019 served isotonic (audit) / 0.0034 Platt (frozen report); raw 0.295'],
            ['Serving', 'Extracted as iso_x.npy and iso_y.npy — np.interp(raw_prob, iso_x, iso_y) — zero sklearn dependency'],
            ['Raw GBM ECE', '0.296 (uncalibrated) — calibration reduces ECE by ~98%'],
        ], [4.5*cm, 12*cm]),
        sp(6),
        h2('Calibration Forensics Discovery'),
        p('The frozen GP2 single-shot test report labels its calibrator "Platt" (test ECE=0.0034). The model actually served by app.py uses the isotonic calibrator (iso_x.npy / iso_y.npy). An audit recomputed both on the same 61,503-row held-out test set: served isotonic ECE=0.0019, Platt ECE=0.0034 — isotonic is served because it has the lower test ECE.'),
        h2('The Numpy Serving Solution'),
        p('''iso_x = iso.X_thresholds_   # shape (134,) — raw probability thresholds
iso_y = iso.y_thresholds_   # shape (134,) — calibrated probability values
# At serve time — exact replication, zero sklearn:
calibrated_prob = float(np.interp(raw_prob, iso_x, iso_y))'''),
        p('np.interp implements the same piecewise-linear interpolation that IsotonicRegression.predict() uses. Max difference between the two: 0.0 across all test values. This eliminates sklearn version lock at serve time entirely.'),
        h2('Why Calibrated PD Matters'),
        b('A raw GBM score is not a probability — it is an uncalibrated log-odds output'),
        b('After isotonic calibration, PD=0.20 means the model genuinely estimates a 20% default probability'),
        b('Enables semantically defensible score-band thresholds'),
        b('Enables the cost-sensitive threshold formula: theta* = C_reject / (C_bad + C_reject)'),
        b('ECE is a measurable governance metric — served isotonic 0.0019; Platt 0.0034 in frozen report'),
        pb()
    ]

# ── Section 9: Score Bands ────────────────────────────────────────────────────
def sec9():
    return [
        h1('9. Thresholds & Score Bands  [IMPLEMENTED]'),
        tbl([
            ['Band', 'Threshold', 'Test %', 'Test DR', 'Policy'],
            ['GREEN', 'PD < 0.20', '89.72%', '5.77%', 'Auto-approve eligible (subject to hard-stop check)'],
            ['AMBER', '0.20 <= PD < 0.40', '9.80%', '26.96%', 'Manual credit officer review required'],
            ['RED', 'PD >= 0.40', '0.47%', '53.77%', 'Enhanced underwriting or decline'],
        ], [2*cm, 3*cm, 2.5*cm, 2.5*cm, 6.5*cm]),
        sp(6),
        h2('Threshold Justification'),
        p('<b>PD=0.20 semantic justification:</b> At this boundary the model estimates 20% default probability. The GREEN band observed DR (5.77%) is materially below 20%, confirming conservative assignment. Defensible to auditor: "applicants below this line have a predicted default probability under 20%."'),
        p('<b>Cost-sensitive analysis</b> [SIMULATED]: Under scenario economics (C_bad=10, C_reject=1, C_review=0.3), the cost-optimal single threshold is 0.47 with expected loss 0.0807/applicant. These are scenario assumptions, not real bank economics. Operational threshold requires real LGD, NIM, and regulatory capital parameters.'),
        h2('Three Threshold Methods Evaluated'),
        tbl([
            ['Method', 'Threshold', 'Approval Rate', 'DR', 'Assessment'],
            ['KS-optimal', '0.0961', '50.7%', '5.6%', 'Too aggressive for practical policy'],
            ['Cost-optimal (C_bad=10, C_reject=1)', '0.47', '~99%', '~8%', 'Scenario-assumed; not real bank econ'],
            ['PD-semantic (CHOSEN)', '0.20 / 0.40', '89.7% / 9.8% / 0.5%', 'Banded', 'Interpretable; defensible to auditor'],
        ], [5*cm, 2.5*cm, 2.5*cm, 2*cm, 4.5*cm]),
        pb()
    ]

# ── Section 10: SHAP ──────────────────────────────────────────────────────────
def sec10():
    return [
        h1('10. SHAP Reason Codes & Stability  [IMPLEMENTED]'),
        h2('Method'),
        p('LightGBM built-in pred_contrib=True (native SHAP TreeExplainer implementation). Avoids external SHAP library — which had a pandas index compatibility issue with non-default-indexed DataFrames. Native implementation is equivalent for tree models and zero additional dependencies.'),
        h2('Global Feature Importance (mean |SHAP|, 1000-sample draw)'),
        tbl([
            ['Rank', 'Feature', 'Mean |SHAP|', 'Monotone', 'Human Label'],
            ['1', 'EXT_SOURCE_MEAN', '0.510', '-1', 'External credit bureau composite score'],
            ['2', 'CREDIT_TO_ANNUITY', '0.141', 'N/A', 'Credit amount vs annual repayment capacity'],
            ['3', 'CREDIT_TO_GOODS', '0.139', 'N/A', 'Loan-to-goods-value ratio'],
            ['4', 'INST_LATE_RATIO', '0.129', '+1', 'Proportion of late instalment payments'],
            ['5', 'EXT_SOURCE_1', '0.120', 'N/A', 'External bureau score 1'],
            ['6', 'OWN_CAR_AGE', '0.092', 'N/A', 'Vehicle age (ownership proxy)'],
            ['7', 'EMPLOYED_YEARS', '0.091', '-1', 'Employment tenure'],
            ['8', 'BUREAU_ACTIVE_COUNT', '0.087', 'N/A', 'Active bureau credit lines'],
            ['9', 'AMT_GOODS_PRICE', '0.082', 'N/A', 'Goods price of financed item'],
            ['10', 'EXT_SOURCE_3', '0.078', 'N/A', 'External bureau score 3'],
        ], [1.5*cm, 4.5*cm, 2.5*cm, 2.5*cm, 5.5*cm]),
        sp(6),
        h2('Local Cases Computed'),
        tbl([
            ['Case', 'PD', 'Band', 'Primary Driver', 'SHAP Value'],
            ['GREEN_APPROVE', '0.0335', 'GREEN', 'EXT_SOURCE_MEAN', '-0.829'],
            ['AMBER_REVIEW', '0.2056', 'AMBER', 'EXT_SOURCE_MEAN', '+0.939'],
            ['RED_HIGH_RISK', '0.4164', 'RED', 'EXT_SOURCE_MEAN', '+1.300'],
            ['AMBER_CONFLICT', '0.3475', 'AMBER', 'EXT_SOURCE_MEAN', '+1.232'],
        ], [3.5*cm, 2*cm, 2.5*cm, 4.5*cm, 3*cm]),
        sp(6),
        h2('Bootstrap Stability (30 Iterations x 500-row Samples)'),
        tbl([
            ['Feature', 'Top-5 Presence', 'Rank-1 Count', 'Stability Tier'],
            ['EXT_SOURCE_MEAN', '30/30', '30/30', 'HIGH'],
            ['EXT_SOURCE_1', '30/30', '-', 'HIGH'],
            ['CREDIT_TO_GOODS', '30/30', '-', 'HIGH'],
            ['CREDIT_TO_ANNUITY', '30/30', '-', 'HIGH'],
            ['INST_LATE_RATIO', '30/30', '-', 'HIGH'],
        ], [4.5*cm, 3*cm, 2.5*cm, 6.5*cm]),
        sp(4),
        p('EXT_SOURCE_MEAN is rank-1 in all 30 bootstraps. Top-5 reason-code set is robust to sampling variation — suitable for production adverse-action drafting (subject to officer review).'),
        h2('Adverse-Action Language (Draft, ASSISTIVE_ONLY)'),
        b('EXT_SOURCE_MEAN: "External credit bureau composite score below threshold"'),
        b('INST_LATE_RATIO: "High proportion of late instalment payments"'),
        b('CREDIT_TO_ANNUITY: "Credit amount high relative to annual repayment capacity"'),
        b('CREDIT_TO_GOODS: "Loan-to-goods-value ratio elevated"'),
        p('<b>These are draft aids, not legally compliant adverse action notices.</b> ECOA/Regulation B requires reason codes from an approved list, reviewed by a licensed credit officer.'),
        pb()
    ]

# ── Section 11: Fairness ──────────────────────────────────────────────────────
def sec11():
    return [
        h1('11. Fairness / Proxy Audit  [PARTIALLY VERIFIED]'),
        p('Proxy-variable analysis on 61,503-row test set. No protected-class labels available in Home Credit. Scope explicitly: skeleton, not certification.'),
        tbl([
            ['Proxy Group', 'Approval Rate', 'Observed DR', 'Assessment'],
            ['Age < 30', '80.5%', '11.5%', 'DR differential explains approval gap'],
            ['Age 30-50', '88.6%', '8.8%', 'Baseline cohort'],
            ['Age 50+', '95.5%', '5.6%', 'Lower DR explains higher approval'],
            ['Income low tercile', '89.0%', '8.1%', 'Narrow spread across terciles'],
            ['Income mid tercile', '88.5%', '8.8%', 'Baseline'],
            ['Income high tercile', '91.3%', '7.5%', 'Slight improvement with higher income'],
            ['Employed', '88.3%', '8.7%', 'Normal'],
            ['Not-employed proxy', '96.2%', '5.2%', 'Sentinel encodes retired/students — lower DR'],
            ['Region 1 (low-risk)', '96.5%', '4.9%', 'DR differential explains gap'],
            ['Region 3 (high-risk)', '81.7%', '11.2%', 'DR differential explains gap'],
        ], [4.5*cm, 3*cm, 2.5*cm, 6.5*cm]),
        sp(4),
        h2('What This Proves vs Does Not Prove'),
        p('<b>What this proves:</b> No evidence of model amplifying approval-rate disparities beyond base-rate differences. Model appears to differentiate risk, not proxy demographics.'),
        p('<b>What it does NOT prove:</b> Not a fairness certification. Disparate Impact ratio not computable (no protected-class labels). A full ECOA/fair-lending review would require demographic enrichment and independent analysis.'),
        pb()
    ]

# ── Section 12: Drift ─────────────────────────────────────────────────────────
def sec12():
    return [
        h1('12. Drift / PSI Baseline  [PARTIALLY VERIFIED]'),
        tbl([
            ['Comparison', 'PSI', 'Interpretation'],
            ['val vs test', '0.0002', 'STABLE — key operational metric'],
            ['train vs val', '~8.10', 'Platt/isotonic calibration artefact (not a drift signal)'],
        ], [4*cm, 2.5*cm, 10*cm]),
        sp(4),
        p('The train PSI is explained by the isotonic calibrator being fit on val-set scores. The calibrated val/test distribution is consistent (PSI=0.0002). All top-10 feature PSIs between train and test are below 0.001.'),
        h2('AUC by Split'),
        tbl([
            ['Split', 'AUC', 'Interpretation'],
            ['Train', '0.8526', 'In-sample (expected overfitting)'],
            ['Val', '0.7734', 'Out-of-sample estimate'],
            ['Test', '0.7769', 'Final untouched evaluation (better than val — within noise)'],
        ], [3*cm, 2.5*cm, 11*cm]),
        sp(4),
        h2('Production Monitoring Policy (DOCUMENTED)'),
        tbl([
            ['PSI Range', 'Status', 'Action', 'SLA'],
            ['PSI < 0.10', 'STABLE', 'No action required', '-'],
            ['0.10 - 0.25', 'SLIGHT_SHIFT', 'Model owner review', '30 days'],
            ['PSI > 0.25', 'SIGNIFICANT_SHIFT', 'MRC escalation', '5 business days'],
        ], [3*cm, 3*cm, 4.5*cm, 5.5*cm]),
        sp(4),
        b('If monthly KS drops > 0.05 from deployment baseline (0.4141): emergency model review regardless of PSI'),
        b('Approve-zone observed DR WARN at 2x baseline (10%), ALERT at 25%, CRITICAL at 35%'),
        p('<b>True vintage validation [FUTURE]:</b> Requires timestamped application data. Home Credit has none. Monthly PSI monitoring on score distribution + top-10 features is the production monitoring recommendation.'),
        pb()
    ]

# ── Section 13: RAG/LLM ───────────────────────────────────────────────────────
def sec13():
    return [
        h1('13. RAG / LLM Governance Assistant  [SIMULATED]'),
        h2('Architecture'),
        tbl([
            ['Component', 'Implementation'],
            ['Retriever', 'BM25 over 5-document policy corpus'],
            ['Abstain threshold', 'BM25 top-score < 0.25 — no output (prevents hallucinated policy citations)'],
            ['LLM role', 'Draft memo and adverse-action language from retrieved policy section'],
            ['Hard rule', 'LLM NEVER autonomously approves or rejects applicant in any case'],
            ['All outputs', 'ASSISTIVE_ONLY + HUMAN_REVIEW_REQUIRED + NOT_FINAL_DECISION'],
        ], [4*cm, 12.5*cm]),
        sp(6),
        h2('6-Case Demonstration'),
        tbl([
            ['Case', 'Band', 'Retrieved Policy', 'LLM Output', 'Abstain'],
            ['GREEN_APPROVE', 'GREEN', 'POL-001 (Score Band Policy)', 'Approval eligibility memo', 'No'],
            ['AMBER_REVIEW', 'AMBER', 'POL-001', 'Review memo + top-3 SHAP drivers', 'No'],
            ['RED_DECLINE', 'RED', 'POL-002 (Adverse Action Policy)', 'Adverse-action draft + 3 reason codes', 'No'],
            ['CONFLICT_OVERRIDE', 'AMBER', 'POL-004 (Override Protocol)', 'Override checklist; officer authority noted', 'No'],
            ['OUT_OF_DOMAIN', 'N/A', 'None (BM25=0.0)', 'ABSTAIN — no output generated', 'YES'],
            ['DRIFT_ALERT', 'MONITOR', 'POL-003 (Monitoring Policy)', 'MRC escalation memo', 'No'],
        ], [3.5*cm, 2*cm, 4*cm, 4*cm, 1.5*cm]),
        sp(4),
        p('<b>What the LLM supports:</b> Draft memos, reason-code language, policy lookups, checklist generation, escalation flagging.'),
        p('<b>What the LLM NEVER does:</b> Make or suggest credit approval/rejection, claim legal compliance, access live applicant data, produce output when BM25 < 0.25.'),
        pb()
    ]

# ── Section 14: Evidence Ledger ───────────────────────────────────────────────
def sec14():
    return [
        h1('14. Evidence Artifacts Ledger'),
        tbl([
            ['Artifact', 'Key Numbers', 'Claim Enabled'],
            ['gold_pass1_leakage_audit.json', '10/10 PASS, safe_to_tune=true', 'No target or post-outcome leakage'],
            ['gold_pass1_data_spine_validation.json', '21/21 PASS, 0 ID overlap', 'No data leakage between splits'],
            ['gold_pass2_tuning_trace.json', '5 models, 4-8 trials', 'Validation-only Optuna HPO'],
            ['gold_pass2_calibration_report.json', 'Isotonic ECE_val=0.0051', 'Isotonic calibration selected'],
            ['gold_pass2_champion_selection_report.json', 'Composite=0.7312', '9-component composite champion'],
            ['gold_pass2_final_untouched_test_report.json', 'AUC=0.7769, ECE=0.0034 (Platt; served isotonic 0.0019 per audit)', 'Final test: AUC=0.7769'],
            ['gold_pass3_threshold_scoreband_report.json', 'GREEN 89.7%, AMBER 9.8%, RED 0.5%', 'Score-band policy'],
            ['gold_pass3_shap_reason_code_report.json', 'EXT_SOURCE_MEAN=0.510, 4 local cases', 'SHAP reason codes'],
            ['gold_pass3_reason_code_stability.json', '30/30 top-5, 30/30 rank-1', 'Reason codes stable across bootstraps'],
            ['gold_pass3_fairness_proxy_audit.json', '4 proxy groups, aligned with DR', 'Fairness proxy audit skeleton'],
            ['gold_pass3_drift_vintage_stress.json', 'PSI=0.0002, all features STABLE', 'val-vs-test PSI=0.0002 STABLE'],
            ['gold_pass3_rag_llm_demo_report.json', '6 cases, abstain fires', 'RAG/LLM 6-case governance demo'],
            ['pulseguard_final_gold_audit.json', '89.3%, GOLD', 'PulseGuard is GOLD checkpointed'],
            ['docs/PULSEGUARD_MODEL_CARD.md', 'All lifecycle fields', 'Complete model card'],
            ['04_EVIDENCE_LEDGER.md', 'All claims traced', 'Every claim has an artifact'],
            ['06_CLAIM_BOUNDARY.md', 'Safe/forbidden per gate', 'Claim boundary maintained'],
        ], [6.5*cm, 4.5*cm, 5.5*cm]),
        pb()
    ]

# ── Section 14b: Full Feature Catalogue ──────────────────────────────────────
def sec14b():
    return [
        h1('14b. Feature Catalogue — All 140 Features by Source Table'),
        h2('application_train.csv — Base Features'),
        tbl([
            ['Feature', 'Type', 'Monotone', 'Description'],
            ['CREDIT_TO_INCOME', 'ratio', '-', 'AMT_CREDIT / AMT_INCOME_TOTAL — debt-to-income proxy'],
            ['CREDIT_TO_GOODS', 'ratio', '-', 'AMT_CREDIT / AMT_GOODS_PRICE — LTV proxy'],
            ['CREDIT_TO_ANNUITY', 'ratio', '-', 'AMT_CREDIT / AMT_ANNUITY — repayment capacity'],
            ['ANNUITY_TO_INCOME', 'ratio', '-', 'AMT_ANNUITY / AMT_INCOME_TOTAL — debt service ratio'],
            ['AGE_YEARS', 'transformed', '-1', 'DAYS_BIRTH / -365 — older applicants lower risk'],
            ['EMPLOYED_YEARS', 'transformed', '-1', 'DAYS_EMPLOYED / -365; sentinel-corrected'],
            ['FLAG_EMPLOYED_ANOMALY', 'binary', '-', '1 if DAYS_EMPLOYED=365243 (not employed encoding)'],
            ['EXT_SOURCE_MEAN', 'aggregate', '-1', 'Mean of EXT_SOURCE_1/2/3 — rank-1 SHAP driver'],
            ['EXT_SOURCE_1', 'raw', '-', 'External bureau score 1'],
            ['EXT_SOURCE_2', 'raw', '-', 'External bureau score 2'],
            ['EXT_SOURCE_3', 'raw', '-', 'External bureau score 3'],
            ['AMT_CREDIT', 'raw', '-', 'Loan amount requested'],
            ['AMT_INCOME_TOTAL', 'raw', '-', 'Applicant annual income'],
            ['AMT_ANNUITY', 'raw', '-', 'Proposed annual loan payment'],
            ['AMT_GOODS_PRICE', 'raw', '-', 'Price of financed goods'],
            ['OWN_CAR_AGE', 'raw', '-', 'Age of car owned (null if no car)'],
            ['DAYS_REGISTRATION', 'raw', '-', 'Days since current registration'],
            ['DAYS_ID_PUBLISH', 'raw', '-', 'Days since ID was published/changed'],
            ['CNT_FAM_MEMBERS', 'raw', '-', 'Number of family members'],
            ['CNT_CHILDREN', 'raw', '-', 'Number of children'],
            ['REGION_RATING_CLIENT', 'raw', '+1', 'Client region rating — higher is riskier'],
            ['REGION_RATING_CLIENT_W_CITY', 'raw', '+1', 'City-adjusted region rating'],
            ['NAME_CONTRACT_TYPE', 'onehot', '-', 'Cash loan vs revolving'],
            ['CODE_GENDER', 'onehot', '-', 'M/F encoding'],
            ['FLAG_OWN_CAR', 'binary', '-', 'Owns a car'],
            ['FLAG_OWN_REALTY', 'binary', '-', 'Owns real estate'],
            ['NAME_INCOME_TYPE', 'onehot', '-', 'Working/Pensioner/etc.'],
            ['NAME_EDUCATION_TYPE', 'onehot', '-', 'Education level'],
            ['NAME_FAMILY_STATUS', 'onehot', '-', 'Marital status'],
            ['NAME_HOUSING_TYPE', 'onehot', '-', 'Housing situation'],
            ['OCCUPATION_TYPE', 'onehot', '-', 'Occupation category'],
            ['FLAG_WORK_PHONE / FLAG_PHONE / FLAG_EMAIL', 'binary', '-', 'Contact flags'],
            ['REG_REGION_NOT_LIVE_REGION', 'binary', '+1', 'Address vs residence mismatch'],
            ['LIVE_CITY_NOT_WORK_CITY', 'binary', '+1', 'Lives and works in different cities'],
            ['DAYS_LAST_PHONE_CHANGE', 'raw', '-', 'Recency of phone number change'],
        ], [5.5*cm, 2.5*cm, 2*cm, 6.5*cm]),
        sp(6),
        h2('bureau.csv + bureau_balance.csv — Credit Bureau Features'),
        tbl([
            ['Feature', 'Monotone', 'Description'],
            ['BUREAU_ACTIVE_COUNT', '-', 'Number of currently active credit bureau accounts'],
            ['BUREAU_CLOSED_COUNT', '-', 'Number of closed bureau accounts'],
            ['BUREAU_TOTAL_COUNT', '-', 'Total number of bureau accounts (active + closed)'],
            ['BUREAU_OVERDUE_RATIO', '+1', 'Overdue accounts / total bureau accounts'],
            ['BUREAU_AMT_CREDIT_SUM', '-', 'Sum of all bureau credit amounts'],
            ['BUREAU_AMT_CREDIT_DEBT', '+1', 'Total outstanding bureau debt'],
            ['BUREAU_AMT_OVERDUE', '+1', 'Total overdue balance across bureau accounts'],
            ['BUREAU_CREDIT_TYPE_COUNT', '-', 'Count of distinct credit types in bureau'],
            ['BUREAU_MAX_OVERDUE_AMT', '+1', 'Maximum single overdue amount in bureau'],
            ['BUREAU_AVG_DAYS_CREDIT', '-', 'Average age of bureau credit lines (days)'],
            ['BB_DPD_RATIO_MEAN', '+1', 'Mean DPD ratio across bureau balance monthly records'],
            ['BB_DPD_RATIO_MAX', '+1', 'Maximum DPD ratio in bureau balance history'],
            ['BB_STATUS_ACTIVE_RATIO', '-', 'Fraction of bureau balance records with active status'],
            ['BB_STATUS_DPD_RATIO', '+1', 'Fraction of bureau balance records showing DPD'],
        ], [5.5*cm, 2*cm, 9*cm]),
        sp(6),
        h2('previous_application.csv — Prior Application Features'),
        tbl([
            ['Feature', 'Monotone', 'Description'],
            ['PREV_APP_COUNT', '-', 'Total number of prior Home Credit applications'],
            ['PREV_APPROVED_COUNT', '-', 'Number of prior approved applications'],
            ['PREV_REFUSED_COUNT', '+1', 'Number of prior refused applications'],
            ['PREV_REFUSAL_RATE', '+1', 'PREV_REFUSED_COUNT / PREV_APP_COUNT — rank-signal feature'],
            ['PREV_AMT_CREDIT_MEAN', '-', 'Mean credit amount in prior applications'],
            ['PREV_AMT_ANNUITY_MEAN', '-', 'Mean annuity in prior applications'],
            ['PREV_DAYS_DECISION_MEAN', '-', 'Mean days since prior application decision'],
            ['PREV_PRODUCT_TYPE_CASH_RATIO', '-', 'Fraction of prior apps for cash loans'],
            ['PREV_CNT_PAYMENT_MEAN', '-', 'Mean contracted payment count in prior loans'],
        ], [5.5*cm, 2*cm, 9*cm]),
        sp(6),
        h2('installments_payments.csv — Payment Behaviour Features'),
        tbl([
            ['Feature', 'Monotone', 'Description'],
            ['INST_LATE_RATIO', '+1', 'Late payments / total payments — rank-4 global SHAP feature'],
            ['INST_PAY_RATIO', '-', 'Mean (actual_payment / scheduled_payment) — underpayment proxy'],
            ['INST_DPD_MEAN', '+1', 'Mean days past due across all instalment records'],
            ['INST_DPD_MAX', '+1', 'Maximum DPD in instalment history'],
            ['INST_PAYMENT_DIFF_MEAN', '+1', 'Mean shortfall between scheduled and actual payment'],
            ['INST_AMT_INSTALMENT_SUM', '-', 'Total instalment amount across all payments'],
            ['INST_NUM_INSTALMENT_MEAN', '-', 'Mean instalments per prior loan'],
            ['INST_OVERPAY_RATIO', '-', 'Ratio of overpayments in instalment history'],
        ], [5.5*cm, 2*cm, 9*cm]),
        sp(6),
        h2('credit_card_balance.csv + POS_CASH_balance.csv — Revolving/POS Features'),
        tbl([
            ['Feature', 'Source', 'Monotone', 'Description'],
            ['CC_DPD_RATIO', 'credit_card_balance', '+1', 'Credit card days-past-due ratio across monthly records'],
            ['CC_ATM_RATIO', 'credit_card_balance', '-', 'ATM withdrawal / total credit card drawings'],
            ['CC_BALANCE_TO_LIMIT', 'credit_card_balance', '+1', 'Mean credit utilisation ratio on credit cards'],
            ['CC_PAYMENT_RATIO', 'credit_card_balance', '-', 'Mean actual / min payment ratio on cards'],
            ['CC_OVERDUE_COUNT', 'credit_card_balance', '+1', 'Count of months with credit card DPD > 0'],
            ['POS_IS_DPD_RATIO', 'POS_CASH_balance', '+1', 'POS instalment days-past-due ratio'],
            ['POS_CNT_INSTALMENT_MEAN', 'POS_CASH_balance', '-', 'Mean contracted instalment count (POS)'],
            ['POS_MONTHS_BALANCE_MEAN', 'POS_CASH_balance', '-', 'Mean months in POS balance history'],
            ['POS_COMPLETED_RATIO', 'POS_CASH_balance', '-', 'Fraction of POS contracts marked completed'],
        ], [4.5*cm, 3.5*cm, 2*cm, 6.5*cm]),
        sp(6),
        h2('Composite / Engineered Cross-Table Features'),
        tbl([
            ['Feature', 'Formula', 'Rationale'],
            ['BEHAVIORAL_RISK_SCORE', '0.4*INST_LATE_RATIO + 0.3*CC_DPD_RATIO + 0.2*POS_IS_DPD_RATIO + 0.1*BUREAU_OVERDUE_RATIO', 'Weighted delinquency composite across all payment domains'],
            ['EXT_SOURCE_MEAN', '(EXT_SOURCE_1 + EXT_SOURCE_2 + EXT_SOURCE_3) / 3', 'Average external bureau signal — rank-1 SHAP globally'],
            ['INCOME_PER_PERSON', 'AMT_INCOME_TOTAL / max(CNT_FAM_MEMBERS, 1)', 'Per-capita income proxy accounting for household size'],
            ['PAYMENT_RATE', 'AMT_ANNUITY / AMT_CREDIT', 'Fraction of credit paid annually — repayment velocity'],
        ], [4*cm, 7*cm, 5.5*cm]),
        p('Remaining features to reach 140 total: additional one-hot encoded categoricals from application_train (NAME_CONTRACT_TYPE, WEEKDAY_APPR_PROCESS_START, ORGANIZATION_TYPE with 55 categories, etc.), binary flags (FLAG_DOCUMENT_*), and raw numeric fields not listed above. All 140 passed to LightGBM which handles missing values natively in histogram-based split-finding.'),
        pb()
    ]

# ── Section 14c: Model Card (Inline) ─────────────────────────────────────────
def sec14c():
    return [
        h1('14c. Model Card (Inline Summary)'),
        tbl([
            ['Field', 'Value'],
            ['Model name', 'PulseGuard Champion — LightGBM_monotonic v2 (GP2)'],
            ['Version', 'Gold Pass 2 — frozen 2026-06-18'],
            ['Model type', 'Gradient Boosted Trees (LightGBM) with 15 monotone constraints'],
            ['Calibration', 'Isotonic regression, val-only fit, served as numpy interp arrays'],
            ['Training data', 'Home Credit Default Risk — 184,506 applicants (60% train split, seed=42)'],
            ['Validation data', 'Home Credit Default Risk — 61,502 applicants (20% val split)'],
            ['Test data', 'Home Credit Default Risk — 61,503 applicants (20% test split, evaluated once)'],
            ['Target variable', 'TARGET (1=default within loan term, 0=repaid) — 8.07% positive rate'],
            ['Features', '140 features from 7 relational tables; all imputation fit on train only'],
            ['Intended use', 'Portfolio demonstration of credit-risk model governance methodology'],
            ['Out-of-scope use', 'Production lending decisions, regulatory submissions, live underwriting'],
            ['Test AUC', '0.7769'],
            ['Test PR-AUC', '0.2628'],
            ['Test KS', '0.4141'],
            ['Test Brier', '0.0668'],
            ['Test ECE', '0.0019 served isotonic / 0.0034 Platt (frozen report)'],
            ['Composite score', '0.7312 (9-component)'],
            ['Governance audit', 'GOLD — 89.3% (134/150) on 15-dimension audit'],
            ['SR 26-2 alignment', 'Designed to demonstrate SR 26-2 principles; NOT certified by regulatory body'],
            ['Fairness status', 'Proxy audit only — no protected-class labels; NOT fairness-certified'],
            ['Reject inference', 'NOT addressed — model trained on approved applicants only (MNAR bias)'],
            ['Temporal validation', 'NOT possible — Home Credit dataset has no application timestamps'],
            ['Deployment status', 'NOT deployed — champion pkl incompatible with Python 3.9 deployment environment'],
            ['Champion selected', '2026-06-18, by 9-component composite score'],
            ['Model frozen', '2026-06-18 — no retuning, no champion changes permitted after Gold checkpoint'],
        ], [5*cm, 11.5*cm]),
        pb()
    ]

# ── Section 15: Failure Modes ─────────────────────────────────────────────────
def sec15():
    return [
        h1('15. Failure Modes & Mitigations'),
        tbl([
            ['#', 'Failure', 'Detection', 'Gap'],
            ['1', 'Target leakage', '10/10 GP1 leakage audit — safe_to_tune=true', 'No automated re-audit if features change'],
            ['2', 'Test-set leakage', 'Test evaluated exactly once, after all decisions locked', 'Manual discipline required'],
            ['3', 'Post-outcome variables', 'GP1 temporal checks on side-tables', 'Future additions require re-audit'],
            ['4', 'Temporal overclaim', 'FEASIBILITY_LIMITED documented; no OOT claim made', 'True vintage requires timestamped data'],
            ['5', 'AUC-only selection', '9-component composite; governance premium for monotone', 'None'],
            ['6', 'Calibration selected on degenerate metric', 'Isotonic val ECE=0.0 is fit-on-itself; justify on test ECE — served isotonic 0.0019 < Platt 0.0034', 'None'],
            ['7', 'SHAP instability', '30-bootstrap stability check; top-5 features 30/30', 'Full-corpus SHAP would be stronger'],
            ['8', 'Near-threshold instability', 'AMBER_CONFLICT local case computed at PD=0.347', 'Fine-grained boundary stability unmeasured'],
            ['9', 'Fairness overclaim', 'SKELETON label; proxy analysis only; forbidden claims documented', 'No protected-class labels'],
            ['10', 'Cost matrix overclaim', 'SCENARIO_ASSUMPTIONS label; interview answer prepared', 'Requires real LGD/NIM data'],
            ['11', 'Drift hidden by random split', 'val-vs-test PSI=0.0002 is correct; train PSI explained', 'No true temporal drift test possible'],
            ['12', 'RAG wrong policy retrieval', 'Abstain threshold BM25<0.25; OOD case abstains correctly', 'Small corpus may have weak coverage'],
            ['13', 'LLM makes credit decision', 'Hard rule: LLM never approves/rejects in any demo case', 'Ongoing prompt discipline in production'],
            ['14', 'Adverse-action legal overclaim', 'ASSISTIVE_ONLY + HUMAN_REVIEW_REQUIRED on all outputs', 'Licensed officer must review'],
            ['15', 'Public-data-to-production overclaim', 'PORTFOLIO PROJECT stated throughout; model card explicit', 'MNAR bias unaddressed'],
        ], [0.8*cm, 4.5*cm, 5*cm, 5.5*cm]),
        pb()
    ]

# ── Section 16: Claim Boundary ────────────────────────────────────────────────
def sec16():
    return [
        h1('16. Claim Boundary'),
        h2('Locked Safe Claims'),
        b('Tuned LightGBM_monotonic, isotonic-calibrated (served): AUC=0.7769, PR-AUC=0.2628, KS=0.4141, test ECE=0.0019 / 0.0034 Platt (frozen report) on 61k held-out test'),
        b('Validation-only Optuna HPO; champion selected by 9-component composite score'),
        b('Monotone constraints on 15 features support SR 26-2 directional interpretability'),
        b('EXT_SOURCE_MEAN rank-1 SHAP driver in 30/30 bootstraps; top-5 features stable 30/30'),
        b('Score-band policy: GREEN<0.20 (89.7%, DR=5.8%), AMBER 0.20-0.40 (9.8%, DR=27%), RED>=0.40 (0.5%, DR=54%)'),
        b('RAG/LLM: abstains on OOD (BM25<0.25); LLM never makes credit decisions in any of 6 demo cases'),
        b('Fairness proxy: approval-rate differentials aligned with DR differentials; no amplification'),
        b('val-vs-test PSI=0.0002; all top-10 feature PSIs STABLE'),
        b('PulseGuard scores GOLD at 89.3% (134/150) on 15-dimension governance audit'),
        b('Committed app.py serves the GP2 LightGBM champion via native .txt booster + numpy isotonic (no sklearn lock); an earlier Cloud Run revision served a G4 XGBoost demo (AUC=0.6261, synthetic) — verify the live revision and redeploy if needed'),
        sp(6),
        h2('Locked Forbidden Claims'),
        b('Production lending system or live deployment'),
        b('SR 26-2 certified or regulatory compliance certified'),
        b('Legally compliant adverse action notice'),
        b('Fairness certified or disparate impact compliant'),
        b('Real bank data or real lender economics'),
        b('Full vintage/out-of-time validation'),
        b('LLM makes or influences credit decisions'),
        b('100 Optuna trials completed — actual: 4-8 per model'),
        b('CatBoost is the final champion — champion is LightGBM_monotonic'),
        b('AUC=0.7716 is the tuned result — that is the BASELINE untuned CatBoost score'),
        b('Do not quote a live-endpoint AUC without checking the deployed revision — committed app.py serves the champion (native booster + numpy isotonic); an older revision served the G4 demo at 0.6261'),
        sp(6),
        h2('Resume-Safe Wording'),
        p('"Built end-to-end credit-risk ML pipeline on Home Credit Default Risk (307k applicants, 57.4M rows); champion LightGBM (isotonic-calibrated) achieves AUC=0.7769, KS=0.41, test ECE=0.0019 (served; 0.0034 Platt in frozen report) — selected via 9-component composite score including monotone constraints, calibration, and adverse-reason readiness."'),
        pb()
    ]

# ── Section 17: Interview Q&A ─────────────────────────────────────────────────
def sec17():
    items = [
        h1('17. Interview Q&A Master Deck'),
        h2('Standard Questions'),
    ]
    qas = [
        ('Q1 — 60-second opener: "Tell me about PulseGuard in one minute."',
         'PulseGuard is my credit-risk governance portfolio project built on the Home Credit Default Risk dataset — 307,000 applicants, 57 million rows across 7 relational tables. I engineered 140 features, ran a 12-model baseline tournament, then tuned 5 models with Optuna. The champion is LightGBM with monotone constraints, calibrated with isotonic regression (served) — AUC=0.77, test ECE ~0.002 on a 61,000-row holdout. I then added the governance layer: score-band policy, SHAP reason codes with bootstrap stability, a fairness proxy audit, a drift baseline, and a local RAG policy assistant that drafts adverse-action memos for credit officer review. Every claim is traceable to an evidence artifact. Not a production system — a demonstration of the full governed ML lifecycle.'),
        ('Q2 — 2-minute walkthrough: "Walk me through the project."',
         'I will cover it in four stages: data, model, governance, and boundaries. DATA: Home Credit Default Risk — 307,000 applicants at 8% default rate, across 7 tables including bureau history, instalment payments, credit cards, and POS cash records. I engineered 140 features: ratio features like credit-to-annuity and loan-to-goods-value, behavioural aggregates like late-payment ratio and bureau overdue ratio, and a composite behavioural risk score. 10-check leakage audit before any model training — test set never touched until final evaluation. MODEL: 12-model baseline tournament. LightGBM was underperforming due to an early-stopping bug on imbalanced data. Fixed and ran Optuna HPO on 5 models. Champion: LightGBM with monotone constraints, selected by a 9-component composite score. Isotonic calibration produces test ECE ~0.002 (Platt variant 0.003 in the frozen report). Final test AUC: 0.7769. GOVERNANCE: Three-zone score-band policy (GREEN/AMBER/RED), SHAP reason codes stable across 30 bootstrap resamples, fairness proxy audit on age/income/employment/region, PSI drift baseline, and a local BM25 policy RAG with an LLM that drafts adverse-action memos — ASSISTIVE_ONLY. BOUNDARIES: Portfolio project, not production. Limitations documented: no temporal validation, MNAR selection bias, proxy fairness only, 4-8 Optuna trials. Every claim in my resume has an artifact.'),
        ('Q3 — "Why LightGBM_monotonic and not CatBoost?"',
         'CatBoost val AUC=0.7708 vs LightGBM_mono=0.7734 — only a 0.0026 AUC gap. But the composite score is 0.6802 for CatBoost vs 0.7312 for LightGBM_mono. The composite includes a 10% explainability weight: LightGBM_mono gets a full score for SHAP + monotone constraints; CatBoost only gets partial credit. And a 5% weight for adverse-reason readiness — monotone constraints make every prediction auditable without SHAP. More importantly: LightGBM_mono is both the performance champion AND the governance champion. There is no trade-off to defend. That is a better story than "we traded 0.002 AUC for governance compliance."'),
        ('Q4 — "Why monotone constraints?"',
         'Monotone constraints enforce directional interpretability at every tree split. If BUREAU_OVERDUE_RATIO has a +1 constraint, then for any two applicants identical in all other features, the one with the higher overdue ratio will always receive a higher predicted default probability — guaranteed by the model\'s construction. This matters for SR 26-2 model risk management. An auditor can verify the directional claim by inspection without needing a SHAP explanation. A credit officer can explain the model\'s logic to a regulator without showing a SHAP waterfall chart. The cost is some flexibility in tree splits. In practice, LightGBM_mono AUC=0.7734 vs LightGBM_base AUC=0.7724 — the monotone version is actually slightly better on AUC, probably because the constraints act as useful regularisation on the 140-feature space.'),
        ('Q5 — "How did you avoid leakage?"',
         'Three layers. First, TARGET excluded from features — confirmed by 10/10 pre-tuning leakage audit. Second, the calibrator was fit on validation set only — not on train, not on test. Third, the test set was used exactly once, after champion was locked, calibration complete, and score-band thresholds defined. The audit also verified: no applicant ID overlap between splits, no post-outcome proxy variables in the side-tables. The test set was never consulted during Optuna HPO — all optimisation was on the validation set.'),
        ('Q6 — "What is the early stopping bug?"',
         'With eval_metric="auc" and early_stopping_rounds=50 on scale_pos_weight=11.39 imbalanced data, the first tree dominates the AUC improvement. Subsequent trees add only marginal gain. If those gains fall below the default tolerance, training halts at 1-9 trees. The model looks like it ran normally but is severely undertrained. Result: LightGBM G9A AUC=0.7203 — looked plausible, was wrong. I accepted it as BASELINE_NOT_TUNED at Gold Pass 1 without diagnosing the root cause. Gold Pass 2 fix: remove early stopping; treat n_estimators as Optuna search parameter (range 200-1000). After fix, LightGBM_mono reaches AUC=0.7734 and becomes the champion. This bug pattern appears in any imbalanced problem with high scale_pos_weight — production fraud models at 0.1% positive rate have this risk at scale_pos_weight=999.'),
        ('Q7 — "How did tuning work?"',
         'Optuna Tree-structured Parzen Estimator — a Bayesian search that models which hyperparameter configurations produce good validation AUC and proposes new configurations accordingly. I searched over n_estimators, learning rate, num_leaves, max_depth, subsample, colsample_bytree, and regularisation parameters. All tuning optimised on validation AUC — test set never consulted. Trial counts: 4-8 per model, not 100. CPU-only sandbox with 44-second bash execution limit. I am honest about that: the tuning plan specified 100 trials; actual counts are documented in gold_pass2_tuning_trace.json. On GPU with 100 trials I would likely get 0.001-0.003 further AUC improvement.'),
        ('Q8 — "What is ECE?"',
         'Expected Calibration Error. It measures how well predicted probabilities match observed default rates. A calibrated model with PD=0.20 should produce ~20% defaults in that bucket. ECE is computed by binning predictions into 10 buckets, averaging the absolute difference between mean predicted PD and observed DR, weighted by bucket size. Served isotonic ECE=0.0019 on test (frozen GP2 report scored Platt at 0.0034). Raw uncalibrated LightGBM ECE=0.296. Calibration reduces ECE by ~99%. ECE=0.0034 means the model\'s predicted probabilities are extremely close to observed outcomes — reliable, well-calibrated probabilities.'),
        ('Q9 — "What is KS and why does it matter for credit?"',
         'KS (Kolmogorov-Smirnov) is the maximum separation between the cumulative distribution functions of predicted scores for defaulters and non-defaulters. KS=0.4141 means there is a 41.4 percentage-point gap between the two CDFs at the point of maximum separation. It is a useful single-number discriminative measure that does not depend on a specific threshold. For credit scoring, KS>0.40 is conventionally considered strong. KS is widely used in credit risk because lenders care about performance at a specific operating point; AUC is better for comparing models across all thresholds.'),
        ('Q10 — "Why PR-AUC matters at 8% default rate?"',
         'ROC-AUC rewards true negatives heavily at 8% DR — 11.4 non-defaulters per defaulter. A model mediocre at finding defaulters can still score well on ROC. PR-AUC focuses on precision and recall for the minority class. A random classifier at 8% DR has PR-AUC ~= 0.08 (the base rate). Champion PR-AUC=0.2628 is 3.3x the random baseline. PR-AUC is the honest measure of how well the model actually identifies defaulters.'),
        ('Q11 — "How did you create reason codes?"',
         'Using LightGBM\'s built-in pred_contrib=True parameter — the LightGBM implementation of SHAP TreeExplainer values. For each prediction, it returns the marginal contribution of each feature to the log-odds of default. I rank by absolute value and map the top drivers to human-readable language. EXT_SOURCE_MEAN contribution of +0.94 for an AMBER applicant maps to "External credit bureau composite score below threshold." INST_LATE_RATIO contribution of +0.45 maps to "High proportion of late instalment payments." I used LightGBM\'s built-in implementation rather than the external SHAP library because the external library had a pandas index compatibility issue with our non-default-indexed DataFrames. The native implementation is equivalent for tree models and avoids the dependency.'),
        ('Q12 — "Are they legally compliant adverse action notices?"',
         'No. ECOA and Regulation B require adverse action notices with specific reason codes drawn from an approved list, reviewed by a licensed credit officer. Our SHAP-derived language is a draft aid — it helps a credit officer identify the right reason codes faster. The output is always tagged ASSISTIVE_ONLY and HUMAN_REVIEW_REQUIRED. A credit officer must review, confirm, and sign off on any adverse action notice sent to an applicant. This boundary is documented in the model card, the governance report, the claim boundary document, and the RAG/LLM system\'s hard rules.'),
        ('Q13 — "What are the biggest limitations?"',
         'Five material ones. First, reject inference: model trained on approved applicants only — MNAR selection bias; declined population performance is unknown. Second, no temporal holdout: no timestamps in Home Credit; val and test are from the same distribution. Third, single geography: Eastern European portfolio — generalisation to other markets is untested. Fourth, CPU trial count: 4-8 Optuna trials instead of 100; reasonable local optimum, not globally optimal. Fifth, fairness: proxy audit only — protected-class labels unavailable. None of these are hidden — all documented in the model card.'),
        ('Q14 — "How did you audit fairness?"',
         'I ran a proxy audit — the maximum achievable without protected-class labels. Home Credit does not contain race, sex, or national origin fields. I used age bands, income terciles, employment status proxy, and regional rating as approximate proxies. For each group I computed approval rate at the GREEN band threshold (PD<0.20) and compared to the observed default rate for that group. Finding: all approval-rate differences are directionally aligned with default-rate differences. The model appears to differentiate risk, not discriminate by demographics. Explicitly labelled a governance skeleton, not a fairness certification.'),
        ('Q15 — "I tested your live endpoint. AUC is 0.62. What is going on?"',
         'Correct, and documented. The live endpoint at Cloud Run demonstrates the serving architecture: preprocessing pipeline, isotonic-calibrated probability, SHAP top-3 reason codes, score banding, and the ASSISTIVE_ONLY response structure. An earlier revision served the G4 demo model — XGBoost on 50,000 synthetic rows, 28 features, AUC=0.6261. That pkl version lock only affected an abandoned serving path; committed app.py serves the champion via the native .txt booster + numpy isotonic — no sklearn at serve time. If the live revision still returns 0.6261 it is the older G4-demo revision pending redeploy. The serving pattern is what the endpoint demonstrates. For champion quality, the evidence artifacts in outputs/evidence/ have every metric traceable to a specific gate.'),
        ('Q16 — "How would you monitor drift in production?"',
         'Monthly PSI on the score distribution and top-10 input features. PSI<0.10 is STABLE; 0.10-0.25 is SLIGHT_SHIFT (model owner review, 30-day SLA); >0.25 is SIGNIFICANT_SHIFT (MRC escalation, 5 business days). Additionally: if monthly KS drops more than 0.05 from the deployment baseline (0.4141), that triggers emergency model review regardless of PSI. Approve-zone observed DR: WARN at 2x baseline (10%), ALERT at 25%, CRITICAL at 35%. And the score distribution itself — if mean score shifts by more than 0.05, flag for investigation.'),
        ('Q17 — "What would production require?"',
         'Eight things at minimum: independent model validation team review (SR 26-2); out-of-time validation on recent vintages; real bank economics for the cost matrix (real LGD, NIM, regulatory capital); fairness audit with real demographic labels and legal review; reject inference correction for the approved-applicant selection bias; FastAPI serving with training-serving parity check (version-pinned sklearn/Dockerfile); monthly PSI monitoring with automated WARN/ALERT/CRITICAL escalation; credit officer workflow integration for adverse-action notice review and sign-off.'),
        ('Q18 — "What would you improve next?"',
         'Top three in order of impact. First, GPU with 100 Optuna trials — expect 0.001-0.003 AUC improvement and more robust champion. Second, temporal validation if I can find a timestamped public credit dataset — HMDA has application dates and would allow true out-of-time testing; that is the single biggest methodological gap. Third, a stronger fairness audit with demographic enrichment — finding or acquiring protected-class labels for Home Credit or a comparable dataset is the highest-governance-value next step.'),
        ('Q19 — "What does the LLM do exactly?"',
         'The LLM governance assistant has three functions: policy retrieval, memo drafting, and adverse-action language suggestion. It takes an anonymised case summary, retrieves the relevant policy section using BM25, and drafts a memo for the credit officer to review. The BM25 abstain threshold (0.25) prevents the LLM from generating output when no relevant policy is found — the out-of-domain query in Case 5 produces zero output, not a hallucinated policy citation. The LLM never generates a credit decision. In all six demo cases, every output is either a memo, a checklist, or a reason-code draft — all labelled ASSISTIVE_ONLY.'),
        ('Q20 — "How would you explain PulseGuard to a non-technical hiring manager?"',
         'The model estimates how likely each loan applicant is to default. Applicants are sorted into three buckets: Green for low risk, Amber for medium risk, and Red for high risk. Green applicants can be approved quickly — very low estimated default rate. Amber applicants go to a credit officer for manual review. Red applicants need extra scrutiny or are declined. When we decline an applicant or send them to review, the system drafts the top reasons — for example, "high proportion of late payments in prior credit history" — for the credit officer to review and confirm. The officer makes the final decision; the model helps them work faster and more consistently.'),
    ]
    for q, a in qas:
        items.extend(qa(q, a))
    items.append(pb())
    return items

# ── Section 18: Adversarial Follow-Ups ───────────────────────────────────────
def sec18():
    items = [
        h1('18. Adversarial Follow-Up Drill'),
        h2('Second-Punch Questions'),
    ]
    qas = [
        ('Q — "You mentioned 57.4M rows. That is the raw input, right?"',
         'Correct. Each side table is aggregated to applicant level via GROUP BY SK_ID_CURR — bureau_balance from 27M monthly records down to a handful of ratios per applicant. The final modeling matrix is 307,511 rows x 140 features. 57.4M is the raw data volume processed during feature engineering, not the size of what goes into the model.'),
        ('Q — "What did you do with nulls?"',
         'Median imputation for numerics, mode for categoricals, all fit on train only and applied to val and test. Explicit missingness indicator flags added for features where missingness is a signal — OWN_CAR_AGE is null when the applicant owns no car, which is informative. LightGBM handles missing values natively in splitting decisions, so imputation is belt-and-suspenders.'),
        ('Q — "Why not k-fold cross-validation?"',
         'Three reasons. Calibration discipline: Platt/isotonic calibration must be fit on a fixed held-out set; k-fold complicates this. Test isolation: with k-fold every sample eventually appears in a validation fold. Sample size: at 307K rows, variance on a single 20% val split is already low — k-fold adds computational cost without meaningfully reducing estimator variance.'),
        ('Q — "Why TPE over random search?"',
         'Random search samples uniformly with no memory of prior results. TPE builds a probabilistic model after each trial — it fits two density models over configurations that produced good/bad val AUC, proposes configurations where the good-to-bad ratio is highest. After even 3-4 trials, TPE starts exploiting productive regions. With a budget of 4-8 trials, sample efficiency matters.'),
        ('Q — "val-vs-test PSI is 0.0002. Is that too good? Does something seem wrong?"',
         'No — it is expected. Val and test are from the same stratified random split of the same dataset, drawn from the same distribution at the same point in time. PSI close to zero is the correct result when there is no temporal shift. The interesting PSI question would be comparing a new vintage to training — impossible here without timestamps. If val-vs-test PSI were high, that would suggest a bug in the split, not a real drift signal.'),
        ('Q — "Are SHAP reason codes legally compliant adverse action notices?"',
         'No. ECOA and Regulation B require adverse action notices with specific reason codes drawn from an approved list, reviewed by a licensed credit officer. SHAP-derived language is a draft aid — it helps a credit officer identify the right reason codes faster. Output is always tagged ASSISTIVE_ONLY and HUMAN_REVIEW_REQUIRED. A credit officer must review, confirm, and sign off before any applicant communication.'),
        ('Q — "Why not C=1 in LogisticRegression for Platt?"',
         'C is inverse regularisation in sklearn. C=1e6 means effectively zero regularisation — the sigmoid finds the best slope and intercept on the validation scores without penalty. We want the calibrator to fit the calibration data as closely as possible; the only guard against overfitting is the held-out test set evaluation (ECE_test=0.0034 confirms the Platt calibrator generalises; the served isotonic calibrator reaches 0.0019).'),
        ('Q — "What is the difference between Brier score and ECE?"',
         'Brier score is mean squared error of probability predictions — mean((p_i - y_i)^2) — a proper scoring rule penalising both miscalibration and poor discrimination. ECE is calibration-specific: bins predictions, computes the gap between mean predicted probability and observed DR per bin, averages across bins. A model can have low Brier but high ECE (good discrimination, bad calibration) or vice versa. We report both: Brier=0.0668 measures overall probabilistic accuracy; served isotonic ECE=0.0019 confirms the probabilities are reliable.'),
    ]
    for q, a in qas:
        items.extend(qa(q, a))
    items.append(pb())
    return items

# ── Section 19: Core ML Concepts ──────────────────────────────────────────────
def sec19():
    items = [
        h1('19. Core ML Concept Drill'),
    ]
    qas = [
        ('Q — "How does LightGBM differ from XGBoost architecturally?"',
         'Two main differences. Tree growth: LightGBM uses leaf-wise (best-first) growth — splits the leaf producing the largest loss reduction regardless of depth. XGBoost uses level-wise growth — completes all splits at depth d before going to d+1. Leaf-wise converges faster but can overfit on small datasets. Split-finding: LightGBM uses histogram-based binning (256 bins), finding splits on bin boundaries. XGBoost exact split-finding evaluates every unique value. LightGBM also has GOSS (downsamples low-gradient instances) and EFB (bundles sparse features). Core gradient boosting math is the same.'),
        ('Q — "What does scale_pos_weight do mathematically?"',
         'scale_pos_weight multiplies the gradient and hessian of every positive-class (minority) sample by that factor before summing across the node. At scale_pos_weight=11.39 the model treats each defaulter as if it were 11.39 samples, making misclassifying a defaulter 11.39x more costly during training. It does not change the output probabilities directly — it changes what the trees optimise. Calibration is still needed afterwards.'),
        ('Q — "What is a proper scoring rule? Is AUC one?"',
         'A proper scoring rule is minimised by reporting the true conditional probability — it incentivises honest probability estimates. Brier score and log-loss are proper. AUC is NOT: you can maximise AUC with any monotone transformation of the true probabilities. AUC measures ranking accuracy, not calibration. This is why we do not select champion by AUC alone — a model with AUC=0.78 and ECE=0.29 is less useful than AUC=0.77 and ECE=0.003 for threshold-based policy decisions.'),
        ('Q — "What is the bias-variance tradeoff in your specific context?"',
         'With 140 features and 184K training rows, variance (overfitting) is the dominant risk. Train AUC=0.8526 vs val AUC=0.7734 — a 0.08 gap — is the variance signature. Managed with: monotone constraints (reduce effective complexity), Optuna searching over lambda/alpha/min_child_samples/subsample, and not over-tuning (4-8 trials produces a stable local optimum).'),
        ('Q — "What is the difference between monotone constraints and feature selection?"',
         'Feature selection removes features from the model entirely. Monotone constraints keep a feature but restrict the direction of its effect. A +1 constraint on BUREAU_OVERDUE_RATIO means the model can use that feature for any split, but only splits where higher overdue ratio increases predicted default probability are permitted. The model can capture non-linearities and interactions in the constrained direction — just cannot produce a split where higher overdue ratio leads to lower risk, which would be economically nonsensical.'),
    ]
    for q, a in qas:
        items.extend(qa(q, a))
    items.append(pb())
    return items

# ── Section 20: Implementation Probes ────────────────────────────────────────
def sec20():
    items = [
        h1('20. Implementation Probes ("Did You Write This?")'),
    ]
    qas = [
        ('Q — "What shape is the pred_contrib output for LightGBM?"',
         'Shape (n_samples, n_features + 1). The last column is the bias term — the model base score (log-odds of the training prior). To get feature-level SHAP contributions, slice [:,:-1]. The sum of all columns including bias equals the raw log-odds prediction for that sample. Verify: booster.predict(X, raw_score=True) should equal contrib.sum(axis=1) for all samples.'),
        ('Q — "What was the exact root cause of the pandas index error in SHAP?"',
         'y_val was a pandas Series with original Home Credit row labels — integers like 289233, 95708, 302524 — because sliced from the full DataFrame without resetting the index. green_idx was a numpy array of 0-based positional integers from np.where. When you do y_val[green_idx], pandas interprets it as label-based lookup — it looks for rows labelled 0, 1, 2, 3. Those labels do not exist in a Series indexed at 289233. Fix: y_val.values converts to a plain numpy array; positional indexing works correctly.'),
        ('Q — "What is the exact PSI formula you implemented?"',
         'Ten equal-frequency bins computed from the reference distribution using np.percentile(ref, np.linspace(0, 100, 11)). Bin edges nudged (bins[0] -= 1e-9, bins[-1] += 1e-9) to ensure boundary values fall inside. np.histogram(ref, bins) and np.histogram(curr, bins) give counts; divide by n for proportions. Epsilon smoothing: replace any proportion below 1e-9 with 1e-9 to avoid log(0). PSI = sum over bins of (curr_pct - ref_pct) x log(curr_pct / ref_pct).'),
        ('Q — "Walk me through what happens when Optuna runs a trial."',
         'Optuna TPE sampler proposes a hyperparameter configuration. The objective function receives it, builds the model with those parameters, trains on the training set, evaluates on the validation set, returns the val AUC. Optuna logs the (hyperparams, val_AUC) pair. After ~5 trials, TPE fits two KDE models — over configurations that produced top-25% vs bottom val AUC — and proposes the next configuration by maximising the good-to-bad density ratio. study.best_params gives the best trial hyperparams. Direction is "maximize" since we optimise val AUC.'),
        ('Q — "If you called booster.predict(X, pred_contrib=True) on a 2-class problem with 50 features, what are the dimensions?"',
         '(n_samples, 51) — 50 feature contribution columns plus 1 bias column. For binary classification LightGBM returns a single output column per sample, not two — it is the log-odds of the positive class.'),
    ]
    for q, a in qas:
        items.extend(qa(q, a))
    items.append(pb())
    return items

# ── Section 21: Behavioral Questions ─────────────────────────────────────────
def sec21():
    items = [
        h1('21. Behavioral / STAR Questions'),
    ]
    qas = [
        ('Q — "Tell me about a bug you hit and how you diagnosed it."',
         'The SHAP pandas index error is the best example. The symptom was a KeyError on integer indices — looks like a simple off-by-one but was a dtype mismatch. Three different approaches across separate sessions: list conversion, .iloc, explicit numpy casting. None fixed it because I was treating the symptom, not the cause. Diagnosis came from printing the actual index of y_val: index[:5] = [289233, 95708, 302524]. That is not a 0-based index — it is original Home Credit applicant IDs. green_idx contained 0-based positional integers. Pandas label lookup for label 1 in a Series indexed at 289233: not found. Fix was one line: y_val.values. Lesson: when debugging pandas indexing errors, print .index first.'),
        ('Q — "What is the most governance-conscious decision you made?"',
         'Selecting the champion by composite score rather than AUC alone. After tuning, LightGBM_monotonic val AUC=0.7734 and CatBoost=0.7708 — a gap of 0.0026. On AUC alone, barely a real difference. The composite includes calibration, KS, PR-AUC, and a governance premium for monotone constraints. By building the composite before running tuning, I committed to the selection criteria upfront — could not retroactively choose whatever metric made the preferred model win. That is the same discipline a real model risk committee expects.'),
        ('Q — "What is the hardest limitation to defend?"',
         'Reject inference. The model was trained on approved applicants only — Home Credit never observed outcomes for declined applicants. If the previous lending policy systematically declined a particular demographic, the model inherits that bias. There is no clean fix on this dataset. Semi-supervised reject inference methods exist but require strong assumptions about the declined population. I documented it as a material limitation in the model card. In any model trained on bank data, reject inference is a real problem that cannot be handwaved.'),
        ('Q — "Tell me about a design decision you would change."',
         'Using the external SHAP library at all for tree models. The library is valuable for model-agnostic explanations or visualisation tools. For LightGBM, pred_contrib is the native equivalent — same values, no dependency overhead. I planned to use the SHAP library because it is the standard portfolio recommendation, not because it added anything LightGBM could not do natively. Had I read the LightGBM pred_contrib documentation first, I would have used it from the start and avoided the index bug entirely.'),
    ]
    for q, a in qas:
        items.extend(qa(q, a))
    items.append(pb())
    return items

# ── Section 22: Role Expansion ────────────────────────────────────────────────
def sec22():
    return [
        h1('22. Role Expansion: Fraud / MLOps / Risk Scoring'),
        h2('27A — Fraud Detection Roles'),
        p('<b>The bridge:</b> PulseGuard solves imbalanced binary classification — 8.07% positive rate, scale_pos_weight=11.39, gradient boosting, Platt calibration, SHAP reason codes. Fraud detection is the same problem class at lower positive rate (0.1-5%). Methods are identical. Feature domain and regulatory vocabulary differ.'),
        tbl([
            ['Question', 'Fraud-context answer'],
            ['"Have you worked on fraud detection?"', 'Not directly — PulseGuard is credit default. Problem class is identical: rare positive label, gradient boosting, calibration, SHAP, PSI drift monitoring. Methodology maps 1:1; would be applying it to transaction/application fraud features rather than bureau aggregates.'],
            ['"How would you handle class imbalance in fraud?"', 'Same approach: scale_pos_weight. At 8% default rate I used 11.39. For 0.5% fraud rate: ~199. Platt/isotonic calibration afterwards to recover well-calibrated probabilities.'],
            ['"How would drift monitoring apply to fraud?"', 'PSI on score distribution plus top-k feature PSIs. Fraud pattern drift is faster — fraud rings adapt. Tighten PSI WARN threshold (0.05 instead of 0.10) and add velocity-feature PSI checks.'],
        ], [5*cm, 11.5*cm]),
        sp(6),
        h2('27B — MLOps / ML Platform Roles'),
        p('<b>The bridge:</b> PulseGuard is a manually-implemented version of what an MLOps platform automates. Champion selection criteria = what Model Registry encodes. Evidence ledger = what MLflow experiment tracking stores. PSI/KS drift policy = what a monitoring dashboard surfaces.'),
        tbl([
            ['Question', 'MLOps-context answer'],
            ['"Walk me through model lifecycle experience."', 'End to end: data audit -> leakage-checked feature engineering -> baseline tournament -> validation-only Optuna HPO -> calibration -> 9-component composite champion selection -> score-band policy -> SHAP explainability -> PSI drift baseline -> model card + evidence ledger. Full governed lifecycle, implemented manually.'],
            ['"Have you used MLflow?"', 'Not MLflow specifically — PulseGuard evidence ledger is the manual equivalent. Every experiment result logged to JSON artifact with champion selection documented. Know exactly what MLflow would store because I have been doing it by hand.'],
            ['"What is a champion/challenger framework?"', 'Deploy a champion in production, route a fraction of traffic to a challenger. If challenger meets promotion criteria — higher composite score, statistically significant AUC improvement (DeLong test), no calibration regression — promote it. PulseGuard has the 9-component composite; the A/B routing is a future build.'],
        ], [5*cm, 11.5*cm]),
        sp(6),
        h2('27C — Risk Scoring / Decision Science Roles'),
        b('Score-band thresholds set at PD=0.20 and PD=0.40 — interpretable meaning; business stakeholder can reason about "20% chance of default" without understanding the model'),
        b('Cost-sensitive decisioning: documented scenario analysis under C_bad=10, C_reject=1. Framework ready for real bank economics; inputs are scenario assumptions.'),
        b('Champion selection by composite score is decision science discipline: define criteria before running the experiment, not after'),
        sp(6),
        h2('27D — Live Endpoint Deployment Caveat'),
        tbl([
            ['Dimension', 'Live Endpoint', 'PulseGuard Champion'],
            ['Model', 'G4 XGBoost + Platt', 'GP2 LightGBM_monotonic + Isotonic'],
            ['Training data', 'synthetic_home_credit_like', 'Home Credit Default Risk'],
            ['Rows', '50,000', '307,511'],
            ['Features', '28', '140'],
            ['Test AUC', '0.6261', '0.7769'],
            ['Deployment status', 'LIVE at Cloud Run', 'NOT deployed (sklearn version incompatibility)'],
        ], [4*cm, 6*cm, 6.5*cm]),
        p('<b>Root cause:</b> GP2 pkl artifacts serialized with scikit-learn 1.7.2 (requires Python 3.10+). Deployment machine runs Python 3.9, which maxes out at sklearn 1.6.1. Cross-version pkl deserialization is not supported.'),
        p('<b>Fix if more time:</b> Pin sklearn version at training time to match deployment. Or use ONNX export to decouple model artifact from sklearn version entirely.'),
        pb()
    ]

# ── Section 23: Failures ──────────────────────────────────────────────────────
def sec23():
    return [
        h1('23. Failures I\'m Proud Of'),
        tbl([
            ['Failure', 'Root Cause', 'Fix', 'Senior Behavior Demonstrated'],
            ['DGP default rate overshoot (26% vs 8% target)', 'Logistic intercept too shallow (-2.8 instead of -4.2)', 'Binary search on intercept; N=200k for stability; 8 iterations', 'Verify data distributions before modeling'],
            ['LightGBM early stopping bug (AUC=0.7203)', 'early_stopping_rounds fires at iteration 1 with scale_pos_weight=11.39', 'Remove early stopping; treat n_estimators as Optuna parameter', 'Audit surprising baselines before accepting them'],
            ['SHAP pandas index bug (3 sessions)', 'y_val had non-sequential Home Credit IDs as index; green_idx had 0-based integers', 'y_val.values — one line', 'Debug root causes, not symptoms; print .index first'],
            ['Python 3.9 union type annotation crash', 'ColumnTransformer | None uses PEP 604 syntax (3.10+ only)', 'from __future__ import annotations (PEP 563)', 'Environment parity; know the Python version matrix'],
            ['sklearn pkl version lock-out', 'Serialized with sklearn 1.7.2; deployed on Python 3.9/sklearn 1.6.1', 'Retrained G4 demo model on Python 3.9; documented serving gap fully', 'Training/serving parity; version-pin artifacts'],
            ['joblib vs pickle deserialization mismatch', 'app.py used pickle.load(); train_champion.py saved with joblib.dump()', 'joblib.load() throughout', 'Match your serializer; read the error traceback carefully'],
        ], [4*cm, 4*cm, 4*cm, 4.5*cm]),
        sp(4),
        p('<b>Portfolio-level discipline:</b> None of these were hidden. Each one is documented in the gate logs, the claim boundary, or the failure archaeology document. A model that looks clean because failures were buried is more dangerous than one where failures are catalogued.'),
        pb()
    ]

# ── Section 24: GP5 LSTM ──────────────────────────────────────────────────────
def sec24():
    return [
        h1('24. Gold Pass 5: LSTM Sequence Encoder Experiment'),
        h2('What Was Built'),
        tbl([
            ['Component', 'Detail'],
            ['Input data', 'installments_payments.csv — 13.6M rows, 339,587 applicants'],
            ['Per-row features', 'days_late, payment_ratio, log_amt_instalment'],
            ['Sequence length', 'Last 50 instalments per applicant, left-padded with zeros'],
            ['Architecture', '1-layer LSTM (input=3, hidden=64) -> Linear(64->32) -> tanh -> 32-dim embedding'],
            ['Training', 'PyTorch, Colab T4 GPU, 15 epochs, BCEWithLogitsLoss(pos_weight=11.4), AdamW(lr=3e-3), gradient clipping (max_norm=1.0)'],
            ['Integration', 'Embeddings appended to 140-feature LightGBM input -> 172 features; same GP2 Optuna hyperparameters with monotone constraints extended with 32 zeros'],
        ], [4*cm, 12.5*cm]),
        sp(6),
        h2('Results'),
        tbl([
            ['Metric', 'GP5 Challenger', 'GP2 Champion', 'Delta'],
            ['Test AUC (calibrated)', '0.7264', '0.7769', '-0.0505'],
            ['Verdict', '-', 'GP2 RETAINED', '-'],
        ], [4*cm, 3.5*cm, 3.5*cm, 3.5*cm]),
        sp(6),
        h2('Why GP5 Did Not Win'),
        b('35% of applicants have zero instalment history — zero-padded sequences encode noise, not signal, for 65,639 of 184,506 training applicants'),
        b('Scalar aggregates (INST_LATE_RATIO, INST_PAY_RATIO) are already in top-7 SHAP features in GP2 — LSTM learned a redundant representation'),
        b('Supervised LSTM on 8.1% imbalanced labels with 50-timestep sequences may not converge to embeddings more informative than handcrafted aggregates'),
        sp(4),
        h2('What GP5 Adds to the Portfolio Story'),
        b('Ability to write PyTorch training loops with imbalance handling, early stopping, and gradient clipping'),
        b('Understanding of sequence preprocessing: padding, feature engineering at the row level'),
        b('Integration of a neural component with a tree ensemble pipeline'),
        b('Honest evaluation: the negative result is documented, not buried'),
        b('Concrete answer to "walk me through a neural component you built"'),
        sp(6),
        h2('Key Q&A'),
        p('<b>Q: "What would you do differently to make the LSTM work?"</b>'),
        p('Three things. First, restrict LSTM features to only the 65% of applicants who have instalment history — separate "no history" indicator for the others rather than zero-padding everyone. Second, try bidirectional LSTM or self-attention over the sequence (100+ payments window). Third, pre-train the encoder on a reconstruction task (autoencoder on payment sequences) before fine-tuning on the default TARGET — supervised training on 8% imbalance may converge to a less informative latent space.', ANS),
        pb()
    ]

# ── Section 25: Calibration Forensics ────────────────────────────────────────
def sec25():
    return [
        h1('25. Calibration Reconciliation: Isotonic Served vs Platt Frozen'),
        h2('What Happened'),
        p('GP2 evaluated both Platt (logistic regression) and isotonic calibration, both fit on validation only. The frozen single-shot test report (gold_pass2_final_untouched_test_report.json) labels its calibrator "Platt" and reports test ECE=0.0034. The model served by app.py, however, uses the isotonic calibrator.'),
        h2('Root Cause'),
        p('An audit recomputed both calibrators on the same 61,503-row held-out test set using the locked champion:'),
        p('Served isotonic: test ECE=0.0019, Brier=0.0668, AUC=0.7764. Platt (frozen report): test ECE=0.0034, Brier=0.0668, AUC=0.7769. Both cut raw ECE (0.295) by ~99%.'),
        p('Isotonic is served because it has the lower test ECE (its AUC is marginally lower, 0.7764, because isotonic flat segments create ranking ties). An earlier draft attributed the choice to a champion_calibrated.pkl cal["selected"] key — that pkl is the unrelated G4 XGBoost demo calibrator; the reproducible basis is the side-by-side recomputation above.'),
        h2('The Fix'),
        p('''iso_x = iso.X_thresholds_   # shape (134,) — raw probability thresholds
iso_y = iso.y_thresholds_   # shape (134,) — calibrated probability values
np.save("iso_x.npy", iso_x)
np.save("iso_y.npy", iso_y)

# At serve time — exact replication, zero sklearn:
calibrated_prob = float(np.interp(raw_prob, iso_x, iso_y))''', CODE),
        p('np.interp implements the same piecewise-linear interpolation that IsotonicRegression.predict() uses. Max difference between the two: 0.0 across all test values. This eliminates sklearn version lock at serve time entirely — calibration runs as a two-array numpy operation.'),
        h2('Interview Answer'),
        p('<b>Q: "Your writeup mentions Platt, but your serving code uses isotonic — which is it?"</b>'),
        p('Both were evaluated; isotonic is what serves. The frozen GP2 single-shot test report scored the Platt variant at ECE=0.0034, and app.py serves the isotonic calibrator. An audit recomputed both on the same held-out test set: served isotonic ECE=0.0019, Platt 0.0034 — isotonic wins on test, so it serves. I extracted the isotonic calibrator as two numpy threshold arrays and replicated it with np.interp, removing the sklearn dependency at serve time. One correction from that audit: an earlier draft claimed a pkl cal["selected"] key proved the choice — that pkl is the unrelated G4 XGBoost demo calibrator, so the evidence is the side-by-side recomputation, not the pkl.', ANS),
        pb()
    ]

# ── Section 25b: Implemented vs Future ───────────────────────────────────────
def sec25b():
    return [
        h1('25b. Implemented vs Future Roadmap'),
        tbl([
            ['Component', 'Status', 'Safe Claim', 'Future Extension'],
            ['Multi-table feature engineering', 'IMPLEMENTED', '"140 features from 7 tables"', 'WOE/IV scorecard secondary model'],
            ['Leakage audit', 'IMPLEMENTED', '"10/10 PASS, safe_to_tune=true"', 'Re-audit after future feature additions'],
            ['12-model baseline tournament', 'IMPLEMENTED', '"12-model tournament, 2 hard-failures documented"', 'Neural baseline with GPU'],
            ['Optuna HPO', 'IMPLEMENTED', '"Validation-only Optuna TPE, 4-8 trials"', '100-trial GPU search'],
            ['Calibration (isotonic served)', 'IMPLEMENTED', '"served test ECE=0.0019; Platt 0.0034 frozen report; numpy serving"', 'Beta calibration; group-specific calibration'],
            ['Composite champion selection', 'IMPLEMENTED', '"9-component composite score"', 'DeLong test significance'],
            ['Score-band policy', 'IMPLEMENTED', '"GREEN/AMBER/RED PD-semantic thresholds"', 'Threshold calibrated to real LGD'],
            ['SHAP reason codes', 'IMPLEMENTED', '"SHAP top-5 stable 30/30"', 'Full 61k-row SHAP computation'],
            ['Fairness proxy audit', 'PARTIALLY VERIFIED', '"Proxy audit; no amplification beyond DR"', 'Full DI analysis with protected-class labels'],
            ['Drift/PSI baseline', 'PARTIALLY VERIFIED', '"val-vs-test PSI=0.0002 STABLE"', 'Monthly monitoring dashboard; OOT validation'],
            ['RAG/LLM demo', 'SIMULATED', '"6-case demo; abstain fires; ASSISTIVE_ONLY"', '50+ doc corpus; live LLM integration'],
            ['GP5 LSTM experiment', 'IMPLEMENTED', '"LSTM challenger AUC=0.7264; GP2 retained"', 'Bidirectional LSTM; pre-trained encoder'],
            ['Champion/challenger monitoring', 'FUTURE', '-', 'Challenger promotion framework with DeLong test'],
            ['Production serving API', 'COMMITTED', '"app.py serves GP2 champion via native booster + numpy isotonic"', 'Verify/redeploy live Cloud Run revision to match committed code'],
            ['Reject inference', 'FUTURE', '-', 'Semi-supervised correction'],
            ['Real temporal validation', 'FUTURE', '-', 'Requires timestamped dataset (HMDA candidate)'],
            ['MLflow / model registry', 'FUTURE', '-', 'Evidence ledger is the manual equivalent'],
            ['Full fairness audit (DI ratio)', 'FUTURE', '-', 'Requires protected-class demographic labels'],
        ], [5*cm, 3.5*cm, 5*cm, 4*cm]),
        pb()
    ]

# ── Section 25c: API Spec ─────────────────────────────────────────────────────
def sec25c():
    return [
        h1('25c. Cloud Run API — Serving Architecture'),
        h2('Endpoint'),
        p('https://pulseguard-api-98058433335.us-central1.run.app (revision 00006-zrm)'),
        p('<b>Committed serving (app.py):</b> GP2 LightGBM champion via native .txt booster + numpy isotonic — no sklearn lock. An earlier Cloud Run revision served a G4 XGBoost demo (AUC=0.6261, synthetic); verify the live revision and redeploy if needed.'),
        h2('Request Format (POST /predict)'),
        p('''{
  "AMT_CREDIT": 450000,
  "AMT_INCOME_TOTAL": 180000,
  "AMT_ANNUITY": 22500,
  "AMT_GOODS_PRICE": 400000,
  "DAYS_BIRTH": -14000,
  "DAYS_EMPLOYED": -2000,
  "EXT_SOURCE_1": 0.65,
  "EXT_SOURCE_2": 0.55,
  "EXT_SOURCE_3": 0.70,
  ... (28 features total)
}''', CODE),
        h2('Response Format'),
        p('''{
  "applicant_id": "demo_001",
  "raw_score": 0.134,
  "calibrated_pd": 0.112,
  "score_band": "GREEN",
  "governance_tag": "ASSISTIVE_ONLY",
  "human_review_required": false,
  "shap_top3": [
    {"feature": "EXT_SOURCE_2", "contribution": -0.41, "direction": "risk_reducing"},
    {"feature": "CREDIT_TO_ANNUITY", "contribution": 0.18, "direction": "risk_increasing"},
    {"feature": "DAYS_EMPLOYED", "contribution": -0.14, "direction": "risk_reducing"}
  ],
  "adverse_reason_draft": null,
  "llm_memo": null,
  "model_version": "G4_XGB_demo_v1",
  "disclaimer": "NOT_FINAL_DECISION. Subject to credit officer review."
}''', CODE),
        h2('Architecture Components'),
        tbl([
            ['Component', 'Implementation', 'Notes'],
            ['Web framework', 'FastAPI + Uvicorn', 'app.py in /src'],
            ['Containerisation', 'Docker (python:3.9-slim base)', 'Dockerfile at repo root'],
            ['Deployment', 'Google Cloud Run (us-central1)', 'Revision 00006-zrm'],
            ['Feature pipeline', 'src/feature_pipeline.py', 'ColumnTransformer; from __future__ import annotations for Python 3.9'],
            ['Calibration', 'iso_x.npy + iso_y.npy; np.interp', 'Zero sklearn dependency at serve time'],
            ['SHAP at serve', 'booster.predict(X, pred_contrib=True)', 'Top-3 by |SHAP| per request'],
            ['Model artifact', 'outputs/models/g4_champion.pkl (joblib)', 'Loaded with joblib.load() — matches joblib.dump() at train time'],
            ['Monitoring', 'Request logs in Cloud Logging', 'No automated PSI/drift; manual review cadence'],
        ], [3.5*cm, 4*cm, 9*cm]),
        sp(4),
        h2('Known Deployment Issues Fixed'),
        tbl([
            ['Issue', 'Root Cause', 'Fix Applied'],
            ['UnpicklingError: STACK_GLOBAL', 'app.py used pickle.load(); train used joblib.dump()', 'Switched to joblib.load() throughout'],
            ['TypeError: unsupported | operand', 'ColumnTransformer | None is Python 3.10+ syntax', 'from __future__ import annotations (PEP 563)'],
            ['Champion pkl unloadable', 'sklearn 1.7.2 pkl incompatible with Python 3.9', 'Retrained G4 demo model on Python 3.9; serving gap documented'],
        ], [4*cm, 6*cm, 6.5*cm]),
        pb()
    ]

# ── Section 25d: Resume Bullets ───────────────────────────────────────────────
def sec25d():
    return [
        h1('25d. Resume Bullets — Ready to Use'),
        h2('Short Bullets (1-line each)'),
        b('Built end-to-end credit-risk governance pipeline (Home Credit, 307k applicants) — LightGBM (isotonic-calibrated) — AUC=0.7769 — test ECE=0.0019 (served) / 0.0034 (Platt, frozen report) on 61k holdout'),
        b('Engineered 140 features across 7 relational tables (bureau, instalment, POS, credit card); composite behavioural risk score; FOIR/LTV/DTI proxies'),
        b('Delivered SR 26-2-aligned governance stack: SHAP reason codes, fairness proxy audit, score-band policy, PSI drift baseline, local RAG/LLM governance assistant'),
        sp(6),
        h2('Strong Bullets (2-3 lines)'),
        p('<b>Credit-risk ML governance stack, Home Credit Default Risk:</b> Engineered 140 features from 7 relational tables (57.4M rows); ran 12-model baseline + Optuna-tuned 5-model tournament; champion LightGBM with monotone constraints achieves AUC=0.7769; test ECE=0.0019 served isotonic (0.0034 Platt in frozen report) on 61k held-out test set; selected by 9-component composite including calibration, explainability, and adverse-reason readiness — not AUC alone.'),
        sp(4),
        p('<b>End-to-end leakage-audited pipeline:</b> Pre-tuning 10-check leakage audit (safe_to_tune=true) ensured TARGET exclusion, val-only calibration, and single test-set evaluation; 60/20/20 stratified split with zero entity overlap; test set evaluated exactly once; all results traceable to outputs/evidence/ artifacts.'),
        sp(4),
        p('<b>SHAP governance layer with bootstrap stability:</b> Computed reason codes via LightGBM pred_contrib for 4 local applicant cases; bootstrapped global feature importance across 30 resamples (500 samples each) — top-5 features appear in all 30 bootstraps; EXT_SOURCE_MEAN rank-1 in 30/30; adverse-action drafts tagged ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED.'),
        sp(4),
        p('<b>Calibration and score-band policy:</b> Isotonic regression calibration (served) reduces ECE from 0.296 (raw) to 0.0019 (test); served as numpy interp arrays — zero sklearn dependency at runtime; GREEN<0.20 (89.7% of test, DR=5.8%), AMBER 0.20-0.40 (9.8%, DR=27%), RED>=0.40 (0.5%, DR=54%).'),
        sp(4),
        p('<b>Imbalanced-data modeling:</b> Handled 8.07% default rate (scale_pos_weight=11.39); diagnosed LightGBM early-stopping bug with scale_pos_weight (fires at iteration=1); fixed by treating n_estimators as Optuna hyperparameter; AUC improved from 0.7203 (baseline, bug present) to 0.7734 (tuned, fix applied).'),
        sp(4),
        p('<b>Local RAG/LLM governance assistant:</b> BM25 policy retriever over 5-document corpus; abstain threshold (BM25<0.25) prevents hallucinated citations; 6-case demo (approve/review/decline/conflict/OOD/drift); LLM drafts ECOA-style adverse-action memos for credit officer review — ASSISTIVE_ONLY, HUMAN_REVIEW_REQUIRED enforced.'),
        sp(4),
        p('<b>GP5 Neural Experiment:</b> Built 1-layer LSTM encoder on 13.6M instalment payment rows (PyTorch, Colab T4 GPU); 32-dim embeddings appended to 140-feature LightGBM; challenger AUC=0.7264 vs baseline 0.7769 (delta=-0.0505); negative result documented — 35% zero-padding and redundant signal are root causes; GP2 champion retained.'),
        sp(6),
        h2('Unsafe Bullets to Avoid'),
        b('"Built production credit scoring model" — not production'),
        b('"Model approved for lending" — not approved'),
        b('"AUC 0.85+ on credit data" — champion is 0.7769'),
        b('"100 Optuna trials completed" — actual: 4-8 per model'),
        b('"Fair model across protected classes" — proxy audit only'),
        b('"CatBoost champion at AUC=0.7716" — wrong champion and wrong metric (that is the untuned baseline CatBoost)'),
        b('Do not assert a live-endpoint AUC without checking the deployed revision — committed app.py serves the champion (native booster + numpy isotonic); an older revision served the G4 demo at 0.6261'),
        pb()
    ]

# ── Section 26: Defense Checklist ────────────────────────────────────────────
def sec26():
    return [
        h1('26. Final Defense Checklist'),
        tbl([
            ['Item', 'Status'],
            ['60-second opener ready (Section 17, Q1)', 'READY'],
            ['2-minute walkthrough ready (Section 17, Q2 extended)', 'READY'],
            ['Every metric memorised: AUC=0.7769, PR-AUC=0.2628, KS=0.4141, Brier=0.0668, ECE=0.0019 (served)/0.0034 (Platt, frozen)', 'MEMORISED'],
            ['Can explain champion selection (composite, not AUC; monotone governance premium)', 'READY'],
            ['Can explain 57.4M rows correctly (raw data volume; aggregated to 307K modelling grain)', 'READY'],
            ['Can explain limitations (reject inference, no temporal, proxy fairness, CPU trial count)', 'READY'],
            ['Can explain why not production (portfolio project; no independent validation)', 'READY'],
            ['Can defend LLM boundary (ASSISTIVE_ONLY; 6 cases; LLM never decides)', 'READY'],
            ['Can defend fairness limits (no protected-class labels; proxy audit only)', 'READY'],
            ['Can answer adversarial follow-ups (k-fold, stratify, PSI=0.0002, SHAP legality)', 'READY'],
            ['Can answer core ML concepts (LightGBM vs XGBoost, TPE, bias-variance, proper scoring rules)', 'READY'],
            ['Can answer implementation probes (pred_contrib shape, index bug, PSI formula)', 'READY'],
            ['Can answer behavioral questions (bug story, design decision, champion selection rationale)', 'READY'],
            ['Can explain GP5 LSTM experiment and why it failed (35% zero-padding, redundant signal)', 'READY'],
            ['Can explain calibration reconciliation (served isotonic 0.0019 vs frozen Platt 0.0034, numpy serving)', 'READY'],
            ['Know forbidden claims and avoid them under pressure', 'CRITICAL'],
        ], [13*cm, 3.5*cm]),
        sp(8),
        h2('Resume-Safe One-Liner'),
        p('"Built end-to-end credit-risk governance pipeline (Home Credit, 307k applicants, 57.4M rows) — LightGBM with monotone constraints + isotonic calibration; AUC=0.7769, test ECE=0.0019 (served) on 61k holdout; selected via 9-component composite score; SHAP reason codes stable 30/30 bootstraps; fairness proxy audit, PSI drift baseline, local RAG/LLM governance assistant (ASSISTIVE_ONLY); GOLD checkpoint at 89.3%."'),
    ]

# ── Main build ────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUT_PATH,
        pagesize=A4,
        leftMargin=1.8*cm,
        rightMargin=1.8*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    story = []
    story += cover()
    story += sec1()
    story += sec2()
    story += sec3()
    story += sec4()
    story += sec5()
    story += sec6()
    story += sec7()
    story += sec8()
    story += sec9()
    story += sec10()
    story += sec11()
    story += sec12()
    story += sec13()
    story += sec14()
    story += sec14b()
    story += sec14c()
    story += sec15()
    story += sec16()
    story += sec17()
    story += sec18()
    story += sec19()
    story += sec20()
    story += sec21()
    story += sec22()
    story += sec23()
    story += sec24()
    story += sec25()
    story += sec25b()
    story += sec25c()
    story += sec25d()
    story += sec26()

    doc.build(story)
    print(f"PDF written to: {OUT_PATH}")

if __name__ == '__main__':
    build()
