# AWS Setup Guide: 3 Accounts (Beginner-Friendly, Bare Minimum)

> **Read this first.**
> - This is a **demo**, not a production system. The goal is to **show each AWS service working**,
>   not to configure it perfectly. Wherever the console asks you something not mentioned here,
>   **leave the default** and move on.
> - No tests, no edge cases, no fancy settings. Just follow the steps for **your** account, in order.
> - Time: about 45–60 min per account the first time.

---

## Part 0: Overview (everyone reads this)

### 0.1 Who does what

| Account | Owner does | Services | Needs on laptop |
|---|---|---|---|
| **A: Data pipeline** | Sections A1–A6 | IAM, S3, Athena, Glue, Step Functions, CloudWatch | `application_train.csv` only |
| **B: Model serving** | Sections B1–B8 | IAM, S3, ECR, SageMaker, DynamoDB, Lambda, API Gateway, CloudWatch | nothing for the console steps (see below) |
| **C: Website** | Sections C1–C3 | S3, CloudFront, CloudWatch | `credit-risk-demo.html` only |

**About the "Docker laptop" (Account B only):** SageMaker steps B2 + B4b–B4d need **one laptop** with
Docker Desktop, the AWS CLI, Python, and the model files in `models/`. It does **not** have to be the B
person's own laptop. Whoever has a capable laptop and the model files (the friend who trained the model)
can do it using **account B's access keys** (created in B1). The image and endpoint still land in account B.
Everything else in B (and all of A and C) is just clicking in the browser.

### 0.2 How the accounts connect (no special permissions between accounts)
```
Account C (website)  --calls the public URL-->  Account B (API Gateway → Lambda → SageMaker, DynamoDB)
Account A (data pipeline) is independent: S3 → Athena, Glue, Step Functions
```
The **only thing passed between people**: when B finishes section B7, B sends the **API Invoke URL** to C.
- A can start any time.
- B can start any time (once the model files are available).
- C can do C1 any time, but C2 step 1 needs B's URL.

### 0.3 Three rules that prevent 90% of problems
1. **Always use region `US East (N. Virginia)` = `us-east-1`** in all 3 accounts.
   The region dropdown is in the **top-right corner** of every console page. Check it **every time** you open a
   service. If something "disappeared", you're probably in the wrong region. (S3, IAM and CloudFront show
   "Global"; that's normal.)
2. **To open a service:** click the **search bar at the top** of the console, type the name (e.g. `S3`), click it.
3. **Use the exact names in this guide** (`credit-risk-audit`, `credit-risk-endpoint`, `CreditRiskRole`, ...).
   The code expects them. The only names you choose yourself are bucket names.

### 0.4 Bucket names
S3 bucket names must be **globally unique** (across all AWS users), lowercase, no spaces. Each account makes its own:
- Account A: e.g. `credit-risk-data-<yourname>` (called **`<BUCKET_A>`** below)
- Account B: e.g. `credit-risk-model-<yourname>` (called **`<BUCKET_B>`**)
- Account C: e.g. `credit-risk-web-<yourname>` (called **`<BUCKET_C>`**)

### 0.5 Your account number
Click your account name in the **top-right** of the console. The 12-digit **Account ID** is shown there
(copy it with the copy icon). This guide calls it **`<ACCOUNT_ID>`**. Only account B needs it.

### 0.6 Costs + budget alert (everyone, do this FIRST)
These services are **pay-as-you-go**, so they do show up on your bill, but for this demo it's **cents**
(well under $1 per account if you follow the cleanup at the end). Newer AWS accounts also come with free credits,
and several of these services have a free tier.

| Account | What can cost money | Rough cost for this demo |
|---|---|---|
| A | Glue (~$0.44 per DPU-hour, billed per minute), Athena ($5 per TB scanned; our CSV is 0.00016 TB), S3 storage | a few cents |
| B | SageMaker serverless (only while answering requests), ECR image storage (~$0.10/GB-month), Lambda / API Gateway / DynamoDB (free tier covers a demo) | cents; **delete the endpoint + image after** |
| C | S3 + CloudFront (free tier covers a demo) | ~$0 |

