# Thin Lambda behind API Gateway: query params -> SageMaker endpoint -> DynamoDB audit row -> JSON.
# Only needs boto3 (built into the Lambda runtime). Handler name: lambda_function.handler
# (if you paste this into the console's lambda_function.py).
import json
import uuid
import datetime
from decimal import Decimal
import boto3

sm = boto3.client("sagemaker-runtime")
table = boto3.resource("dynamodb").Table("credit-risk-audit")

# Same query-param -> column mapping as predict_api.py
NUM = {
    "credit": "AMT_CREDIT", "income": "AMT_INCOME_TOTAL", "ext2": "EXT_SOURCE_2", "ext3": "EXT_SOURCE_3",
    "annuity": "AMT_ANNUITY", "goods": "AMT_GOODS_PRICE", "children": "CNT_CHILDREN",
    "fam_members": "CNT_FAM_MEMBERS", "own_car": "FLAG_OWN_CAR", "own_realty": "FLAG_OWN_REALTY",
    "bureau_year": "AMT_REQ_CREDIT_BUREAU_YEAR", "def_30": "DEF_30_CNT_SOCIAL_CIRCLE",
    "def_60": "DEF_60_CNT_SOCIAL_CIRCLE",
}
STR = {
    "gender": "CODE_GENDER", "contract_type": "NAME_CONTRACT_TYPE", "income_type": "NAME_INCOME_TYPE",
    "education": "NAME_EDUCATION_TYPE", "occupation": "OCCUPATION_TYPE", "organization": "ORGANIZATION_TYPE",
}

def handler(event, context):
    q = event.get("queryStringParameters") or {}
    inputs = {NUM[k]: float(v) for k, v in q.items() if k in NUM}
    inputs.update({STR[k]: v for k, v in q.items() if k in STR})
    if "days_employed" in q:
        inputs["DAYS_EMPLOYED"] = -abs(float(q["days_employed"]))
    if "age_years" in q:
        inputs["DAYS_BIRTH"] = -(float(q["age_years"]) * 365)

    resp = sm.invoke_endpoint(EndpointName="credit-risk-endpoint",
                              ContentType="application/json", Body=json.dumps(inputs))
    result = json.loads(resp["Body"].read())

    table.put_item(Item={
        "applicant_id": q.get("applicant_id", str(uuid.uuid4())),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "inputs": json.dumps(inputs),
        "probability": Decimal(str(result.get("probability", -1))),
        "tier": result.get("tier", "error"),
        "decision": result.get("decision", result.get("error", "")),
    })

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(result),
    }
