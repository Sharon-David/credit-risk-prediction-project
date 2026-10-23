# predict_single.py
import joblib
import pandas as pd
import numpy as np
import os
import sys
import json
import warnings
warnings.filterwarnings("ignore")

model        = joblib.load("models/stacked/stacked_model.pkl")
preprocessor = joblib.load("models/preprocessor.pkl")

# Cost-optimized threshold from notebooks/05_threshold_optimization.ipynb.
# Falls back to 0.5 if the file is missing (e.g. pipeline not yet run).
_THRESHOLD_PATH = os.path.join(os.path.dirname(__file__), "notebooks", "optimal_threshold.txt")
try:
    with open(_THRESHOLD_PATH) as _f:
        OPTIMAL_THRESHOLD = float(_f.read().strip())
except (FileNotFoundError, ValueError):
    OPTIMAL_THRESHOLD = 0.5

# Exact columns the preprocessor was fitted on (from notebook 02)
EXACT_COLUMNS = [
    'NAME_CONTRACT_TYPE','CODE_GENDER','FLAG_OWN_CAR','FLAG_OWN_REALTY',
    'CNT_CHILDREN','AMT_INCOME_TOTAL','AMT_CREDIT','AMT_ANNUITY',
    'AMT_GOODS_PRICE','NAME_TYPE_SUITE','NAME_INCOME_TYPE',
    'NAME_EDUCATION_TYPE','NAME_FAMILY_STATUS','NAME_HOUSING_TYPE',
    'REGION_POPULATION_RELATIVE','DAYS_BIRTH','DAYS_EMPLOYED',
    'DAYS_REGISTRATION','DAYS_ID_PUBLISH','FLAG_MOBIL','FLAG_EMP_PHONE',
    'FLAG_WORK_PHONE','FLAG_CONT_MOBILE','FLAG_PHONE','FLAG_EMAIL',
    'OCCUPATION_TYPE','CNT_FAM_MEMBERS','REGION_RATING_CLIENT',
    'REGION_RATING_CLIENT_W_CITY','WEEKDAY_APPR_PROCESS_START',
    'HOUR_APPR_PROCESS_START','REG_REGION_NOT_LIVE_REGION',
    'REG_REGION_NOT_WORK_REGION','LIVE_REGION_NOT_WORK_REGION',
    'REG_CITY_NOT_LIVE_CITY','REG_CITY_NOT_WORK_CITY',
    'LIVE_CITY_NOT_WORK_CITY','ORGANIZATION_TYPE','EXT_SOURCE_2',
    'EXT_SOURCE_3','YEARS_BEGINEXPLUATATION_AVG','FLOORSMAX_AVG',
    'YEARS_BEGINEXPLUATATION_MODE','FLOORSMAX_MODE',
    'YEARS_BEGINEXPLUATATION_MEDI','FLOORSMAX_MEDI','TOTALAREA_MODE',
    'EMERGENCYSTATE_MODE','OBS_30_CNT_SOCIAL_CIRCLE',
    'DEF_30_CNT_SOCIAL_CIRCLE','OBS_60_CNT_SOCIAL_CIRCLE',
    'DEF_60_CNT_SOCIAL_CIRCLE','DAYS_LAST_PHONE_CHANGE','FLAG_DOCUMENT_2',
    'FLAG_DOCUMENT_3','FLAG_DOCUMENT_4','FLAG_DOCUMENT_5',
    'FLAG_DOCUMENT_6','FLAG_DOCUMENT_7','FLAG_DOCUMENT_8',
    'FLAG_DOCUMENT_9','FLAG_DOCUMENT_10','FLAG_DOCUMENT_11',
    'FLAG_DOCUMENT_12','FLAG_DOCUMENT_13','FLAG_DOCUMENT_14',
    'FLAG_DOCUMENT_15','FLAG_DOCUMENT_16','FLAG_DOCUMENT_17',
    'FLAG_DOCUMENT_18','FLAG_DOCUMENT_19','FLAG_DOCUMENT_20',
    'FLAG_DOCUMENT_21','AMT_REQ_CREDIT_BUREAU_HOUR',
    'AMT_REQ_CREDIT_BUREAU_DAY','AMT_REQ_CREDIT_BUREAU_WEEK',
    'AMT_REQ_CREDIT_BUREAU_MON','AMT_REQ_CREDIT_BUREAU_QRT',
    'AMT_REQ_CREDIT_BUREAU_YEAR','CREDIT_INCOME_RATIO',
    'ANNUITY_INCOME_RATIO','EMPLOYED_AGE_RATIO','CREDIT_DURATION_RATIO',
    # new engineered features added in improved notebook 02
    'GOODS_CREDIT_RATIO','AGE_YEARS','YEARS_EMPLOYED',
    'INCOME_PER_PERSON','DOC_COUNT',
]