**Set a budget alert so you get an email if anything costs money** (2 min, each account owner does it in their own account):
1. Search bar → **Budgets** (it's under **Billing and Cost Management**) → **Create budget**.
2. **Budget setup**: **Use a template (simplified)**.
3. **Templates**: **Zero spend budget** (emails you as soon as spending goes over $0.01).
   (Prefer fewer emails? Pick **Monthly cost budget** instead and type `5` as the amount, so it emails you near $5.)
4. **Email recipients**: your email → **Create budget**.

If the alert email arrives, don't panic: check **Billing and Cost Management** → **Bills** to see which service it is.
A few cents is expected. Just make sure you do the **Cleanup** section at the end of this guide after the demo.

---
---

# ACCOUNT A: Data Pipeline

## A1. IAM role `CreditRiskRole`
1. Open **IAM** → left menu **Roles** → **Create role**.
2. **Trusted entity type**: **Custom trust policy**.
3. Delete everything in the text box, paste the contents of `aws/iam_trust_policy.json` → **Next**.
4. **Add permissions**: search each name and **tick its checkbox** (search, tick, clear the search, search the next):
   - `AmazonS3FullAccess`
   - `AWSGlueServiceRole`
5. **Next** → **Role name**: `CreditRiskRole` → scroll down → **Create role**.

## A2. S3 (data lake)
1. Open **S3** → **Create bucket** → **Bucket name**: `<BUCKET_A>` → leave everything else default → **Create bucket**.
2. Click the bucket → **Create folder** → `raw` → **Create folder**.
3. Open the `raw` folder → **Upload** → **Add files** → `application_train.csv` → **Upload**.
   Wait for the green "Upload succeeded" banner (160 MB) → **Close**.

**Demo talking point:** S3 is the data lake; the raw data and processed outputs live here.

## A3. Athena (SQL on S3)
1. On your laptop, open `aws/athena_queries.sql` and replace `<BUCKET>` in the `LOCATION` line with `<BUCKET_A>`.
2. Open **Athena** → if you see a welcome page, **Launch query editor**.
3. The first time, a banner asks for a query result location → **Edit settings** (or **Settings** tab → **Manage**)
   → enter `s3://<BUCKET_A>/athena-results/` → **Save** → back to the **Editor** tab.
4. Run the statements **one at a time**: copy one statement (from its first word to its `;`) into the editor → **Run**.
   - Statement 1 creates the database. Then pick `credit_risk` in the left panel's **Database** dropdown.
   - Statement 2 creates the table.
   - Statements 3–6 are the 4 exploration queries (marked `-- 1.` to `-- 4.` in the file). The one to show is
     `-- 2. Class imbalance`: about 282,686 rows with target `0` vs 24,825 with target `1` (~92% vs ~8%).

**Demo talking point:** we query a 160 MB CSV with plain SQL straight from S3, without loading it anywhere.

## A4. Glue (preprocessing job)
1. On your laptop, open `aws/glue_preprocess.py` and set line 3: `BUCKET = "<BUCKET_A>"`.
2. Open **AWS Glue** → left menu **ETL jobs** → **Script editor**.
3. **Engine**: **Python shell**. **Options**: **Start fresh** → **Create script**.
4. Delete the sample code and paste **all** of `aws/glue_preprocess.py`.
5. Click the **Job details** tab and set only:
   - **Name**: `credit-risk-preprocess` (exactly this; Step Functions uses it)
   - **IAM Role**: `CreditRiskRole`
   - **Python version**: `Python 3.9`
   - **Data processing units**: `1 DPU` (not 1/16; the small one runs out of memory)
   - **Load common analytics libraries**: **ticked** (gives pandas)
6. **Save** (top right) → **Run**.
7. **Runs** tab: after ~1–3 min the status should be **Succeeded**.
   If **Failed**: click the run → read the **Error message**, or click **Output logs** / **Error logs**.
8. Check S3: `<BUCKET_A>` now has a `processed/` folder with `application_clean.csv`.

**Demo talking point:** Glue runs the data cleaning (sentinel fix, ratio features, dropping mostly-empty columns)
as a serverless ETL job. The model itself was trained offline (see the notebooks) and is hosted in account B.

## A5. Step Functions (orchestration)
1. Open **Step Functions** → **Create state machine** (if there's a "Get started" page, choose to create your own).
2. Choose the **Blank** template → **Select**.
3. Click the **Code** toggle → delete everything → paste all of `aws/step_functions.json`.
   The diagram shows: GluePreprocess → Done (or PipelineFailed).
4. **Config** tab → **State machine name**: `credit-risk-pipeline` → **Execution role**: choose an **existing role**
   → `CreditRiskRole`.
5. **Create** (top right). If a popup asks about role permissions, click **Confirm**.
   - If it complains the role lacks permissions, go to IAM → Roles → `CreditRiskRole` → **Add permissions**
     → **Attach policies** → tick `AWSStepFunctionsFullAccess` → **Add permissions**, then try again.
6. **Start execution** → **Start execution**. Boxes turn blue (running) → green (done) after a few minutes.

**Demo talking point:** Step Functions runs the pipeline and halts and flags it if any step fails.

## A6. CloudWatch (show the logs)
1. Open **CloudWatch** → left menu **Logs** → **Log groups**.
2. Open `/aws-glue/python-jobs/output` → click the latest log stream → you'll see the Glue job's `Done: ...` line.

---
---

# ACCOUNT B: Model Serving

> SageMaker **only hosts the model we already trained** (`stacked_model.pkl` + `preprocessor.pkl`).
> Nothing is trained on AWS.

## B1. IAM role `CreditRiskRole` + CLI user
**Role:**
1. Open **IAM** → **Roles** → **Create role** → **Custom trust policy** → paste `aws/iam_trust_policy.json` → **Next**.
2. Search and tick each:
   - `AmazonS3FullAccess`
   - `AmazonSageMakerFullAccess`
   - `AmazonDynamoDBFullAccess`
   - `AWSLambdaBasicExecutionRole`
   - `AmazonEC2ContainerRegistryReadOnly`
3. **Next** → **Role name**: `CreditRiskRole` → **Create role**.

**User for your laptop:**
1. IAM → **Users** → **Create user** → name `demo-cli` → **Next**.
2. **Attach policies directly** → tick `AdministratorAccess` → **Next** → **Create user**.
3. Click `demo-cli` → **Security credentials** tab → **Access keys** → **Create access key**.
4. Choose **Command Line Interface (CLI)** → tick the confirmation → **Next** → **Create access key**.
5. **Copy both keys now** (the secret is shown only once).
6. If someone else's laptop will do the Docker steps (see Part 0.1), send them **privately**
   (direct message, not a group chat): the two keys, the account B **Account ID**, and `<BUCKET_B>` (from B3).

## B2. Docker laptop setup (one time, on whichever laptop does the Docker steps)
1. Install **Docker Desktop** (https://www.docker.com/products/docker-desktop/), open it, and wait until it
   says "Engine running". Leave it open.
2. Install **AWS CLI** (https://aws.amazon.com/cli/ → Windows installer). Reopen your terminal. Check: `aws --version`.
3. `pip install boto3`
4. Run `aws configure` and enter **account B's** two keys, region `us-east-1`, and press Enter for the output format.
   (If this laptop already had other AWS keys configured, this replaces them. That's fine for the demo.)
5. Test: `aws sts get-caller-identity` must print **account B's** Account ID. If it shows a different number,
   redo step 4.
6. The repo on this laptop must contain the model files at exactly:
   `models/stacked/stacked_model.pkl` and `models/preprocessor.pkl`
   (They already exist on the friend's laptop that trained them. `TRAINING.md` is only for regenerating them if lost.)

## B3. S3 bucket (for the model file)
**S3** → **Create bucket** → name `<BUCKET_B>` → defaults → **Create bucket**. Leave it empty; the script fills it.

## B4. SageMaker (host the model)

**Who does what in B4:** 4b and 4e are done by the **B person in the console**. 4c, 4c-check and 4d are done
on the **Docker laptop** (B2). Order: B1 → B3 → 4b (B person) → B2, 4c, 4c-check, 4d (Docker laptop) → 4e onwards (B person).

**4a. Versions: nothing to do.** The library versions are **already pinned** in
`aws/sagemaker/requirements.txt` (scikit-learn 1.9.1, XGBoost 3.2.0, LightGBM 4.x, read directly from
the model files). The Dockerfile uses Python 3.13, which is fine.

**4b. Create an image repository.** Open **Elastic Container Registry** (search "ECR") → **Create repository**
(or "Get started") → **Repository name**: `credit-risk` → defaults → **Create**.

**4c. Build and upload the image.** With Docker Desktop running, open a terminal **in the repo folder** and run
these one by one (replace `<ACCOUNT_ID>` in each):
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

docker build --provenance=false -f aws/sagemaker/Dockerfile -t credit-risk .

docker tag credit-risk <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/credit-risk:latest

docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/credit-risk:latest
```
- The first command should print `Login Succeeded`.
- In the ECR console → `credit-risk`, you should now see an image tagged `latest`.

**4c-check (optional but recommended, ~3 min): test the image locally before/after pushing.**
This runs the exact container SageMaker will run, the same way SageMaker runs it (model files under
`/opt/ml/model`, requests on port 8080). If it works here, it works on SageMaker.
1. In a terminal **in the repo folder** (PowerShell):
   ```
   docker run --rm -p 8080:8080 -v "${PWD}/models:/opt/ml/model/models" credit-risk
   ```
   Leave it running. It should print `Running on http://0.0.0.0:8080`.
2. In a **second** terminal:
   ```
   curl.exe -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d "{\"AMT_CREDIT\": 500000, \"AMT_INCOME_TOTAL\": 180000}"
   ```
   Expected: `{"probability": 0.3..., "decision": "...", "tier": "..."}`.
   - `{"error": ...}` or a crash in the first terminal = something's wrong. Copy the error text and ask for help
     **before** deploying (fixing it here takes minutes; fixing it on SageMaker takes ~15 min per try).
3. Stop the container: press `Ctrl + C` in the first terminal.

**4d. Deploy.** Set `BUCKET = "<BUCKET_B>"` in `aws/deploy_sagemaker.py`, then from the repo folder:
```
python aws/deploy_sagemaker.py
```
This uploads the model to `s3://<BUCKET_B>/models/model.tar.gz` and creates the SageMaker model + endpoint.

**4e. Watch it.** Open **Amazon SageMaker AI** → left menu **Inference** → **Endpoints** (close any "Studio" popup;
you don't need Studio). `credit-risk-endpoint` goes **Creating** → **InService** in ~5–10 min.
- If **Failed**: click it → **View logs** (CloudWatch) and read the last error lines. After fixing,
  redo 4c and 4d (re-running `deploy_sagemaker.py` updates the existing endpoint).

**Demo talking point:** our trained stacked ensemble runs on a **serverless** SageMaker endpoint, billed only per call.

## B5. DynamoDB (audit table)
1. Open **DynamoDB** → **Create table**.
2. **Table name**: `credit-risk-audit`; **Partition key**: `applicant_id` (String); **Sort key**: `timestamp` (String).
3. Leave **Default settings** → **Create table**. Wait for **Active**.

**Demo talking point:** every prediction is logged here with a timestamp for auditability.

## B6. Lambda (prediction function)
1. Open **Lambda** → **Create function** → **Author from scratch**:
   - **Function name**: `credit-risk-predict`
   - **Runtime**: **Python 3.12** (any 3.x works)
   - Expand **Change default execution role** → **Use an existing role** → `CreditRiskRole`
   - **Create function**.
2. **Code source**: open `lambda_function.py`, delete everything, paste all of `aws/lambda_handler.py` → **Deploy**.
3. Scroll to **Runtime settings** → **Edit** → **Handler**: `lambda_function.handler` → **Save**.
4. **Configuration** tab → **General configuration** → **Edit** → **Timeout** `1 min 0 sec` → **Save**.
5. **Test** tab → Event name `test1` → Event JSON:
   ```json
   {"queryStringParameters": {"credit": "500000", "income": "180000", "days_employed": "1000"}}
   ```
   → **Test**. A green box with `statusCode: 200` and a body containing `probability`, `decision`, `tier` = success.
   The first test may time out while the endpoint wakes up; click **Test** again.
6. **DynamoDB** → **Tables** → `credit-risk-audit` → **Explore table items**: a new row is there.

**Demo talking point:** Lambda calls the model, writes the audit record and returns the result, with no servers to manage.

## B7. API Gateway (public URL)
1. Open **API Gateway** → **Create API** → **HTTP API** → **Build**.
2. **Add integration** → **Lambda** → `credit-risk-predict`. **API name**: `credit-risk-api` → **Next**.
3. **Routes**: Method `GET`, Resource path `/predict` → **Next**.
4. **Stages**: keep `$default` (auto-deploy) → **Next** → **Create**.
5. Copy the **Invoke URL** (e.g. `https://abc123xyz.execute-api.us-east-1.amazonaws.com`).
6. Test in a browser: `<Invoke URL>/predict?credit=500000&income=180000&days_employed=1000` → JSON appears.
   (A timeout or "Service Unavailable" on the first try = the endpoint was asleep; refresh.)
7. **Send the Invoke URL to the account C person.** ✉️

**Demo talking point:** API Gateway gives the model a public HTTPS endpoint the website can call.

## B8. CloudWatch (logs + one alarm)
1. **CloudWatch** → **Logs** → **Log groups**: show `/aws/lambda/credit-risk-predict` and
   `/aws/sagemaker/Endpoints/credit-risk-endpoint`.
2. Optional alarm: **Alarms** → **All alarms** → **Create alarm** → **Select metric** → **Lambda** →
   **By Function Name** → tick `credit-risk-predict` **Errors** → **Select metric** → Threshold: Greater than `0`
   → **Next** → notification: **Remove** → **Next** → name `credit-risk-lambda-errors` → **Next** → **Create alarm**.

---
---

# ACCOUNT C: Website

No IAM role needed in this account.

## C1. S3 (website file)
1. **S3** → **Create bucket** → name `<BUCKET_C>` → defaults → **Create bucket**.
2. (Do this after you get B's URL.) On your laptop, open `credit-risk-demo.html`, find this line near the `<script>` tag:
   `const API_BASE = 'http://localhost:8000';`
   Replace it with B's Invoke URL (no trailing slash, no `/predict`):
   `const API_BASE = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com';` → save.
3. Click `<BUCKET_C>` → **Upload** → `credit-risk-demo.html` → **Upload**.
   (Upload straight into the bucket, not into a folder.)

## C2. CloudFront (HTTPS website)
1. Open **CloudFront** → **Create distribution**. The wizard changes now and then; set just these:
   - **Origin domain**: click the box → choose `<BUCKET_C>.s3.us-east-1.amazonaws.com`
   - **Origin access**: **Origin access control settings (recommended)** → **Create new OAC** → **Create** (defaults)
   - **Web Application Firewall (WAF)**: **Do not enable security protections**
   - **Default root object**: `credit-risk-demo.html`
   - Everything else default → **Create distribution**.
   (If the wizard asks for a plan/pricing tier, pick the **free** one. If it offers
   "Allow private S3 bucket access to CloudFront", keep it selected. If you don't see **Default root object**
   in the wizard, set it after creating: your distribution → **General** tab → **Settings** → **Edit** →
   **Default root object** `credit-risk-demo.html` → **Save changes**.)
2. If a yellow banner says **"The S3 bucket policy needs to be updated"** → **Copy policy** → S3 → `<BUCKET_C>` →
   **Permissions** tab → **Bucket policy** → **Edit** → paste → **Save changes**.
   (If the console updated it automatically, skip this.)
3. Wait until **Last modified** shows a date instead of "Deploying" (~5 min).
4. Copy the **Distribution domain name** (e.g. `d1234abcd.cloudfront.net`) → open `https://d1234abcd.cloudfront.net`.
   Fill in the form → submit → the risk verdict appears. (Ask B to check DynamoDB: a new row.)
   - If you change the HTML later: re-upload it, then CloudFront → your distribution → **Invalidations** →
     **Create invalidation** → `/*` → **Create**, so the new version shows up.

**Demo talking point:** the UI is a static page in S3, delivered worldwide over HTTPS by CloudFront.

## C3. CloudWatch (show metrics)
**CloudFront** → left menu **Monitoring** (or **Reports & analytics**) → select the distribution → shows
requests and errors. That's the CloudWatch metrics for the website.

---
---

## Demo day checklist
1. **5 min before:** someone opens the CloudFront URL and submits the form once to wake the SageMaker endpoint.
2. **Account A tabs:** S3 bucket, Athena query 2 result, Glue job runs, Step Functions green execution, CloudWatch Glue log.
3. **Account B tabs:** SageMaker endpoint (InService), Lambda, API Gateway, DynamoDB items, CloudWatch Lambda log.
4. **Account C tabs:** the website, CloudFront distribution, S3 bucket.
5. Live flow: submit the form on the website (C) → refresh DynamoDB items (B) → the new row appears.

## Cleanup after the demo (avoid charges)
- **Account B:** SageMaker → delete the endpoint, endpoint configurations and models; ECR → delete the image;
  IAM → delete user `demo-cli` (it has admin keys!).
- **Account C:** CloudFront → select the distribution → **Disable** → wait → **Delete**.
- **Account A:** nothing costs money when idle (only the tiny S3 storage); delete the S3 bucket if you like.
- **Everyone:** a day later, open **Billing and Cost Management** → **Bills** and check the total is ~$0.
