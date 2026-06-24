#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PG_ROOT="$ROOT"
OUT="$ROOT/outputs/data"
mkdir -p "$OUT"
LOG="$OUT/fe_runner.log"
exec > "$LOG" 2>&1

python3 << 'PY'
import pandas as pd, numpy as np, pickle, time, os, json, warnings
warnings.filterwarnings("ignore")

HC  = os.path.join(os.environ["PG_ROOT"], "data", "home-credit-default-risk")
OUT = os.path.join(os.environ["PG_ROOT"], "outputs", "data")
OUT_EV = os.path.join(os.environ["PG_ROOT"], "outputs", "evidence")
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT_EV, exist_ok=True)
t_global = time.time()
feature_log = {}

# Step A: bureau_balance
print(f"[{time.time()-t_global:.0f}s] bureau_balance...", flush=True)
bb = pd.read_csv(f"{HC}/bureau_balance.csv")
bb['STATUS_PAST_DUE'] = bb['STATUS'].isin(['1','2','3','4','5']).astype(int)
bb_agg = bb.groupby('SK_ID_BUREAU').agg(
    BB_MONTHS_COUNT=('MONTHS_BALANCE','count'),
    BB_MONTHS_PAST_DUE=('STATUS_PAST_DUE','sum'),
    BB_DPD_RATIO=('STATUS_PAST_DUE','mean'),
).reset_index()
del bb
bb_agg.to_parquet(f"{OUT}/bb_agg.parquet", index=False)
print(f"[{time.time()-t_global:.0f}s] bb_agg done {bb_agg.shape}", flush=True)

# Step B: bureau
print(f"[{time.time()-t_global:.0f}s] bureau...", flush=True)
bur = pd.read_csv(f"{HC}/bureau.csv")
bur = bur.merge(bb_agg, on='SK_ID_BUREAU', how='left'); del bb_agg
bur['BUREAU_ACTIVE']  = (bur['CREDIT_ACTIVE']=='Active').astype(int)
bur['BUREAU_CLOSED']  = (bur['CREDIT_ACTIVE']=='Closed').astype(int)
bur['BUREAU_OVERDUE'] = (bur['CREDIT_DAY_OVERDUE']>0).astype(int)
bur['BUREAU_CC']      = (bur['CREDIT_TYPE']=='Credit card').astype(int)
bur_agg = bur.groupby('SK_ID_CURR').agg(
    BUREAU_COUNT=('SK_ID_BUREAU','count'),
    BUREAU_ACTIVE_COUNT=('BUREAU_ACTIVE','sum'),
    BUREAU_CLOSED_COUNT=('BUREAU_CLOSED','sum'),
    BUREAU_OVERDUE_COUNT=('BUREAU_OVERDUE','sum'),
    BUREAU_DAYS_CREDIT_MEAN=('DAYS_CREDIT','mean'),
    BUREAU_DAYS_CREDIT_MAX=('DAYS_CREDIT','max'),
    BUREAU_AMT_CREDIT_SUM_MEAN=('AMT_CREDIT_SUM','mean'),
    BUREAU_AMT_CREDIT_SUM_MAX=('AMT_CREDIT_SUM','max'),
    BUREAU_AMT_CREDIT_SUM_DEBT_MEAN=('AMT_CREDIT_SUM_DEBT','mean'),
    BUREAU_AMT_CREDIT_OVERDUE_MEAN=('AMT_CREDIT_SUM_OVERDUE','mean'),
    BUREAU_CC_COUNT=('BUREAU_CC','sum'),
    BUREAU_BB_DPD_RATIO_MEAN=('BB_DPD_RATIO','mean'),
    BUREAU_BB_DPD_RATIO_MAX=('BB_DPD_RATIO','max'),
    BUREAU_BB_MONTHS_COUNT_MEAN=('BB_MONTHS_COUNT','mean'),
    BUREAU_BB_MONTHS_PAST_DUE_SUM=('BB_MONTHS_PAST_DUE','sum'),
).reset_index()
bur_agg['BUREAU_ACTIVE_RATIO']  = bur_agg['BUREAU_ACTIVE_COUNT']/(bur_agg['BUREAU_COUNT']+1)
bur_agg['BUREAU_OVERDUE_RATIO'] = bur_agg['BUREAU_OVERDUE_COUNT']/(bur_agg['BUREAU_COUNT']+1)
bur_agg['BUREAU_DEBT_CREDIT']   = bur_agg['BUREAU_AMT_CREDIT_SUM_DEBT_MEAN']/(bur_agg['BUREAU_AMT_CREDIT_SUM_MEAN']+1)
bur_agg.to_parquet(f"{OUT}/bur_agg.parquet", index=False)
del bur; feature_log['bureau']=len(bur_agg.columns)-1
print(f"[{time.time()-t_global:.0f}s] bur_agg done {bur_agg.shape}", flush=True)