DEFAULTS = {
    'NAME_CONTRACT_TYPE':'Cash loans','CODE_GENDER':'F',
    'FLAG_OWN_CAR':0,'FLAG_OWN_REALTY':1,'CNT_CHILDREN':0,
    'AMT_INCOME_TOTAL':180000.0,'AMT_CREDIT':500000.0,
    'AMT_ANNUITY':25000.0,'AMT_GOODS_PRICE':450000.0,
    'NAME_TYPE_SUITE':'Unaccompanied','NAME_INCOME_TYPE':'Working',
    'NAME_EDUCATION_TYPE':'Secondary / secondary special',
    'NAME_FAMILY_STATUS':'Married','NAME_HOUSING_TYPE':'House / apartment',
    'REGION_POPULATION_RELATIVE':0.02,'DAYS_BIRTH':-15000.0,
    'DAYS_EMPLOYED':-1000.0,'DAYS_REGISTRATION':-3000.0,
    'DAYS_ID_PUBLISH':-2000.0,'FLAG_MOBIL':1,'FLAG_EMP_PHONE':1,
    'FLAG_WORK_PHONE':0,'FLAG_CONT_MOBILE':1,'FLAG_PHONE':0,
    'FLAG_EMAIL':0,'OCCUPATION_TYPE':'Laborers','CNT_FAM_MEMBERS':2.0,
    'REGION_RATING_CLIENT':2,'REGION_RATING_CLIENT_W_CITY':2,
    'WEEKDAY_APPR_PROCESS_START':'TUESDAY','HOUR_APPR_PROCESS_START':10,
    'REG_REGION_NOT_LIVE_REGION':0,'REG_REGION_NOT_WORK_REGION':0,
    'LIVE_REGION_NOT_WORK_REGION':0,'REG_CITY_NOT_LIVE_CITY':0,
    'REG_CITY_NOT_WORK_CITY':0,'LIVE_CITY_NOT_WORK_CITY':0,
    'ORGANIZATION_TYPE':'Business Entity Type 3',
    'EXT_SOURCE_2':0.5,'EXT_SOURCE_3':0.5,
    'YEARS_BEGINEXPLUATATION_AVG':0.98,'FLOORSMAX_AVG':0.1,
    'YEARS_BEGINEXPLUATATION_MODE':0.98,'FLOORSMAX_MODE':0.1,
    'YEARS_BEGINEXPLUATATION_MEDI':0.98,'FLOORSMAX_MEDI':0.1,
    'TOTALAREA_MODE':0.05,'EMERGENCYSTATE_MODE':'No',
    'OBS_30_CNT_SOCIAL_CIRCLE':1.0,'DEF_30_CNT_SOCIAL_CIRCLE':0.0,
    'OBS_60_CNT_SOCIAL_CIRCLE':1.0,'DEF_60_CNT_SOCIAL_CIRCLE':0.0,
    'DAYS_LAST_PHONE_CHANGE':-300.0,
    'FLAG_DOCUMENT_2':0,'FLAG_DOCUMENT_3':1,'FLAG_DOCUMENT_4':0,
    'FLAG_DOCUMENT_5':0,'FLAG_DOCUMENT_6':0,'FLAG_DOCUMENT_7':0,
    'FLAG_DOCUMENT_8':0,'FLAG_DOCUMENT_9':0,'FLAG_DOCUMENT_10':0,
    'FLAG_DOCUMENT_11':0,'FLAG_DOCUMENT_12':0,'FLAG_DOCUMENT_13':0,
    'FLAG_DOCUMENT_14':0,'FLAG_DOCUMENT_15':0,'FLAG_DOCUMENT_16':0,
    'FLAG_DOCUMENT_17':0,'FLAG_DOCUMENT_18':0,'FLAG_DOCUMENT_19':0,
    'FLAG_DOCUMENT_20':0,'FLAG_DOCUMENT_21':0,
    'AMT_REQ_CREDIT_BUREAU_HOUR':0.0,'AMT_REQ_CREDIT_BUREAU_DAY':0.0,
    'AMT_REQ_CREDIT_BUREAU_WEEK':0.0,'AMT_REQ_CREDIT_BUREAU_MON':0.0,
    'AMT_REQ_CREDIT_BUREAU_QRT':0.0,'AMT_REQ_CREDIT_BUREAU_YEAR':1.0,
    'CREDIT_INCOME_RATIO':2.5,'ANNUITY_INCOME_RATIO':0.125,
    'EMPLOYED_AGE_RATIO':0.067,'CREDIT_DURATION_RATIO':20.0,
    'GOODS_CREDIT_RATIO':0.9,'AGE_YEARS':41.0,'YEARS_EMPLOYED':2.7,
    'INCOME_PER_PERSON':90000.0,'DOC_COUNT':1.0,
}


