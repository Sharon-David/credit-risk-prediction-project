# AWS Implementation Plan (Bare-Minimum Version)

> **IMPORTANT, READ FIRST:** This is a **bare-minimum, basic, demo-only** implementation.
> **NOT production grade.** No edge-case handling, no tests, no retries, no input validation,
> no VPCs, no custom domains, no CI/CD, no infrastructure-as-code frameworks.
> Every step should be the **smallest amount of code and the fewest AWS console clicks** that
> gets something working end to end. If there's a choice, pick the simplest option.

Target architecture (from the report):
S3 (data lake) → Athena (SQL exploration) → Glue (preprocessing) → SageMaker (training) →
S3 (artifacts) → Lambda + API Gateway (`/predict`) → DynamoDB (audit log) → CloudFront (UI),
orchestrated by Step Functions, secured by IAM, monitored by CloudWatch.

Region: use **one region for everything** (e.g. `us-east-1`).

---

## 0. New files to add (all minimal)

```
aws/
├── glue_preprocess.py        # Glue Python Shell job = notebook 02 logic, condensed
├── sagemaker/                # tiny custom container (Dockerfile + serve.py + requirements.txt) hosting OUR .pkl files
├── deploy_sagemaker.py       # tar the existing .pkl files → S3 → create/update the serverless endpoint
├── lambda_handler.py         # thin Lambda: call SageMaker endpoint + DynamoDB put_item
├── athena_queries.sql        # 3–4 exploration queries
├── step_functions.json       # state machine definition (Glue → SageMaker)
└── README_AWS.md             # optional: console steps checklist
```

> Keep each file **as short as possible**. Copy logic from the notebooks; don't refactor, don't add
> abstractions, don't handle errors beyond what's needed for it to run.

---

## 1. Amazon S3 (data lake + artifact store)

**Basic only: one bucket, a few prefixes.**

Console steps:
1. Create bucket `credit-risk-<yourname>` (defaults are fine; default encryption is already on).
2. Upload `application_train.csv` to `raw/application_train.csv`.

Prefix layout:
```
raw/application_train.csv
processed/            # application_clean.csv (written by Glue)
models/               # preprocessor.pkl, feature_columns.json, stacked/stacked_model.pkl
reports/figures/      # optional PNGs
athena-results/       # Athena query output
ui/                   # credit-risk-demo.html for CloudFront
```

No versioning, lifecycle rules, or replication. **Keep it minimal.**

---

## 2. Amazon Athena (exploration, replaces notebook 01)

**Basic only: one table, a handful of queries.**