# Step C: previous_application
print(f"[{time.time()-t_global:.0f}s] previous_application...", flush=True)
prev = pd.read_csv(f"{HC}/previous_application.csv")
prev['PREV_APPROVED'] = (prev['NAME_CONTRACT_STATUS']=='Approved').astype(int)
prev['PREV_REFUSED']  = (prev['NAME_CONTRACT_STATUS']=='Refused').astype(int)
prev['CREDIT_RATIO']  = prev['AMT_CREDIT']/(prev['AMT_APPLICATION']+1)
prev['DAYS_FIRST_DRAWING'] = prev['DAYS_FIRST_DRAWING'].replace(365243,np.nan)
prev_agg = prev.groupby('SK_ID_CURR').agg(
    PREV_COUNT=('SK_ID_PREV','count'),
    PREV_APPROVED_COUNT=('PREV_APPROVED','sum'),
    PREV_REFUSED_COUNT=('PREV_REFUSED','sum'),
    PREV_AMT_CREDIT_MEAN=('AMT_CREDIT','mean'),
    PREV_AMT_APPLICATION_MEAN=('AMT_APPLICATION','mean'),
    PREV_CREDIT_RATIO_MEAN=('CREDIT_RATIO','mean'),
    PREV_DAYS_DECISION_MEAN=('DAYS_DECISION','mean'),
    PREV_DAYS_DECISION_MIN=('DAYS_DECISION','min'),
    PREV_CNT_PAYMENT_MEAN=('CNT_PAYMENT','mean'),
    PREV_RATE_DOWN_PAYMENT_MEAN=('RATE_DOWN_PAYMENT','mean'),
).reset_index()
prev_agg['PREV_APPROVAL_RATE'] = prev_agg['PREV_APPROVED_COUNT']/(prev_agg['PREV_COUNT']+1)
prev_agg['PREV_REFUSAL_RATE']  = prev_agg['PREV_REFUSED_COUNT']/(prev_agg['PREV_COUNT']+1)
prev_agg.to_parquet(f"{OUT}/prev_agg.parquet", index=False)
del prev; feature_log['previous_application']=len(prev_agg.columns)-1
print(f"[{time.time()-t_global:.0f}s] prev_agg done {prev_agg.shape}", flush=True)

# Step D: installments
print(f"[{time.time()-t_global:.0f}s] installments...", flush=True)
inst = pd.read_csv(f"{HC}/installments_payments.csv")
inst['PAYMENT_DELAY'] = inst['DAYS_INSTALMENT']-inst['DAYS_ENTRY_PAYMENT']
inst['PAYMENT_RATIO'] = inst['AMT_PAYMENT']/(inst['AMT_INSTALMENT']+1)
inst['IS_LATE']       = (inst['PAYMENT_DELAY']<-1).astype(int)
inst['IS_UNDERPAID']  = (inst['PAYMENT_RATIO']<0.99).astype(int)
inst['SHORTFALL']     = inst['AMT_INSTALMENT']-inst['AMT_PAYMENT']
inst_agg = inst.groupby('SK_ID_CURR').agg(
    INST_COUNT=('NUM_INSTALMENT_NUMBER','count'),
    INST_PAYMENT_DELAY_MEAN=('PAYMENT_DELAY','mean'),
    INST_PAYMENT_DELAY_MAX=('PAYMENT_DELAY','max'),
    INST_PAYMENT_DELAY_STD=('PAYMENT_DELAY','std'),
    INST_PAYMENT_RATIO_MEAN=('PAYMENT_RATIO','mean'),
    INST_PAYMENT_RATIO_MIN=('PAYMENT_RATIO','min'),
    INST_LATE_COUNT=('IS_LATE','sum'),
    INST_LATE_RATIO=('IS_LATE','mean'),
    INST_UNDERPAID_RATIO=('IS_UNDERPAID','mean'),
    INST_SHORTFALL_MEAN=('SHORTFALL','mean'),
).reset_index()
inst_agg.to_parquet(f"{OUT}/inst_agg.parquet", index=False)
del inst; feature_log['installments']=len(inst_agg.columns)-1
print(f"[{time.time()-t_global:.0f}s] inst_agg done {inst_agg.shape}", flush=True)