def predict(inputs: dict):
    try:
        data = DEFAULTS.copy()
        data.update(inputs)

        # Recompute all engineered features
        credit   = data['AMT_CREDIT']
        income   = data['AMT_INCOME_TOTAL']
        annuity  = data['AMT_ANNUITY']
        days_emp = data['DAYS_EMPLOYED']
        days_age = data['DAYS_BIRTH']
        fam      = max(data['CNT_FAM_MEMBERS'], 1)
        goods    = data['AMT_GOODS_PRICE']

        data['CREDIT_INCOME_RATIO']   = credit / income if income else 0
        data['ANNUITY_INCOME_RATIO']  = annuity / income if income else 0
        data['CREDIT_DURATION_RATIO'] = credit / annuity if annuity else 0
        data['EMPLOYED_AGE_RATIO']    = days_emp / days_age if days_age else 0
        data['GOODS_CREDIT_RATIO']    = goods / credit if credit else 0
        data['AGE_YEARS']             = round(-days_age / 365, 1)
        data['YEARS_EMPLOYED']        = round(-days_emp / 365, 1)
        data['INCOME_PER_PERSON']     = income / fam

        # Use exactly the columns (and order) the loaded preprocessor was fitted on,
        # so a retrained preprocessor with a different column set still works
        df = pd.DataFrame([data])[list(preprocessor.feature_names_in_)]

        df_processed = preprocessor.transform(df)
        prob = model.predict_proba(df_processed)[0][1]

        # Risk tiers, anchored on the cost-optimized threshold from notebook 05
        if prob >= OPTIMAL_THRESHOLD:
            decision = "Reject (High Risk)"
            tier = "high"
        elif prob >= OPTIMAL_THRESHOLD * 0.5:
            decision = "Review (Medium Risk)"
            tier = "medium"
        else:
            decision = "Approve (Low Risk)"
            tier = "low"

        return {"probability": float(prob), "decision": decision, "tier": tier}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            inputs = json.loads(sys.argv[1])
        except:
            # Legacy 3-arg mode
            inputs = {
                'AMT_CREDIT': float(sys.argv[1]),
                'AMT_INCOME_TOTAL': float(sys.argv[2]),
                'DAYS_EMPLOYED': float(sys.argv[3]),
            }
        result = predict(inputs)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": "Missing arguments"}))