1. Athena console → set query result location to `s3://<bucket>/athena-results/`.
2. Create a table over `raw/` with a `CREATE EXTERNAL TABLE` statement. Only declare the columns you
   query (e.g. `TARGET`, `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `DAYS_EMPLOYED`). Use
   `OpenCSVSerde` and `skip.header.line.count=1`.
   - Simplest alternative: run a Glue Crawler once on `raw/` to auto-create the table.
3. Put 3–4 queries in `aws/athena_queries.sql`:
   - row count
   - `TARGET` class counts (imbalance)
   - null count for a couple of columns
   - avg income / credit by `TARGET`

No Parquet conversion, no partitioning. **Bare minimum.**

---

## 3. AWS Glue (preprocessing, replaces notebook 02)

**Basic only: a single Python Shell job, no Spark.**

`aws/glue_preprocess.py` (minimal):
- `boto3`/`pandas` read `raw/application_train.csv` from S3.
- Replace `365243` → NaN, add 2 ratio features, drop columns over 45% missing (pandas only, no scikit-learn).
- Write one cleaned CSV to `processed/` only. **Don't touch `models/`**: the hosted model and preprocessor
  are our existing ones and must not be overwritten.
- It's a talking point for the pipeline; the model was trained offline. No logging, no validation.

Console steps:
1. Upload the script to `s3://<bucket>/scripts/glue_preprocess.py`.
2. Glue → ETL jobs → **Python Shell** job, Python 3.9, 0.0625 DPU (cheapest).
3. Job parameter: `--additional-python-modules scikit-learn,joblib` (pandas is already included).
4. Attach IAM role `GlueRole` (see §9).
5. Run once manually to confirm it works.

---

## 4. Amazon SageMaker (hosting OUR EXISTING model, no ML work)

> **NO training, NO retraining, NO tuning on SageMaker.** The ML part is finished. The model is the
> `stacked_model.pkl` + `preprocessor.pkl` we already trained locally in this repo. SageMaker's only
> job is to **host that exact model** behind an endpoint. Bare minimum.

What to do:
1. Bundle the existing files into one archive and upload it:
   ```
   model.tar.gz
   ├── stacked_model.pkl
   ├── preprocessor.pkl
   └── code/
       ├── inference.py
       ├── predict_single.py    # existing file, reused as-is (only the model load paths change)
       └── requirements.txt     # xgboost, lightgbm
   ```
   → `s3://<bucket>/models/model.tar.gz`
2. `aws/inference.py` (about 10 lines) defines the 4 standard SageMaker hooks:
   - `model_fn`: load the two `.pkl` files from `model_dir`
   - `input_fn`: `json.loads` the request body (the raw applicant dict)
   - `predict_fn`: call the existing `predict()` logic → `{probability, decision, tier}`
   - `output_fn`: `json.dumps`
3. Deploy with a few lines of the `sagemaker` SDK (run once from your laptop or a SageMaker notebook):
   ```python
   SKLearnModel(model_data="s3://<bucket>/models/model.tar.gz", role=SageMakerRole,
                entry_point="inference.py", framework_version="1.2-1"
   ).deploy(endpoint_name="credit-risk-endpoint",
            serverless_inference_config=ServerlessInferenceConfig(memory_size_in_mb=2048))
   ```
   **Serverless endpoint** = pay per request, nothing billed while idle. **Delete it after the demo anyway.**
4. Test it from the notebook with `predictor.predict({...})`.

> **Implementation note (what was actually built):** the model was trained on Python 3.13+, and
> AWS's prebuilt SKLearn container (sklearn 1.2 / Python 3.8) can't unpickle it. So instead of
> `SKLearnModel` + `inference.py`, we use a **tiny custom container** (`aws/sagemaker/`: Dockerfile +
> 15-line Flask `serve.py` that imports the existing `predict_single.py` unchanged), pushed to ECR,
> deployed by `aws/deploy_sagemaker.py` as a **serverless** endpoint. Same idea, guaranteed to load.
> Pin the library versions in `aws/sagemaker/requirements.txt` to the training versions. Don't retrain.
> Step-by-step: `aws/README_AWS.md`.

---

## 5. AWS Lambda (inference + audit write)

**Basic only: one function reusing the existing code.**

Because the model now lives in SageMaker, Lambda is just a **thin glue function**: no ML libraries,
just `boto3` (already built into the Lambda runtime). So it's a **plain zip / paste-in-console
function**: no Docker, no ECR.

`aws/lambda_handler.py` (about 20 lines):
```python
import json, uuid, boto3, datetime
from decimal import Decimal
sm = boto3.client("sagemaker-runtime")
table = boto3.resource("dynamodb").Table("credit-risk-audit")

def handler(event, context):
    inputs = event.get("queryStringParameters") or {}
    # map query params → model column names (same mapping as predict_api.py)
    resp = sm.invoke_endpoint(EndpointName="credit-risk-endpoint",
                              ContentType="application/json", Body=json.dumps(inputs))
    result = json.loads(resp["Body"].read())
    table.put_item(Item={...})          # see §7
    return {"statusCode": 200, "body": json.dumps(result)}
```
- Runtime Python 3.11, memory 256 MB, timeout 30 s (covers the serverless endpoint cold start).
- Role: `LambdaRole` (§9).
- `predict_api.py` (FastAPI) stays in the repo for local runs; on AWS this handler replaces it.
  Mangum isn't needed with this approach (it can still be listed on the tech stack as the local/API layer).

No provisioned concurrency, no layers juggling, no error handling. **Keep it minimal.**

---

## 6. Amazon API Gateway

**Basic only: one HTTP API, one route.**

1. API Gateway → **HTTP API** (cheaper and simpler than REST) → integration = the Lambda.
2. Route `GET /predict` (or `$default` to proxy everything).
3. Enable CORS: allow origin `*` (demo only) and method `GET`.
4. Note the invoke URL and put it in `credit-risk-demo.html` in place of `http://localhost:8000`.

No auth, throttling, usage plans, or custom domain.

---

## 7. Amazon DynamoDB (audit log)

**Basic only: one table, one write per prediction. Nothing else.**

Console steps (about 1 minute):
1. DynamoDB → Create table.
2. Table name `credit-risk-audit`.
3. Partition key `applicant_id` (String), sort key `timestamp` (String).
4. Keep defaults, but pick **On-demand** capacity → Create.

Code: the **one** `put_item` call in the Lambda (§5):
```python
table.put_item(Item={
    "applicant_id": inputs.get("applicant_id", str(uuid.uuid4())),
    "timestamp": datetime.datetime.utcnow().isoformat(),
    "inputs": json.dumps(inputs),
    "probability": Decimal(str(result["probability"])),
    "tier": result["tier"],
    "decision": result["decision"],
})
```
- Floats must be `Decimal` (or strings). DynamoDB rejects Python floats. That's the only gotcha.
- Store `inputs` as a JSON string (simplest; no nested-type mapping).
- To check it works: DynamoDB console → table → **Explore items** → a new row appears after each prediction.
- To show "prediction history" for an applicant: in Explore items, query by `applicant_id`. No extra code.

No GSIs, TTL, streams, backups, global tables, or read API. **Bare minimum.**

---

## 8. AWS Step Functions (orchestration)

> **3-account setup (what was built):** Step Functions lives in Account A with Glue, so the state machine
> only runs the Glue job (Glue → Done / Fail). The SageMaker endpoint check below was dropped because the
> endpoint is in Account B. See `aws/README_AWS.md` for the account split.

**Basic only: two sequential steps.**

`aws/step_functions.json`:
```
Start → Glue StartJobRun (.sync) → SageMaker DescribeEndpoint (check it's InService) → End
```
- Use the built-in integrations (`arn:aws:states:::glue:startJobRun.sync`,
  `arn:aws:aws-sdk:sagemaker:describeEndpoint`).
- No training step. The model is fixed (our existing one), so the pipeline is just: refresh the
  processed data → confirm the hosted model is live.
- "Failure alerts": optionally add one `Catch` → SNS `Publish` to your email. If that's too much,
  skip it and rely on the console's failed-execution view.
- Start it manually from the console. No EventBridge schedule needed.

---

## 9. AWS IAM (security)

**Basic only: ONE shared role + ONE CLI user. No custom JSON policies.**

- Role `CreditRiskRole`, trusted by Glue, SageMaker, Lambda and Step Functions (`aws/iam_trust_policy.json`),
  with AWS-managed policies ticked in the console: `AmazonS3FullAccess`, `AWSGlueServiceRole`,
  `AmazonSageMakerFullAccess`, `AmazonDynamoDBFullAccess`, `AWSLambdaBasicExecutionRole`,
  `AmazonEC2ContainerRegistryReadOnly`.
- User `demo-cli` with `AdministratorAccess` + access keys, only so the laptop can push the Docker image
  and run `deploy_sagemaker.py`. Delete it after the demo.
- Least-privilege per-service roles are what the report describes for production; for the demo one role is enough.

---

## 10. Amazon CloudFront (static UI)

**Basic only: S3 origin, default settings.**

1. Upload `credit-risk-demo.html` (with the API Gateway URL) to `s3://<bucket>/ui/`.
2. CloudFront → create distribution → origin = the bucket, origin path `/ui`,
   **Origin Access Control** (the console creates the bucket policy for you), default root object
   `credit-risk-demo.html`.
3. Open the `https://xxxx.cloudfront.net` URL. Done.

No custom domain, WAF, or cache tuning.

---

## 11. Amazon CloudWatch (monitoring)

**Basic only: use what you get for free.**

- Lambda, Glue, and SageMaker already send logs to CloudWatch Logs automatically. Nothing to code.
- Create **one alarm**: Lambda `Errors` > 0 over 5 min (optionally notify the SNS topic from §8).
- Optional: one dashboard with API Gateway `Latency` (p95/p99) and Lambda `Errors`/`Duration`,
  added from the console.

No custom metrics or prediction-drift monitoring (just mention it in the report).

---

## 12. Order of work (bare-minimum path)

1. S3 bucket + upload CSV.
2. Athena table + queries.
3. Glue job → run → check `processed/` in S3.
4. Package the existing `.pkl` files → `model.tar.gz` → deploy the SageMaker serverless endpoint → test once.
5. DynamoDB table.
6. Lambda (zip, boto3 only) → test from the Lambda console with a sample event → see a row in DynamoDB.
7. API Gateway → hit `/predict?credit=500000&income=180000&days_employed=1000` in a browser.
8. CloudFront + UI → submit the form → see the result, and confirm a new row in DynamoDB.
9. Step Functions → run once end to end.
10. CloudWatch alarm.
11. IAM: just tighten `LambdaRole` and keep the rest as above.

## Explicitly out of scope (do NOT build)

- Unit/integration tests, test cases of any kind
- Input validation, edge-case handling, retries, fallbacks
- IaC (Terraform/CDK/CloudFormation), CI/CD
- VPCs, private subnets, KMS customer keys, WAF, auth/Cognito
- **Any ML work**: retraining, SageMaker training jobs, tuning, new features, model changes
  (we only host the model already in this repo)
- Real-time (always-on) SageMaker endpoints, Model Registry, SageMaker Pipelines
- Model monitoring/drift detection, autoscaling tuning, multi-region

> **Reminder:** the goal is a **basic, minimal, working demo** of each service in the report,
> nothing production grade. Minimal code, minimal console setup.
