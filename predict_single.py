# predict_single.py
import joblib
import pandas as pd
import sys
import json
import numpy as np

# Load model and preprocessor
model = joblib.load("models/stacked/stacked_model.pkl")
preprocessor = joblib.load("models/preprocessor.pkl")

# To match your actual folder structure:
model = joblib.load("../models/stacked/stacked_model.pkl")
preprocessor = joblib.load("../models/preprocessor.pkl")

def get_default_row():
    """Return a dict with all expected columns set to sensible defaults."""
    return {
        # Core financials
        'AMT_CREDIT': 500000.0,
        'AMT_INCOME_TOTAL': 200000.0,
        'AMT_ANNUITY': 25000.0,
        'AMT_GOODS_PRICE': 450000.0,

        # Employment / time features
        'DAYS_EMPLOYED': -1000.0,
        'DAYS_BIRTH': -15000.0,
        'DAYS_REGISTRATION': -3000.0,
        'DAYS_ID_PUBLISH': -2000.0,
        'DAYS_LAST_PHONE_CHANGE': -300.0,

        # Engineered ratios
        'CREDIT_INCOME_RATIO': 2.5,
        'ANNUITY_INCOME_RATIO': 0.125,
        'CREDIT_DURATION_RATIO': 20.0,
        'EMPLOYED_AGE_RATIO': 0.25,

        # External scores
        'EXT_SOURCE_2': 0.5,
        'EXT_SOURCE_3': 0.5,

        # Region / rating
        'REGION_RATING_CLIENT': 2,
        'REGION_RATING_CLIENT_W_CITY': 2,
        'REGION_POPULATION_RELATIVE': 0.02,
        'REG_REGION_NOT_LIVE_REGION': 0,
        'REG_REGION_NOT_WORK_REGION': 0,
        'REG_CITY_NOT_LIVE_CITY': 0,
        'REG_CITY_NOT_WORK_CITY': 0,
        'LIVE_REGION_NOT_WORK_REGION': 0,
        'LIVE_CITY_NOT_WORK_CITY': 0,

        # Social circle
        'OBS_30_CNT_SOCIAL_CIRCLE': 1.0,
        'DEF_30_CNT_SOCIAL_CIRCLE': 0.0,
        'OBS_60_CNT_SOCIAL_CIRCLE': 1.0,
        'DEF_60_CNT_SOCIAL_CIRCLE': 0.0,

        # Credit bureau enquiries
        'AMT_REQ_CREDIT_BUREAU_HOUR': 0.0,
        'AMT_REQ_CREDIT_BUREAU_DAY': 0.0,
        'AMT_REQ_CREDIT_BUREAU_WEEK': 0.0,
        'AMT_REQ_CREDIT_BUREAU_MON': 0.0,
        'AMT_REQ_CREDIT_BUREAU_QRT': 0.0,
        'AMT_REQ_CREDIT_BUREAU_YEAR': 1.0,

        # Building / apartment
        'FLOORSMAX_AVG': 0.1,
        'FLOORSMAX_MODE': 0.1,
        'FLOORSMAX_MEDI': 0.1,
        'YEARS_BEGINEXPLUATATION_AVG': 0.98,
        'YEARS_BEGINEXPLUATATION_MODE': 0.98,
        'YEARS_BEGINEXPLUATATION_MEDI': 0.98,
        'TOTALAREA_MODE': 0.05,

        # Flags – numeric
        'FLAG_OWN_CAR': 0,
        'FLAG_OWN_REALTY': 1,
        'CNT_CHILDREN': 0,
        'CNT_FAM_MEMBERS': 2.0,
        'FLAG_MOBIL': 1,
        'FLAG_EMP_PHONE': 1,
        'FLAG_WORK_PHONE': 0,
        'FLAG_CONT_MOBILE': 1,
        'FLAG_PHONE': 0,
        'FLAG_EMAIL': 0,
        'HOUR_APPR_PROCESS_START': 10,

        # Document flags
        'FLAG_DOCUMENT_2': 0, 'FLAG_DOCUMENT_3': 1, 'FLAG_DOCUMENT_4': 0,
        'FLAG_DOCUMENT_5': 0, 'FLAG_DOCUMENT_6': 0, 'FLAG_DOCUMENT_7': 0,
        'FLAG_DOCUMENT_8': 0, 'FLAG_DOCUMENT_9': 0, 'FLAG_DOCUMENT_10': 0,
        'FLAG_DOCUMENT_11': 0, 'FLAG_DOCUMENT_12': 0, 'FLAG_DOCUMENT_13': 0,
        'FLAG_DOCUMENT_14': 0, 'FLAG_DOCUMENT_15': 0, 'FLAG_DOCUMENT_16': 0,
        'FLAG_DOCUMENT_17': 0, 'FLAG_DOCUMENT_18': 0, 'FLAG_DOCUMENT_19': 0,
        'FLAG_DOCUMENT_20': 0, 'FLAG_DOCUMENT_21': 0,

        # Categorical columns (use most common / mode values)
        'NAME_CONTRACT_TYPE': 'Cash loans',
        'CODE_GENDER': 'F',
        'NAME_TYPE_SUITE': 'Unaccompanied',
        'NAME_INCOME_TYPE': 'Working',
        'NAME_EDUCATION_TYPE': 'Secondary / secondary special',
        'NAME_FAMILY_STATUS': 'Married',
        'NAME_HOUSING_TYPE': 'House / apartment',
        'OCCUPATION_TYPE': 'Laborers',
        'WEEKDAY_APPR_PROCESS_START': 'TUESDAY',
        'ORGANIZATION_TYPE': 'Business Entity Type 3',
        'EMERGENCYSTATE_MODE': 'No',
    }


def predict(credit_amount: float, income_total: float, days_employed: float):
    try:
        data = get_default_row()

        # Override with user-provided values
        data['AMT_CREDIT'] = credit_amount
        data['AMT_INCOME_TOTAL'] = income_total
        data['DAYS_EMPLOYED'] = days_employed

        # Recompute derived ratios from user inputs
        if income_total > 0:
            data['CREDIT_INCOME_RATIO'] = credit_amount / income_total
            data['ANNUITY_INCOME_RATIO'] = data['AMT_ANNUITY'] / income_total
        if data['AMT_ANNUITY'] > 0:
            data['CREDIT_DURATION_RATIO'] = credit_amount / data['AMT_ANNUITY']
        age_days = abs(data['DAYS_BIRTH'])
        emp_days = abs(days_employed)
        if age_days > 0:
            data['EMPLOYED_AGE_RATIO'] = emp_days / age_days

        df = pd.DataFrame([data])

        # Transform with preprocessor
        df_processed = preprocessor.transform(df)

        # Predict
        prob = model.predict_proba(df_processed)[0][1]
        decision = "Reject (High Risk)" if prob >= 0.49 else "Approve (Low Risk)"

        return {
            "probability": float(prob),
            "decision": decision
        }
    except Exception as e:
        return {"error": str(e)}


# Command-line / backend entrypoint
if __name__ == "__main__":
    if len(sys.argv) == 4:
        credit = float(sys.argv[1])
        income = float(sys.argv[2])
        days = float(sys.argv[3])
        result = predict(credit, income, days)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": "Missing arguments"}))