# Step E: credit card
print(f"[{time.time()-t_global:.0f}s] credit_card...", flush=True)
cc = pd.read_csv(f"{HC}/credit_card_balance.csv")
cc['CC_UTILIZATION'] = cc['AMT_BALANCE']/(cc['AMT_CREDIT_LIMIT_ACTUAL']+1)
cc['CC_IS_DPD']      = (cc['SK_DPD']>0).astype(int)
cc['CC_PAY_RATIO']   = cc['AMT_PAYMENT_CURRENT']/(cc['AMT_INST_MIN_REGULARITY']+1)
cc_agg = cc.groupby('SK_ID_CURR').agg(
    CC_COUNT=('SK_ID_PREV','count'),
    CC_BALANCE_MEAN=('AMT_BALANCE','mean'),
    CC_BALANCE_MAX=('AMT_BALANCE','max'),
    CC_LIMIT_MEAN=('AMT_CREDIT_LIMIT_ACTUAL','mean'),
    CC_UTILIZATION_MEAN=('CC_UTILIZATION','mean'),
    CC_UTILIZATION_MAX=('CC_UTILIZATION','max'),
    CC_DPD_COUNT=('CC_IS_DPD','sum'),
    CC_DPD_RATIO=('CC_IS_DPD','mean'),
    CC_PAY_RATIO_MEAN=('CC_PAY_RATIO','mean'),
    CC_ATM_DRAW_MEAN=('AMT_DRAWINGS_ATM_CURRENT','mean'),
).reset_index()
cc_agg.to_parquet(f"{OUT}/cc_agg.parquet", index=False)
del cc; feature_log['credit_card']=len(cc_agg.columns)-1
print(f"[{time.time()-t_global:.0f}s] cc_agg done {cc_agg.shape}", flush=True)

# Step F: POS cash
print(f"[{time.time()-t_global:.0f}s] POS_CASH...", flush=True)
pos = pd.read_csv(f"{HC}/POS_CASH_balance.csv")
pos['POS_IS_DPD']    = (pos['SK_DPD']>0).astype(int)
pos_agg = pos.groupby('SK_ID_CURR').agg(
    POS_COUNT=('SK_ID_PREV','count'),
    POS_MONTHS_MAX=('MONTHS_BALANCE','max'),
    POS_IS_DPD_SUM=('POS_IS_DPD','sum'),
    POS_IS_DPD_RATIO=('POS_IS_DPD','mean'),
    POS_DPD_MEAN=('SK_DPD','mean'),
    POS_DPD_MAX=('SK_DPD','max'),
    POS_DPD_DEF_MEAN=('SK_DPD_DEF','mean'),
    POS_CNT_INST_MEAN=('CNT_INSTALMENT','mean'),
    POS_CNT_INST_FUTURE_MEAN=('CNT_INSTALMENT_FUTURE','mean'),
).reset_index()
pos_agg.to_parquet(f"{OUT}/pos_agg.parquet", index=False)
del pos; feature_log['pos_cash']=len(pos_agg.columns)-1
print(f"[{time.time()-t_global:.0f}s] pos_agg done {pos_agg.shape}", flush=True)

