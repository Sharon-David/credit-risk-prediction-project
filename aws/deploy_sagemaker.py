# Packages the EXISTING model files, uploads them to S3, and creates/updates a serverless SageMaker endpoint.
# Edit BUCKET below, then run from the repo root:   python aws/deploy_sagemaker.py
import time
import tarfile
import boto3

BUCKET = "credit-risk-model-aranck"   # <-- CHANGE THIS to your bucket name
REGION = "us-east-1"

account = boto3.client("sts").get_caller_identity()["Account"]
image_uri = f"{account}.dkr.ecr.{REGION}.amazonaws.com/credit-risk:latest"
role_arn = f"arn:aws:iam::{account}:role/CreditRiskRole"
endpoint = "credit-risk-endpoint"
name = f"credit-risk-{int(time.time())}"

with tarfile.open("model.tar.gz", "w:gz") as tar:
    tar.add("models/stacked/stacked_model.pkl", arcname="models/stacked/stacked_model.pkl")
    tar.add("models/preprocessor.pkl", arcname="models/preprocessor.pkl")
boto3.client("s3", region_name=REGION).upload_file("model.tar.gz", BUCKET, "models/model.tar.gz")
print(f"Uploaded s3://{BUCKET}/models/model.tar.gz")

sm = boto3.client("sagemaker", region_name=REGION)
sm.create_model(
    ModelName=name,
    ExecutionRoleArn=role_arn,
    PrimaryContainer={"Image": image_uri, "ModelDataUrl": f"s3://{BUCKET}/models/model.tar.gz"},
)
sm.create_endpoint_config(
    EndpointConfigName=name,
    ProductionVariants=[{
        "VariantName": "AllTraffic",
        "ModelName": name,
        "ServerlessConfig": {"MemorySizeInMB": 3072, "MaxConcurrency": 2},
    }],
)
try:
    sm.describe_endpoint(EndpointName=endpoint)
    print(f"Endpoint '{endpoint}' exists, updating...")
    sm.update_endpoint(EndpointName=endpoint, EndpointConfigName=name)
except sm.exceptions.ClientError:
    print(f"Creating new endpoint '{endpoint}'...")
    sm.create_endpoint(EndpointName=endpoint, EndpointConfigName=name)
print(f"Endpoint '{endpoint}' is deploying (takes ~5-10 min). Watch it in SageMaker console -> Inference -> Endpoints.")
