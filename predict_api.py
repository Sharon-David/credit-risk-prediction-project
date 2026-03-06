from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess, json, sys

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def serve_html():
    return FileResponse("credit-risk-demo.html")

@app.get("/predict")
def predict(
    credit: float, income: float, days_employed: float,
    age_years: float = 35.0, ext2: float = 0.5, ext3: float = 0.5,
    annuity: float = 25000.0, goods: float = 450000.0,
    children: int = 0, fam_members: float = 2.0,
    own_car: int = 0, own_realty: int = 1,
    gender: str = "F", contract_type: str = "Cash loans",
    income_type: str = "Working", education: str = "Secondary / secondary special",
    occupation: str = "Laborers", organization: str = "Business Entity Type 3",
    bureau_year: float = 1.0, def_30: float = 0.0, def_60: float = 0.0,
):
    try:
        inputs = {
            "AMT_CREDIT": credit,
            "AMT_INCOME_TOTAL": income,
            "DAYS_EMPLOYED": -abs(days_employed),
            "DAYS_BIRTH": -(age_years * 365),
            "EXT_SOURCE_2": ext2,
            "EXT_SOURCE_3": ext3,
            "AMT_ANNUITY": annuity,
            "AMT_GOODS_PRICE": goods,
            "CNT_CHILDREN": children,
            "CNT_FAM_MEMBERS": fam_members,
            "FLAG_OWN_CAR": own_car,
            "FLAG_OWN_REALTY": own_realty,
            "CODE_GENDER": gender,
            "NAME_CONTRACT_TYPE": contract_type,
            "NAME_INCOME_TYPE": income_type,
            "NAME_EDUCATION_TYPE": education,
            "OCCUPATION_TYPE": occupation,
            "ORGANIZATION_TYPE": organization,
            "AMT_REQ_CREDIT_BUREAU_YEAR": bureau_year,
            "DEF_30_CNT_SOCIAL_CIRCLE": def_30,
            "DEF_60_CNT_SOCIAL_CIRCLE": def_60,
        }
        result = subprocess.run(
            [sys.executable, "-W", "ignore", "predict_single.py", json.dumps(inputs)],
            capture_output=True, text=True, timeout=30
        )
        stdout = result.stdout.strip()
        if not stdout:
            return {"error": result.stderr.strip()[:400]}
        return json.loads(stdout)
    except subprocess.TimeoutExpired:
        return {"error": "Prediction timed out"}
    except Exception as e:
        return {"error": str(e)}