# Step G: application features + merge
print(f"[{time.time()-t_global:.0f}s] application merge...", flush=True)
app = pd.read_csv(f"{HC}/application_train.csv")
app['FLAG_EMPLOYED_ANOMALY'] = (app['DAYS_EMPLOYED']==365243).astype(int)
app['DAYS_EMPLOYED'] = app['DAYS_EMPLOYED'].replace(365243,np.nan)
app['AGE_YEARS']           = -app['DAYS_BIRTH']/365
app['EMPLOYED_YEARS']      = -app['DAYS_EMPLOYED']/365
app['EMPLOYMENT_RATIO']    = app['EMPLOYED_YEARS']/app['AGE_YEARS']
app['CREDIT_TO_INCOME']    = app['AMT_CREDIT']/(app['AMT_INCOME_TOTAL']+1)
app['ANNUITY_TO_INCOME']   = app['AMT_ANNUITY']/(app['AMT_INCOME_TOTAL']+1)
app['CREDIT_TO_GOODS']     = app['AMT_CREDIT']/(app['AMT_GOODS_PRICE']+1)
app['ANNUITY_TO_CREDIT']   = app['AMT_ANNUITY']/(app['AMT_CREDIT']+1)
app['INCOME_PER_CHILD']    = app['AMT_INCOME_TOTAL']/(app['CNT_CHILDREN']+1)
app['EXT_SOURCE_MEAN']     = app[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']].mean(axis=1)
app['EXT_SOURCE_PRODUCT']  = app[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']].prod(axis=1, skipna=True)
app['EXT_SOURCE_STD']      = app[['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3']].std(axis=1)
for col in ['EXT_SOURCE_1','OWN_CAR_AGE','OCCUPATION_TYPE']:
    app[f'MISS_{col}'] = app[col].isnull().astype(int)
doc_flags = [c for c in app.columns if c.startswith('FLAG_DOCUMENT')]
app['FLAG_DOCUMENT_COUNT'] = app[doc_flags].sum(axis=1)
cat_cols = ['NAME_CONTRACT_TYPE','CODE_GENDER','FLAG_OWN_CAR','FLAG_OWN_REALTY',
            'NAME_INCOME_TYPE','NAME_EDUCATION_TYPE','NAME_FAMILY_STATUS',
            'NAME_HOUSING_TYPE','WEEKDAY_APPR_PROCESS_START']
app = pd.get_dummies(app, columns=cat_cols, drop_first=True, dtype=np.int8)
drop_cols=['NAME_TYPE_SUITE','OCCUPATION_TYPE','ORGANIZATION_TYPE',
           'FONDKAPREMONT_MODE','HOUSETYPE_MODE','WALLSMATERIAL_MODE','EMERGENCYSTATE_MODE']
app.drop(columns=[c for c in drop_cols if c in app.columns], inplace=True)
feature_log['application'] = len([c for c in app.columns if c not in ['TARGET','SK_ID_CURR']])

# merge side tables
for parquet_name, key in [
    ('bur_agg','bureau'),('prev_agg','prev'),('inst_agg','inst'),
    ('cc_agg','cc'),('pos_agg','pos')]:
    agg = pd.read_parquet(f"{OUT}/{parquet_name}.parquet")
    app = app.merge(agg, on='SK_ID_CURR', how='left')
    del agg

print(f"[{time.time()-t_global:.0f}s] merged shape: {app.shape}", flush=True)

# Cross-table features
if 'BUREAU_AMT_CREDIT_SUM_MEAN' in app.columns:
    app['BUREAU_CREDIT_TO_INCOME'] = app['BUREAU_AMT_CREDIT_SUM_MEAN']/(app['AMT_INCOME_TOTAL']+1)
if 'INST_LATE_RATIO' in app.columns and 'CC_DPD_RATIO' in app.columns:
    app['BEHAVIORAL_RISK_SCORE'] = (
        app['INST_LATE_RATIO'].fillna(0)*0.4
        + app['CC_DPD_RATIO'].fillna(0)*0.3
        + app['POS_IS_DPD_RATIO'].fillna(0)*0.2
        + app['BUREAU_OVERDUE_RATIO'].fillna(0)*0.1)

target = app['TARGET'].copy()
sk_id  = app['SK_ID_CURR'].copy()
app.drop(columns=['SK_ID_CURR','TARGET'], inplace=True)
app.fillna(app.median(numeric_only=True), inplace=True)

feature_names = list(app.columns)
feature_log['total_features'] = len(feature_names)
print(f"[{time.time()-t_global:.0f}s] total features: {len(feature_names)}", flush=True)

# Split 60/20/20 stratified
from sklearn.model_selection import train_test_split
X=app.values.astype(np.float32); y=target.values
X_tmp,X_test,y_tmp,y_test = train_test_split(X,y,test_size=0.20,random_state=42,stratify=y)
X_train,X_val,y_train,y_val = train_test_split(X_tmp,y_tmp,test_size=0.25,random_state=42,stratify=y_tmp)
print(f"[{time.time()-t_global:.0f}s] split: train={len(X_train):,} val={len(X_val):,} test={len(X_test):,}  DR_train={y_train.mean()*100:.2f}%", flush=True)

with open(f"{OUT}/g9a_splits.pkl",'wb') as f:
    pickle.dump({'X_train':X_train,'X_val':X_val,'X_test':X_test,
                 'y_train':y_train,'y_val':y_val,'y_test':y_test,
                 'feature_names':feature_names},f,protocol=4)
print(f"[{time.time()-t_global:.0f}s] splits saved", flush=True)

# Save evidence
fr = {"gate":"G9A","feature_matrix_shape":list(app.shape),
      "total_features":len(feature_names),
      "feature_groups":feature_log,
      "split":{"train":int(len(X_train)),"val":int(len(X_val)),"test":int(len(X_test)),
                "strategy":"stratified_random_60_20_20",
                "default_rate_train":round(float(y_train.mean()),4),
                "temporal_note":"No application timestamp available; DAYS_BIRTH/DAYS_REGISTRATION used as recency proxies. True temporal split requires multi-cohort vintage data."},
      "elapsed_total_s":round(time.time()-t_global,1)}
json_path=f"{OUT_EV}/g9a_feature_factory_report.json"
import json
with open(json_path,'w') as f: json.dump(fr,f,indent=2)
print(f"[{time.time()-t_global:.0f}s] COMPLETE. Saved {json_path}", flush=True)

# completion marker
with open(f"{OUT}/FE_COMPLETE","w") as f: f.write("DONE")
PY
