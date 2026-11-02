# How to Run & Test the Credit Risk Prediction Platform

---

## ⚡ 1. Fastest Way: Access the Live Public CloudFront Deployment

> ### 🌐 **Live CloudFront Web Application**:  
> ### 👉 **[https://d254hkfcghacxc.cloudfront.net/](https://d254hkfcghacxc.cloudfront.net/)** 👈

**No installation, environment setup, or AWS credentials are required.**  
The complete enterprise architecture is deployed and live on AWS:
- **Frontend CDN**: Static single-page application served globally via **Amazon CloudFront** edge points over HTTPS.
- **API Routing**: Requests route to **Amazon API Gateway** HTTP API.
- **Compute & Feature Engineering**: **AWS Lambda** performs on-the-fly calculation of the 9 engineered domain ratios.
- **Inference Engine**: Containerized stacked ensemble hosted on an **Amazon SageMaker Serverless Endpoint**.
- **Audit Logging**: Every prediction is logged in real time to **Amazon DynamoDB** (`credit-risk-audit`) with applicant ID and UTC timestamp.

---

### Interactive Browser Test Walkthrough
1. Open **[https://d254hkfcghacxc.cloudfront.net/](https://d254hkfcghacxc.cloudfront.net/)** in your browser.
2. Fill out or adjust the applicant details in the form. You can test these two representative applicant personas:

#### Persona A: Low Risk (Prime Applicant)
- **Credit Amount**: `300,000`
- **Total Annual Income**: `180,000`
- **Years Employed**: `8.0`
- **Applicant Age**: `42`
- **External Bureau Score 2 (EXT_SOURCE_2)**: `0.75`
- **External Bureau Score 3 (EXT_SOURCE_3)**: `0.70`
- **Goods Price**: `280,000`
- **Delinquency Count (30 / 60 Days)**: `0`
- **Expected Outcome**: Default Probability $< 0.15 \rightarrow$ **`Approve (Low Risk)`** (Green verdict)

#### Persona B: High Risk (Subprime Applicant)
- **Credit Amount**: `1,200,000`
- **Total Annual Income**: `75,000`
- **Years Employed**: `0.5`
- **Applicant Age**: `22`
- **External Bureau Score 2 (EXT_SOURCE_2)**: `0.15`
- **External Bureau Score 3 (EXT_SOURCE_3)**: `0.12`
- **Goods Price**: `1,100,000`
- **Delinquency Count (30 / 60 Days)**: `2`
- **Expected Outcome**: Default Probability $\ge 0.25 \rightarrow$ **`Reject (High Risk)`** (Red verdict)

3. Click **"Evaluate Credit Risk"**. The real-time prediction card will render:
   - **Default Probability** (e.g., `8.4%`)
   - **Decision Verdict** (`Approve (Low Risk)`, `Review (Medium Risk)`, or `Reject (High Risk)`)
   - **Risk Tier Badge** (`LOW`, `MEDIUM`, or `HIGH`)
   - **Dynamic Feature Ratios** computed on the fly (Credit-to-Income, Annuity-to-Income, Implied Term, etc.)
   - **Transaction Audit Metadata** (Assigned Applicant UUID & Timestamp)

> [!NOTE]  
> **Serverless Cold Starts**: If the SageMaker Serverless endpoint has been idle, the very first invocation may take 5–15 seconds to spin up the container. Subsequent requests execute in milliseconds.

---

## 🌐 2. Testing the Live Cloud REST API via Terminal / cURL

You can also send HTTP GET requests directly to the live backend API Gateway powering the application:

```bash
# Windows PowerShell / CMD / Unix Terminal
curl "https://n5ll15gzi8.execute-api.us-east-1.amazonaws.com/predict?credit=500000&income=180000&days_employed=1000&age_years=35&ext2=0.55&ext3=0.50"
```

### Expected Response Format
```json
{
  "probability": 0.0894,
  "decision": "Approve (Low Risk)",
  "tier": "low"
}
```
*Note: In the cloud backend, this single call also triggers AWS Lambda to write a full audit item into the DynamoDB `credit-risk-audit` table.*

---

## 💻 3. Running the Application Locally (FastAPI + Demo UI)

To run the complete web server and inference engine on your local machine:

### Step 3.1: Prerequisites
- Python 3.10, 3.11, or 3.12 installed.
- Pre-trained model artifacts must exist in `models/` (already present in the repository):
  - `models/preprocessor.pkl`
  - `models/stacked/stacked_model.pkl`
  - `notebooks/optimal_threshold.txt`

### Step 3.2: Create Virtual Environment & Install Dependencies
Open a terminal in the root repository folder:

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv .venv

# Activate environment (if script execution is blocked, run: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3.3: Launch the Local Server
```bash
uvicorn predict_api:app --reload --port 8000
```

### Step 3.4: Open the Local UI
- Open your web browser and navigate to: **`http://localhost:8000/`**
- The local server serves `credit-risk-demo.html` directly. The UI will automatically detect that it is running locally on port 8000 and route predictions to the local FastAPI backend.

### Step 3.5: Query the Local API
```bash
curl "http://localhost:8000/predict?credit=500000&income=180000&days_employed=1000&age_years=35"
```

---

## ⌨️ 4. Running Single Predictions via CLI (`predict_single.py`)

You can run individual applicant predictions directly through the Python command-line interface without starting a web server.

### Option A: Complete JSON Argument
```bash
python predict_single.py "{\"AMT_CREDIT\": 500000, \"AMT_INCOME_TOTAL\": 180000, \"DAYS_EMPLOYED\": -1000, \"DAYS_BIRTH\": -15000, \"EXT_SOURCE_2\": 0.6, \"EXT_SOURCE_3\": 0.5}"
```

### Option B: Quick Positional Fallback Mode
Pass Credit, Income, and Days Employed as three positional arguments:
```bash
python predict_single.py 500000 180000 1000
```

### Output:
```json
{"probability": 0.1032, "decision": "Approve (Low Risk)", "tier": "low"}
```

---

## 🔬 5. Running the Offline MLOps Pipeline (Jupyter Notebooks)

To reproduce the machine learning experiments, feature engineering, and model training from scratch:

1. **Obtain the Dataset**:
   - Download `application_train.csv` (160 MB) from [Kaggle Home Credit Default Risk](https://www.kaggle.com/c/home-credit-default-risk/data).
   - Place the file at: `data/raw/application_train.csv`.
   *(Detailed dataset download steps are provided in [`TRAINING.md`](TRAINING.md)).*

2. **Launch Jupyter Lab / Notebook**:
   ```bash
   jupyter notebook
   ```

3. **Execute the Notebooks in Order**:
   - **`notebooks/01_data_exploration.ipynb`**: Analyzes the raw 307K records, missingness profiles, class skew (~92% vs 8%), and distributions.
   - **`notebooks/02_preprocessing.ipynb`**: Performs stratified 40% sampling, replaces the `365243` employment sentinel, constructs the 9 financial and stability ratios, fits the scikit-learn `ColumnTransformer`, and saves `models/preprocessor.pkl`.
   - **`notebooks/03_base_models.ipynb`**: Trains the 5 base classifiers (Random Forest, Logistic Regression, XGBoost, LightGBM, Gradient Boosting) with imbalance handling and saves ROC curves.
   - **`notebooks/04_stacking.ipynb`**: Constructs the 5-fold cross-validated `StackingClassifier` with a Logistic Regression meta-estimator and saves `models/stacked/stacked_model.pkl`.
   - **`notebooks/05_threshold_optimization.ipynb`**: Evaluates the asymmetric business cost matrix (\$12,000 FP vs. \$2,500 FN) across cutoffs $0.02 \le \tau \le 0.50$ and saves the optimal threshold ($\approx 0.49$) to `notebooks/optimal_threshold.txt`.
   - **`notebooks/06_evaluation.ipynb`**: Generates publication-ready confusion matrices, ROC plots, and classification reports in `reports/figures/`.

---

## ☁️ 6. Deploying to AWS (Full Multi-Account Cloud Infrastructure)

For a complete walkthrough on configuring and deploying the cloud resources across AWS accounts, follow **[`aws/README_AWS.md`](aws/README_AWS.md)**.

### Architecture Summary by Role:

| Account / Role | AWS Services Used | Key Tasks & Scripts |
|---|---|---|
| **Account A: Data Pipeline** | S3, Athena, Glue, Step Functions, CloudWatch | • Upload `application_train.csv` to `s3://<BUCKET_A>/raw/`<br/>• Execute SQL queries from `aws/athena_queries.sql`<br/>• Run serverless ETL script `aws/glue_preprocess.py`<br/>• Orchestrate pipeline via `aws/step_functions.json` |
| **Account B: Model Serving** | ECR, SageMaker, Lambda, DynamoDB, API Gateway | • Package container via `aws/sagemaker/Dockerfile` & push to ECR<br/>• Deploy serverless endpoint using `python aws/deploy_sagemaker.py`<br/>• Create `credit-risk-audit` DynamoDB table<br/>• Deploy `aws/lambda_handler.py` to AWS Lambda<br/>• Configure API Gateway HTTP API with `/predict` route |
| **Account C: Static Web Hosting** | S3, CloudFront CDN | • Upload `credit-risk-demo.html` to S3 website bucket<br/>• Create CloudFront distribution with Origin Access Control (OAC)<br/>• Distribute globally over HTTPS |

---

## 🛠️ 7. Troubleshooting & FAQs

### Q1: The CloudFront website shows "Service Unavailable" or takes a while on the first click.
- **Cause**: Amazon SageMaker Serverless endpoints scale to zero instances when idle to minimize cloud costs.
- **Remedy**: Wait 5–10 seconds and submit the request again. Once warmed up, response times drop to under 200 ms.

### Q2: PowerShell says `cannot be loaded because running scripts is disabled`.
- **Remedy**: Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell, confirm with `Y`, and re-run `.venv\Scripts\Activate.ps1`.

### Q3: How do I verify that DynamoDB is logging predictions?
- Open the AWS Console $\rightarrow$ **DynamoDB** $\rightarrow$ **Tables** $\rightarrow$ `credit-risk-audit` $\rightarrow$ **Explore table items**.
- Every time you submit the form on the CloudFront UI or send a request to the API, a new row containing the `applicant_id`, UTC `timestamp`, derived inputs, risk probability, and verdict will appear.

