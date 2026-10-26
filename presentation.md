# CreditIQ: Presentation & Codebase Walkthrough Guide
**A Cloud-Based MLOps Platform for Cost-Sensitive Credit Risk Prediction**  
*Academic Project Presentation Guide & 4-Person Role Division*

---

## 1. Executive Summary & Team Distribution Matrix

This master document divides the entire **CreditIQ** project—including the IEEE conference research paper ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex)) and the complete production codebase—across **four presenters (Person A, Person B, Person C, and Person D)**.

Each presenter is assigned a self-contained, end-to-end domain with dedicated paper subtopics, specific codebase walkthrough responsibilities, slide-by-slide scripts, visual artifacts, and defense/viva Q&A preparation.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          CREDITIQ PROJECT ARCHITECTURE                                           │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

   [ PERSON A: DATA & PIPELINE ]              [ PERSON B: ML & COST OPTIMIZATION ]
   • Section I & II-A, II-B, II-C, II-F        • Section I (Math), II-D, II-E, IV-A, V-A
   • Data Lake & Preprocessing                 • Stacking Classifier & Cost Sensitivity
   • S3, Athena, Glue, Step Functions          • Notebooks 01-06, Cost Matrix, ROC-AUC
                  │                                           │
                  ▼                                           ▼
   ┌──────────────────────────────┐            ┌──────────────────────────────┐
   │ Offline Pipeline & Storage   │            │ 5-Model Ensemble & Threshold │
   │ S3 Data Lake + Athena + Glue │            │ Stacking (0.7556) + τ*=0.49  │
   └──────────────┬───────────────┘            └──────────────┬───────────────┘
                  │                                           │
                  └─────────────────────┬─────────────────────┘
                                        │ Packaged as model.tar.gz
                                        ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                   [ PERSON C: INFERENCE & CONTAINERIZATION ]             │
   │                   • Section II-D, III-A, IV-B, IV-C, V-B                 │
   │                   • SageMaker Serverless Endpoint (4096 MB)              │
   │                   • Custom Docker Container (ECR) + predict_single.py    │
   │                   • AWS Lambda (Boto3 Orchestrator)                      │
   └────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                   [ PERSON D: DELIVERY, AUDIT & CLOUD ECONOMICS ]        │
   │                   • Section II-E, II-F, III-B, III-C, IV-D, V-C, VI, VII │
   │                   • CloudFront CDN (OAC) + S3 Demo UI (HTML/CSS/JS)      │
   │                   • API Gateway HTTP API + DynamoDB Audit Store          │
   │                   • IAM Least Privilege + CloudWatch + $0.47 Cost Model  │
   └──────────────────────────────────────────────────────────────────────────┘
```

### Team Master Allocation Matrix

| Presenter | Primary Focus Area | Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex)) | Assigned Codebase Files | Core Technologies / Metrics |
| :--- | :--- | :--- | :--- | :--- |
| **Person A** *(Data Engineering & Orchestration)* | Data Lake, Serverless ETL, Schema Engineering & Automated State Machine | **Sec I** (Intro, MLOps Lifecycle), **Sec I-A/B** (Literature & Gap), **Sec II-A** (Problem & Dataset), **Sec II-B** (Layer 1: S3/Athena), **Sec II-C** (Layer 2: Glue Preprocessing), **Sec II-F** (Step Functions), **Sec III-A/B** (S3, Athena, Glue, Step Functions) | [`aws/athena_queries.sql`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/athena_queries.sql)<br>[`aws/glue_preprocess.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/glue_preprocess.py)<br>[`aws/step_functions.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/step_functions.json)<br>[`notebooks/01_data_exploration.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/01_data_exploration.ipynb)<br>[`notebooks/02_preprocessing.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/02_preprocessing.ipynb) | S3, Athena, Glue, Step Functions, OpenCSVSerde, Pandas, NumPy<br>**307k rows, 9 ratios, 192 features** |
| **Person B** *(ML Modeling & Cost Decisioning)* | Cost-Sensitive Machine Learning, Stacking Ensembles & Business Decision Matrix | **Sec I** (Asymmetric Error Theory), **Sec I-A** (Literature on Stacking/Costs), **Sec II-D** (Layer 3: Model Stacking & Cost Optimization), **Eq. (2)** ($\tau^*$ derivation), **Sec II-E** (Tiered Decisioning Table I), **Sec IV-A** (Model Performance Table III, Confusion Matrix Table IV), **Sec V-A** (Cost Sensitivity vs Accuracy) | [`notebooks/03_base_models.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/03_base_models.ipynb)<br>[`notebooks/04_stacking.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/04_stacking.ipynb)<br>[`notebooks/05_threshold_optimization.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/05_threshold_optimization.ipynb)<br>[`notebooks/06_evaluation.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/06_evaluation.ipynb)<br>[`notebooks/optimal_threshold.txt`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/optimal_threshold.txt)<br>[`models/feature_columns.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/models/feature_columns.json) | Scikit-learn, XGBoost, LightGBM, Joblib, StackingClassifier<br>**ROC-AUC 0.7556, $\tau^* = 0.49$, 70% Default Recall** |
| **Person C** *(Cloud Serving & Containerization)* | Docker Containerization, Serverless Model Serving & Inference Backend | **Sec II-D** (Layer 4: SageMaker Serverless & Custom ECR), **Sec II-D** (Feature Reconstruction on the fly), **Sec III-A** (Docker, Flask, Boto3, ECR, SageMaker, Lambda), **Sec IV-B** (Functional Validation & Parity), **Sec IV-C** (Latency Breakdown Tables V & VI), **Sec V-B** (Serverless Trade-Offs & Cold Starts) | [`predict_single.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/predict_single.py)<br>[`aws/sagemaker/Dockerfile`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/Dockerfile)<br>[`aws/sagemaker/serve.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/serve.py)<br>[`aws/deploy_sagemaker.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/deploy_sagemaker.py)<br>[`aws/lambda_handler.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/lambda_handler.py)<br>[`predict_api.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/predict_api.py) | Docker, Amazon ECR, SageMaker Serverless (4096 MB), AWS Lambda, Flask, Gunicorn<br>**73 ms Server-Side Latency, 0.0 Numerical Drift** |
| **Person D** *(Delivery, Governance & Economics)* | Global Edge CDN, API Routing, Compliance Auditing, Security & FinOps | **Sec II-E** (API Gateway HTTP API, DynamoDB Audit Store), **Sec II-F** (Layer 5: IAM Least Privilege & CloudWatch Monitoring), **Sec III-B** (CloudFront, API Gateway, DynamoDB, IAM, CloudWatch, UI), **Sec III-C** (Cost Analysis Table II), **Sec IV-D** (Operational Comparison Table VII), **Sec V-C, VI, VII** (Benefits, Limitations, Future Scope, Conclusion) | [`aws/setup_cloudfront.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_cloudfront.py)<br>[`aws/setup_apigw.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_apigw.py)<br>[`credit-risk-demo.html`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/credit-risk-demo.html)<br>[`aws/iam_trust_policy.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/iam_trust_policy.json)<br>DynamoDB Schema & CloudWatch Logs/Alarms | CloudFront (OAC SigV4), API Gateway HTTP API, DynamoDB Single-Table, IAM, CloudWatch<br>**$0.47 Total Evaluation Cost, 100% Uptime, Zero-Leak Audit** |

---

## 2. Master Presentation Agenda & Timing (20-Minute Total Defense)

```
[00:00 - 05:00]  Person A: Motivation, Data Lake Architecture & Automated Preprocessing
[05:00 - 10:00]  Person B: Machine Learning Modeling, Stacking Ensembles & Cost-Optimal Thresholding
[10:00 - 15:00]  Person C: Custom Containerization, Serverless SageMaker & Low-Latency Lambda Serving
[15:00 - 20:00]  Person D: Global CloudFront Edge, DynamoDB Audit Compliance, Cloud Economics & Live Demo
[20:00 - 25:00]  Panel Q&A and Professor Committee Defense (All Presenters)
```

---

## 3. Person A: Data Engineering, Data Lake Architecture & Workflow Orchestration

### 3.1 Role & Ownership Overview
* **Presenter Role**: Data Lake Architect & Pipeline Engineer
* **Mission**: Explain why traditional credit scoring pipelines fail in production, formulate the data challenge, demonstrate how serverless data lake querying works on Amazon S3 with Amazon Athena, walk through distributed automated cleaning in AWS Glue, and show pipeline orchestration with AWS Step Functions.

### 3.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section I: INTRODUCTION (Lines 92–108)**
  * Context: Consumer lending demands sub-second decisions with full regulatory auditability.
  * Modeling challenges: Severe class sparsity (~8.07% default rate across 307,511 applicants) and asymmetric error costs.
  * Operational challenges: Siloed data science tooling, technical debt in ML systems, high idle compute costs of monolithic servers.
  * The Cloud MLOps Lifecycle: Fig. 1 ([`flowchart.png`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/system%20architecture.png)) showing stages from Ingestion $\rightarrow$ Processing $\rightarrow$ Training $\rightarrow$ Packaging $\rightarrow$ Serving $\rightarrow$ Monitoring.
* **Section I-A & I-B: Literature Review & Research Gap (Lines 109–120)**
  * Citations: Rani & Kumar (2022) on distributed ETL via AWS Glue and S3; Casimiro et al. (2023) on separating ingestion from execution; P.P. et al. (2022) on Step Functions workflow management.
  * Research Gap: Existing literature optimizes either the offline cost matrix in notebooks OR cloud serving in isolation. CreditIQ bridges offline cost-sensitive stacking directly with live, serverless AWS infrastructure.
* **Section II-A: Problem Formulation and Dataset (Lines 131–133)**
  * Home Credit Default Risk dataset (`application_train.csv`): 160 MB, 307,511 rows, 122 columns.
  * Imbalance breakdown: 282,686 non-defaulters (91.9%) vs 24,825 defaulters (8.1%).
  * Stratified 40% sample: 123,004 records used for balanced compute training while preserving target distributions.
* **Section II-B: Layer 1: Data Lake and Exploratory Querying (Lines 134–136)**
  * S3 prefix architecture: `raw/`, `processed/`, `athena-results/`, `models/`.
  * Amazon Athena: Serverless schema-on-read querying using `OpenCSVSerde`.
* **Section II-C: Layer 2: Preprocessing and Feature Engineering (Lines 137–143)**
  * Scrubbing the `365243` sentinel value in `DAYS_EMPLOYED`.
  * Dropping sparse columns (>45% missing values).
  * Synthesizing the 9 domain-specific financial ratios and stability features.
  * Scikit-learn `ColumnTransformer`: Median imputation, standard scaling, and one-hot encoding yielding a 192-dimensional design matrix.
* **Section II-F: Layer 5: Orchestration (AWS Step Functions) (Lines 182–184)**
  * AWS Step Functions state machine with synchronous `startJobRun.sync` and error-catch states.

### 3.3 Codebase Walkthrough & File Splits
Person A must open and explain the following repository files:

#### 1. [`aws/athena_queries.sql`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/athena_queries.sql)
* **Lines 1–18**: Explain the external table DDL:
  ```sql
  CREATE EXTERNAL TABLE IF NOT EXISTS credit_risk.application_train (
    sk_id_curr string, target string, name_contract_type string, ...
  )
  ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
  LOCATION 's3://credit-risk-data-aranck/raw/'
  TBLPROPERTIES ('skip.header.line.count'='1');
  ```
  *Key Concept*: Why `OpenCSVSerde`? It maps raw CSV text to table columns purely by position without spinning up any database instance or modifying raw source data.
* **Lines 19–37**: Explain the 4 serverless analytical queries:
  1. `COUNT(*)` verifying 307,511 rows.
  2. `GROUP BY target` validating 91.9% vs 8.1% class imbalance.
  3. Missing value count across annuity and goods price without memory overhead.
  4. Sentinel inspection finding thousands of occurrences of `365243` in `DAYS_EMPLOYED` (representing retired/unemployed individuals recorded as 1,000 years employed).

#### 2. [`aws/glue_preprocess.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/glue_preprocess.py)
* **Lines 1–24**: Walk through the serverless Glue Python Shell job:
  ```python
  df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
  df["CREDIT_INCOME_RATIO"]  = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"]
  df["ANNUITY_INCOME_RATIO"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"]
  df = df.drop(columns=df.columns[df.isnull().mean() > 0.45])
  ```
  *Key Concept*: Explain why Glue Python Shell was chosen over full PySpark—for a 160 MB dataset, PySpark cluster allocation overhead (several minutes) is wasteful; Python Shell provisions in seconds and costs pennies on DPU-minute billing.

#### 3. [`aws/step_functions.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/step_functions.json)
* **Lines 1–29**: Walk through the Amazon States Language state machine:
  ```json
  "GluePreprocess": {
    "Type": "Task",
    "Resource": "arn:aws:states:::glue:startJobRun.sync",
    "Parameters": { "JobName": "credit-risk-preprocess" },
    "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "PipelineFailed" }],
    "Next": "Done"
  }
  ```
  *Key Concept*: Emphasize `.sync` integration—Step Functions pauses execution until the Glue ETL job signals success or failure, preventing silent data corruption in downstream models.

#### 4. [`notebooks/01_data_exploration.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/01_data_exploration.ipynb) & [`notebooks/02_preprocessing.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/02_preprocessing.ipynb)
* Show how exploratory findings in Notebook 01 were industrialized into Notebook 02:
  * Stratified 40% subsampling (123,004 rows).
  * Derivation of the **9 engineered domain features**:
    $$\text{CREDIT\_INCOME\_RATIO} = \frac{\text{AMT\_CREDIT}}{\text{AMT\_INCOME\_TOTAL}}, \quad \text{ANNUITY\_INCOME\_RATIO} = \frac{\text{AMT\_ANNUITY}}{\text{AMT\_INCOME\_TOTAL}}$$
    $$\text{CREDIT\_DURATION\_RATIO} = \frac{\text{AMT\_CREDIT}}{\text{AMT\_ANNUITY}}, \quad \text{GOODS\_CREDIT\_RATIO} = \frac{\text{AMT\_GOODS\_PRICE}}{\text{AMT\_CREDIT}}$$
    $$\text{EMPLOYED\_AGE\_RATIO} = \frac{\text{DAYS\_EMPLOYED}}{\text{DAYS\_BIRTH}}, \quad \text{INCOME\_PER\_PERSON} = \frac{\text{AMT\_INCOME\_TOTAL}}{\max(\text{CNT\_FAM\_MEMBERS}, 1)}$$
    $$\text{AGE\_YEARS} = \frac{-\text{DAYS\_BIRTH}}{365}, \quad \text{YEARS\_EMPLOYED} = \frac{-\text{DAYS\_EMPLOYED}}{365}, \quad \text{DOC\_COUNT}$$
  * `ColumnTransformer` with `SimpleImputer(strategy='median')` + `StandardScaler()` for 68 numeric columns, and `SimpleImputer(strategy='constant')` + `OneHotEncoder(handle_unknown='ignore')` for 12 categorical columns.
  * Output: 192 encoded features saved as [`models/preprocessor.pkl`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/models/preprocessor.pkl) and [`models/feature_columns.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/models/feature_columns.json).

### 3.4 Slide-by-Slide Speaking Script
* **Slide 1: Title & The Credit Lending Problem**
  > *"Good morning committee members. In retail banking, approving a loan is a high-stakes balance: approving someone who defaults causes catastrophic losses, while rejecting a creditworthy borrower loses revenue. In our project, CreditIQ, we tackle this with an enterprise-grade cloud MLOps platform on AWS. I will start by detailing our data lake architecture and automated preprocessing pipeline."*
* **Slide 2: Dataset Realities & Severe Class Imbalance**
  > *"We utilize the Kaggle Home Credit Default Risk benchmark: 307,511 applicants across 122 variables. As shown in our Athena queries, only 8.07% of borrowers default. If a naive model simply approves everyone, it achieves 91.9% accuracy but destroys bank balance sheets. Furthermore, raw data contains anomalies like `365243` days employed—which is a data-entry sentinel representing retired individuals that would severely skew gradient descent if treated as actual work history."*
* **Slide 3: Serverless Data Lake on S3 & Athena**
  > *"Rather than spinning up an expensive RDS or Redshift database, we engineered a serverless Data Lake using Amazon S3 partitioned into `raw/`, `processed/`, and `athena-results/`. With Amazon Athena, we ran schema-on-read SQL using Hive OpenCSVSerde directly on S3 CSV files. We scanned 158.4 MB of data in 1.9 seconds for a fraction of a cent without maintaining any infrastructure."*
* **Slide 4: Feature Engineering & Preprocessing Transformation**
  > *"In our Glue ETL job and scikit-learn preprocessing pipeline, we drop columns with more than 45% missing values, replace the 365243 sentinel with nulls, and compute 9 high-impact financial ratios including Debt-to-Income, Annuity-to-Income, and Career Stability. Our fitted ColumnTransformer applies median imputation, standard scaling, and one-hot encoding, expanding our cleaned tabular features into a 192-dimensional vector stored as `preprocessor.pkl`."*
* **Slide 5: Automated Workflow Orchestration with Step Functions**
  > *"To ensure repeatability and avoid silent pipeline failures, we orchestrated the data pipeline using AWS Step Functions. Written in Amazon States Language, our state machine synchronously triggers our AWS Glue Python Shell job, awaits execution confirmation, and routes to an explicit failure state if an anomaly occurs. Now, my teammate Person B will explain how these clean features feed into our machine learning models and cost-optimal decision matrix."*

### 3.5 Viva & Committee Defense Q&A
1. **Q: Why use Amazon Athena instead of loading the data into Amazon RDS PostgreSQL?**  
   *Answer*: RDS requires provisioning an always-on EC2 database instance that incurs 24/7 billing even when no queries are executed. Athena is 100% serverless, charges only $5.00 per terabyte scanned, operates directly on raw S3 files via schema-on-read, and costs less than $0.01 for our entire exploratory analysis.
2. **Q: Why drop columns with >45% missing values instead of imputing all of them?**  
   *Answer*: Imputing columns where over half the data is absent injects high synthetic variance and creates spurious correlations in tree-based models. Dropping columns with >45% missingness removed uninformative building mode indicators while preserving all critical financial, demographic, and credit bureau variables.
3. **Q: Why was Step Functions chosen over an open-source tool like Apache Airflow?**  
   *Answer*: Apache Airflow requires deploying a web server, scheduler, and worker cluster (e.g., Celery/Redis or Amazon MWAA at ~$300/month). AWS Step Functions is completely serverless, costs $0.025 per 1,000 state transitions, integrates natively with AWS SDK service APIs with `.sync` execution, and has zero idle cost.

---

## 4. Person B: Machine Learning Modeling, Stacking Ensembles & Cost-Sensitive Optimization

### 4.1 Role & Ownership Overview
* **Presenter Role**: Lead Machine Learning Scientist & Decision Theorist
* **Mission**: Detail the training of the 5 base classifiers, justify the mathematical architecture of the Stacking Ensemble, explain out-of-fold probability blending, formulate the business cost matrix, and prove why threshold tuning ($\tau^* = 0.49$) is mathematically and financially superior to arbitrary 0.5 classification.

### 4.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section I: Asymmetric Error Cost in Credit Risk (Lines 95–96)**
  * The fundamental flaw of standard machine learning in lending: Type I vs Type II errors are not equal.
  * A False Approval (lending to a defaulting applicant) costs orders of magnitude more than a False Rejection (rejecting a creditworthy applicant).
* **Section I-A: Literature Review on Ensembles & Thresholding (Lines 116–117)**
  * Citations: Rofik et al. (2023) and Alamsyah et al. (2024) demonstrating stacked ensembles outperform isolated classifiers; Petrides et al. (2020) and Shen et al. (2019) proving the necessity of cost-sensitive threshold shifting in imbalanced credit scoring.
* **Section II-D: Layer 3: Model Training, Stacking and Cost Optimisation (Lines 144–152)**
  * The 5 base classifiers: Logistic Regression (`class_weight='balanced'`, saga solver), Random Forest, scikit-learn Gradient Boosting, XGBoost (`scale_pos_weight`), and LightGBM.
  * 5-fold cross-validated `StackingClassifier` with Logistic Regression meta-learner.
  * Serialization into [`models/stacked/stacked_model.pkl`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/models/stacked).
* **Equation (2): The Cost Optimization Formulation (Lines 147–151)**
  $$\tau^{*} = \arg\min_{\tau \in [0.02,\,0.50]} \; C_{\mathrm{FA}}\,N_{\mathrm{FA}}(\tau) + C_{\mathrm{FR}}\,N_{\mathrm{FR}}(\tau)$$
  * $C_{\mathrm{FA}} = \$12,000$ (cost of False Approval—loan principal loss).
  * $C_{\mathrm{FR}} = \$2,500$ (cost of False Rejection—lost interest margin and customer acquisition cost).
  * Optimal threshold scan identifying $\tau^* = 0.49$.
* **Section II-E: Tiered Decisioning Policy (Table I) (Lines 161–177)**
  * Low Risk ($p < 0.245$): Automated Instant Approval.
  * Medium Risk ($0.245 \le p < 0.49$): Routed to Human Underwriter Manual Review.
  * High Risk ($p \ge 0.49$): Automated Instant Rejection.
* **Section IV-A: Model Performance & Evaluation Results (Tables III & IV) (Lines 259–297)**
  * Held-out test set ROC-AUC table (24,601 test records):
    * Random Forest: `0.7310`
    * Logistic Regression: `0.7436`
    * XGBoost: `0.7515`
    * LightGBM: `0.7542`
    * Gradient Boosting: `0.7584`
    * **Stacked Ensemble**: `0.7556`
  * Confusion matrix analysis at $\tau^* = 0.49$: 1,398 out of 1,986 actual defaulters successfully caught (**70.4% default recall**).
* **Section V-A: Discussion: Cost Sensitivity versus Accuracy (Lines 412–428)**
  * Why accuracy is a deceptive metric in financial risk.
  * Why the ensemble provides smoother probability calibration than single decision trees.

### 4.3 Codebase Walkthrough & File Splits
Person B must open and explain the following repository files:

#### 1. [`notebooks/03_base_models.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/03_base_models.ipynb)
* Walk through base model training and class imbalance parameterization:
  ```python
  # Handling severe 92:8 class imbalance algorithmically
  lr = LogisticRegression(class_weight='balanced', solver='saga', max_iter=500)
  xgb_clf = XGBClassifier(scale_pos_weight=neg_to_pos_ratio, eval_metric='auc')
  lgb_clf = LGBMClassifier(is_unbalance=True, boosting_type='gbdt')
  ```
* Show the base ROC curves in [`reports/figures/03_base_models_roc.png`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reports/figures/03_base_models_roc.png).

#### 2. [`notebooks/04_stacking.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/04_stacking.ipynb)
* Walk through the out-of-fold `StackingClassifier` implementation:
  ```python
  estimators = [
      ('lr', lr_model),
      ('rf', rf_model),
      ('xgb', xgb_model),
      ('lgb', lgb_model)
  ]
  stacked = StackingClassifier(
      estimators=estimators,
      final_estimator=LogisticRegression(),
      cv=5,
      stack_method='predict_proba',
      n_jobs=-1
  )
  stacked.fit(X_train, y_train)
  ```
  *Key Concept*: Explain how 5-fold cross-validation generates out-of-fold predictions for the training set, ensuring the Logistic Regression meta-learner does not overfit to base model training predictions.
* Show [`reports/figures/04_stacking_roc_comparison.png`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reports/figures/04_stacking_roc_comparison.png).

#### 3. [`notebooks/05_threshold_optimization.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/05_threshold_optimization.ipynb) & [`notebooks/optimal_threshold.txt`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/optimal_threshold.txt)
* Walk through the cost function calculation:
  ```python
  C_FA = 12000  # Cost of False Approval (defaulter approved)
  C_FR = 2500   # Cost of False Rejection (good borrower rejected)

  thresholds = np.linspace(0.02, 0.50, 49)
  total_costs = []
  for t in thresholds:
      preds = (probs >= t).astype(int)
      fa = np.sum((preds == 0) & (y_test == 1))
      fr = np.sum((preds == 1) & (y_test == 0))
      cost = (C_FA * fa) + (C_FR * fr)
      total_costs.append(cost)

  optimal_t = thresholds[np.argmin(total_costs)]  # Evaluates to 0.49
  ```
* Open [`notebooks/optimal_threshold.txt`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/optimal_threshold.txt) and show `0.49`.
* Show [`reports/figures/05_cost_vs_threshold.png`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reports/figures/05_cost_vs_threshold.png).

#### 4. [`notebooks/06_evaluation.ipynb`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/notebooks/06_evaluation.ipynb)
* Present the held-out test evaluation on 24,601 records.
* Explain the Confusion Matrix at $\tau^* = 0.49$ ([`reports/figures/06_confusion_matrix_optimal.png`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reports/figures/06_confusion_matrix_optimal.png)):
  * **True Repay (TN)**: 15,313
  * **False Rejection / Review (FP)**: 7,302
  * **False Approval (FN)**: 588 (Kept to a minimum!)
  * **True Default Detected (TP)**: 1,398 (70.4% default recall)

### 4.4 Slide-by-Slide Speaking Script
* **Slide 6: The Fallacy of 0.5 Cutoffs in Credit Risk**
  > *"Thank you, Person A. In standard machine learning tutorials, binary classifiers use a default threshold of 0.5. In commercial banking, this is dangerous. If we lend $100,000 to an applicant who defaults, the bank loses the unrecoverable principal—often $12,000 or more after recovery costs. But if we reject a good applicant, we only lose the interest profit margin—roughly $2,500. A False Approval is nearly 5 times more damaging than a False Rejection."*
* **Slide 7: Base Models & Class-Imbalance Strategies**
  > *"To capture both linear patterns and non-linear interactions, we trained 5 diverse models: Logistic Regression, Random Forest, scikit-learn Gradient Boosting, XGBoost, and LightGBM. To counteract the 92:8 class imbalance without corrupting distributions with synthetic SMOTE noise, we tuned algorithmic parameters: using balanced class weights for linear models and scaling positive class gradients via `scale_pos_weight` in XGBoost."*
* **Slide 8: The Stacking Ensemble Architecture**
  > *"Rather than relying on a single tree model, we built a 5-fold cross-validated Stacking Ensemble. Logistic Regression, Random Forest, XGBoost, and LightGBM serve as base estimators. A Logistic Regression meta-learner blends their out-of-fold probability predictions. This ensemble achieves a held-out ROC-AUC of 0.7556. Stacking linear and non-linear decision surfaces produces a well-calibrated, smooth probability output that is resilient to feature volatility."*
* **Slide 9: Cost Function Formulation & Optimal Threshold $\tau^* = 0.49$**
  > *"We mathematically formalized business loss as a function of the threshold $\tau$, sweeping candidate values across our validation set. As seen in our cost curve, business losses form a steep U-shaped curve. The global loss minimum occurs at $\tau^* = 0.49$. At this threshold, the model catches 1,398 out of 1,986 defaulters—achieving a 70.4% recall on credit defaults and shielding the institution from extreme default loss."*
* **Slide 10: Operational Three-Tier Risk Policy**
  > *"Rather than a binary yes/no, our production policy translates probability into three tiers: Low Risk below 0.245 receives automated approval; High Risk above 0.49 is rejected; and Medium Risk between 0.245 and 0.49 is routed for human underwriting review. Next, Person C will demonstrate how we containerized this model and deployed it onto an AWS serverless inference endpoint."*

### 4.5 Viva & Committee Defense Q&A
1. **Q: Single Gradient Boosting achieved an ROC-AUC of 0.7584, while the Stacked Ensemble achieved 0.7556. Why deploy the ensemble if its ROC-AUC is 0.0028 lower?**  
   *Answer*: ROC-AUC measures ranking discrimination, not probability calibration. Single boosted trees produce sharp, uncalibrated probability spikes near decision boundaries. The stacked ensemble blends linear decision boundaries (Logistic Regression) with tree ensembles (Random Forest, XGBoost, LightGBM), producing smoother, more reliable probability estimates essential for stable thresholding and financial underwriting.
2. **Q: How does 5-fold cross-validation in the StackingClassifier prevent data leakage?**  
   *Answer*: If base models predicted on the data they were trained on, their probabilities would be over-optimistic, causing the meta-learner to overfit to training noise. 5-fold CV ensures the meta-estimator is trained strictly on out-of-fold predictions—where each fold's probabilities are generated by base models that never saw that fold during training.
3. **Q: Why not use SMOTE or Random Oversampling for handling the class imbalance?**  
   *Answer*: In 192-dimensional sparse tabular data with numerous one-hot encoded flags, synthetic interpolation via SMOTE creates unrealistic applicant records in empty feature space. Instead, algorithmic weighting (`scale_pos_weight` in XGBoost and `class_weight='balanced'` in Logistic Regression) penalizes minority class misclassification during gradient updates without distorting empirical data topology.

---

## 5. Person C: Cloud Containerization, Serverless Inference & Real-Time Backend

### 5.1 Role & Ownership Overview
* **Presenter Role**: Cloud Infrastructure & ML Serving Engineer
* **Mission**: Detail the packaging of models into Amazon ECR, demonstrate the SageMaker Serverless endpoint configuration, explain the dynamic on-the-fly feature reconstruction engine in `predict_single.py`, analyze the AWS Lambda event routing layer, and break down server-side inference latency down to the millisecond.

### 5.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section II-D: Layer 4: Model Hosting (Amazon SageMaker) (Lines 154–156)**
  * Artifact bundle packaging: `model.tar.gz` containing `stacked_model.pkl` and `preprocessor.pkl`.
  * Custom Amazon ECR container: Python 3.13-slim, pinning exact dependencies (scikit-learn, XGBoost, LightGBM, Flask).
  * Amazon SageMaker Serverless Endpoint: 3072–4096 MB memory allocation, max concurrency of 2, auto-scaling to zero when idle.
  * SageMaker REST contract: Exposing `/ping` for health checks and `/invocations` for real-time scoring.
* **Section II-D: On-the-Fly Feature Reconstruction (Lines 157–160)**
  * The production reality: A loan officer or web user provides only 5 to 15 fields, not all 192 raw and encoded features.
  * Merging partial inputs with a baseline dictionary of typical values (`DEFAULTS`).
  * Dynamically recomputing all 9 engineered ratios in real time.
  * Aligning column order strictly with the schema contract (`preprocessor.feature_names_in_`).
* **Section III-A: Technology Stack (Lines 188–196)**
  * Docker, Python 3.13-slim, Flask, Boto3, Amazon ECR, SageMaker Serverless, AWS Lambda.
* **Section IV-B: Functional Validation & Parity (Lines 298–300)**
  * Numerical parity: 500 test records scored both locally on FastAPI and on AWS SageMaker.
  * **Maximum absolute probability difference = 0.0** (Bit-identical execution).
* **Section IV-C: Latency Breakdown (Tables V & VI) (Lines 320–362)**
  * Cloud server-side latency over 1,000 warm requests:
    * API Gateway routing: **6 ms**
    * Lambda execution overhead: **9 ms**
    * SageMaker endpoint overhead: **11 ms**
    * Model inference (preprocessor + stacked ensemble): **41 ms**
    * DynamoDB PutItem audit write: **6 ms**
    * **Total server-side median latency: 73 ms** (Only 27 ms over local localhost!)
* **Section V-B: Discussion: Serverless Trade-Offs (Lines 429–445)**
  * Cold start analysis: 9.8-second average cold start on container initialization vs 73 ms warm execution.
  * Trade-off: Scale-to-zero saves hundreds of dollars in idle compute at the cost of an initial warm-up delay.

### 5.3 Codebase Walkthrough & File Splits
Person C must open and explain the following repository files:

#### 1. [`predict_single.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/predict_single.py)
* Walk through the core inference engine (Lines 1–148):
  * **Lines 11–21**: Loading serialized artifacts and the cost-optimal threshold:
    ```python
    model = joblib.load("models/stacked/stacked_model.pkl")
    preprocessor = joblib.load("models/preprocessor.pkl")
    with open("notebooks/optimal_threshold.txt") as f:
        OPTIMAL_THRESHOLD = float(f.read().strip())
    ```
  * **Lines 60–101**: The `DEFAULTS` baseline dictionary providing typical applicant values.
  * **Lines 104–126**: On-the-fly feature engineering:
    ```python
    data = DEFAULTS.copy()
    data.update(inputs)
    data['CREDIT_INCOME_RATIO']   = credit / income if income else 0
    data['ANNUITY_INCOME_RATIO']  = annuity / income if income else 0
    data['CREDIT_DURATION_RATIO'] = credit / annuity if annuity else 0
    data['EMPLOYED_AGE_RATIO']    = days_emp / days_age if days_age else 0
    data['GOODS_CREDIT_RATIO']    = goods / credit if credit else 0
    data['AGE_YEARS']             = round(-days_age / 365, 1)
    data['YEARS_EMPLOYED']        = round(-days_emp / 365, 1)
    data['INCOME_PER_PERSON']     = income / max(data['CNT_FAM_MEMBERS'], 1)
    ```
  * **Lines 129–145**: Strict schema alignment and decision tiering:
    ```python
    df = pd.DataFrame([data])[list(preprocessor.feature_names_in_)]
    df_processed = preprocessor.transform(df)
    prob = model.predict_proba(df_processed)[0][1]
    if prob >= OPTIMAL_THRESHOLD:
        decision, tier = "Reject (High Risk)", "high"
    elif prob >= OPTIMAL_THRESHOLD * 0.5:
        decision, tier = "Review (Medium Risk)", "medium"
    else:
        decision, tier = "Approve (Low Risk)", "low"
    ```

#### 2. [`aws/sagemaker/Dockerfile`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/Dockerfile) & [`aws/sagemaker/serve.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/serve.py)
* Walk through container definition and server contract:
  ```dockerfile
  FROM python:3.13-slim
  RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
  COPY aws/sagemaker/requirements.txt /app/requirements.txt
  RUN pip install --no-cache-dir -r /app/requirements.txt && pip uninstall -y nvidia-nccl-cu12
  COPY predict_single.py /app/predict_single.py
  COPY notebooks/optimal_threshold.txt /app/notebooks/optimal_threshold.txt
  COPY aws/sagemaker/serve.py /app/serve.py
  ENTRYPOINT ["python", "/app/serve.py"]
  ```
  *Key Concept*: Why `libgomp1`? OpenMP is strictly required by XGBoost and LightGBM for multi-threaded inference in Linux. Unnecessary CUDA libraries are removed to minimize container size to ~400 MB.
* Walk through [`aws/sagemaker/serve.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/serve.py):
  * `os.chdir("/opt/ml/model")` where SageMaker automatically mounts `model.tar.gz`.
  * Flask route `@app.get("/ping")` returning 200 for SageMaker health checks.
  * Flask route `@app.post("/invocations")` deserializing JSON and calling `predict_single.predict()`.

#### 3. [`aws/deploy_sagemaker.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/deploy_sagemaker.py)
* Walk through deployment automation:
  * Creating `model.tar.gz` containing `stacked_model.pkl` and `preprocessor.pkl`.
  * Uploading to `s3://{BUCKET}/models/model.tar.gz`.
  * Calling `sm.create_model()`, `sm.create_endpoint_config()` with `ServerlessConfig: {"MemorySizeInMB": 3072, "MaxConcurrency": 2}`, and `sm.create_endpoint()`.

#### 4. [`aws/lambda_handler.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/lambda_handler.py)
* Walk through the serverless integration layer:
  ```python
  def handler(event, context):
      q = event.get("queryStringParameters") or {}
      inputs = {NUM[k]: float(v) for k, v in q.items() if k in NUM}
      inputs.update({STR[k]: v for k, v in q.items() if k in STR})
      if "days_employed" in q:
          inputs["DAYS_EMPLOYED"] = -abs(float(q["days_employed"]))
      if "age_years" in q:
          inputs["DAYS_BIRTH"] = -(float(q["age_years"]) * 365)

      resp = sm.invoke_endpoint(
          EndpointName="credit-risk-endpoint",
          ContentType="application/json",
          Body=json.dumps(inputs)
      )
      result = json.loads(resp["Body"].read())
      # DynamoDB audit write and CORS response formatting...
  ```

### 5.4 Slide-by-Slide Speaking Script
* **Slide 11: The Cloud Serving Challenge**
  > *"Thank you, Person B. Training an ML model in a Jupyter Notebook is straightforward, but serving it to retail loan officers with low latency, zero maintenance, and strict schema compliance is where most data science projects fail. In CreditIQ, we engineered a fully containerized serverless serving architecture on Amazon SageMaker and AWS Lambda."*
* **Slide 12: Custom Containerization via Amazon ECR**
  > *"Rather than relying on AWS pre-built scikit-learn containers that lack modern LightGBM or XGBoost versions, we built a custom lightweight Docker container based on `python:3.13-slim`. We installed OpenMP (`libgomp1`) for high-speed multi-threaded tree inference, stripped unused GPU libraries, implemented the SageMaker `/ping` and `/invocations` contract in Flask, and pushed the image to Amazon Elastic Container Registry (ECR)."*
* **Slide 13: Amazon SageMaker Serverless Inference**
  > *"We deployed our container to a SageMaker Serverless Endpoint configured with 3072 MB memory. Unlike traditional provisioned endpoints that cost $50 to $100 per month just sitting idle, serverless inference automatically scales down to absolute zero when there are no loan applications. AWS bills us strictly per millisecond of compute during active scoring."*
* **Slide 14: On-the-Fly Feature Reconstruction Engine**
  > *"A critical contribution of our codebase in `predict_single.py` is On-the-Fly Feature Reconstruction. An applicant only enters 10 basic fields like income, credit amount, and age. Our module merges these over a curated baseline vector, recalculates our 9 engineered financial ratios in microseconds, and aligns columns exactly to the 192 features expected by our preprocessor. This eliminates training-serving skew by construction."*
* **Slide 15: Low-Latency Performance & Parity Verification**
  > *"In our testing across 1,000 warm requests, total server-side latency averaged just 73 milliseconds: 6 ms in API Gateway, 9 ms in Lambda, 11 ms in SageMaker overhead, 41 ms in model execution, and 6 ms in DynamoDB writing. Most importantly, across 500 test applicants, our cloud predictions showed 0.0 numerical drift compared to local execution. Now, Person D will explain our edge content delivery, compliance auditing, and cloud economics."*

### 5.5 Viva & Committee Defense Q&A
1. **Q: How did you handle the 9.8-second serverless cold start in SageMaker?**  
   *Answer*: Cold starts occur only on the initial container spin-up after an idle period. At 9.8 seconds, it easily finishes within API Gateway's 29-second HTTP timeout. For production commercial banks operating during fixed hours (9 AM - 5 PM), SageMaker supports provisioned concurrency or scheduled warm-up pings to eliminate cold starts entirely.
2. **Q: Why place an AWS Lambda function between API Gateway and SageMaker instead of integrating API Gateway directly with SageMaker?**  
   *Answer*: API Gateway direct integration would require mapping raw query parameters into SageMaker JSON using complex VTL (Velocity Template Language), and it cannot simultaneously write audit records to DynamoDB. Lambda acts as an event orchestrator: it validates types, formats payload bodies, calls SageMaker, logs the immutable audit row to DynamoDB, and injects CORS headers in a clean 9 ms execution.
3. **Q: How does the system ensure zero training-serving feature skew?**  
   *Answer*: The exact same scoring code ([`predict_single.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/predict_single.py)) and serialized artifacts (`preprocessor.pkl`, `optimal_threshold.txt`) are copied directly into the Docker container. Furthermore, `predict_single.py` forces input DataFrames to match `preprocessor.feature_names_in_` in exact name and column order before calling `.transform()`.

---

## 6. Person D: Global Delivery, Security Governance, Auditability & Financial Economics

### 6.1 Role & Ownership Overview
* **Presenter Role**: Cloud Architect, Security & Compliance Lead
* **Mission**: Demonstrate edge content delivery using Amazon CloudFront with Origin Access Control (OAC), explain API Gateway HTTP API routing, prove regulatory audit compliance with Amazon DynamoDB, present the unified IAM security and CloudWatch observability architecture, detail the $0.47 FinOps cost analysis, and execute the live interactive demonstration.

### 6.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section II-E: Layer 4: API Routing and Auditing (Lines 179–181)**
  * Amazon API Gateway HTTP API: Low-latency `$default` auto-deploy route `GET /predict`.
  * Amazon DynamoDB single-table audit store: Partition Key `applicant_id` (UUID), Sort Key `timestamp` (UTC ISO-8601).
  * Persisting raw inputs, computed default probability, risk tier, and final decision for compliance with Fair Credit Reporting Act (FCRA) and ECOA regulations.
* **Section II-F: Layer 5: Security, Governance & Observability (Lines 182–184)**
  * AWS IAM: `sts:AssumeRole` trust policy granting least-privilege execution permissions to Glue, SageMaker, Lambda, and Step Functions without hardcoding API keys.
  * Amazon CloudWatch: Centralized log groups (`/aws/lambda/credit-risk-predict`, `/aws/sagemaker/Endpoints/credit-risk-endpoint`), latency metrics, and error alarms.
* **Section III-B: Technology Stack (Lines 212–223)**
  * Amazon CloudFront CDN with Origin Access Control (OAC SigV4) distributing the frontend globally over HTTPS while keeping the S3 bucket 100% private.
  * Amazon DynamoDB on-demand capacity mode.
  * Frontend: Single-page zero-build HTML5, Vanilla CSS, and JavaScript ([`credit-risk-demo.html`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/credit-risk-demo.html)).
* **Section III-C: AWS Service Cost Analysis (Table II) (Lines 224–248)**
  * Full workload evaluation cost breakdown:
    * Amazon S3: **$0.01**
    * Amazon Athena: **$0.01**
    * AWS Glue (DPU-minutes): **$0.03**
    * SageMaker Serverless (compute seconds): **$0.38**
    * AWS Lambda (1M free tier): **$0.00**
    * API Gateway HTTP API: **$0.00**
    * Amazon DynamoDB: **$0.00**
    * Amazon CloudFront (1 TB free tier): **$0.00**
    * Step Functions (free tier): **$0.00**
    * CloudWatch: **$0.00**
    * Amazon ECR storage: **$0.04**
    * **Total Evaluation Cost: $0.47 USD**
* **Section IV-D: Operational Comparison (Table VII) (Lines 363–386)**
  * 100% request success rate over 1,000 requests.
  * Sustained throughput: 21.4 requests/second under concurrency limit 2.
  * Audit persistence: Exactly 1,000 out of 1,000 decisions stored in DynamoDB.
* **Section V-C, VI & VII: Operational Benefits, Limitations, Future Scope & Conclusion (Lines 446–475)**
  * Limitations: Single-region WAN latency (Mumbai client to `us-east-1` adding ~200 ms network RTT); single-table Home Credit dataset without bureau history joins.
  * Future Scope: Multi-region active-active deployment (`ap-south-1` + `us-east-1`), Amazon Cognito OAuth2 user authentication, and AWS KMS customer-managed encryption keys.

### 6.3 Codebase Walkthrough & File Splits
Person D must open and explain the following repository files:

#### 1. [`aws/setup_cloudfront.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_cloudfront.py)
* Walk through CDN automation and Origin Access Control (OAC):
  ```python
  # Creating SigV4 Origin Access Control
  resp = cf.create_origin_access_control(
      OriginAccessControlConfig={
          'Name': 'credit-risk-web-oac',
          'SigningProtocol': 'sigv4',
          'SigningBehavior': 'always',
          'OriginAccessControlOriginType': 's3'
      }
  )
  # Attaching S3 bucket policy allowing ONLY CloudFront OAC:
  policy = {
      "Version": "2012-10-17",
      "Statement": [{
          "Sid": "AllowCloudFrontServicePrincipalReadOnly",
          "Effect": "Allow",
          "Principal": {"Service": "cloudfront.amazonaws.com"},
          "Action": "s3:GetObject",
          "Resource": f"arn:aws:s3:::{bucket_name}/*",
          "Condition": {"StringEquals": {"AWS:SourceArn": f"arn:aws:cloudfront::{account_id}:distribution/{dist_id}"}}
      }]
  }
  ```
  *Key Concept*: Explain why OAC is superior to old OAI (Origin Access Identity)—OAC supports AWS Signature Version 4, server-side KMS encryption, and all S3 methods across all AWS regions.

#### 2. [`aws/setup_apigw.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_apigw.py)
* Walk through HTTP API Gateway creation:
  * Creating `credit-risk-api` with `AWS_PROXY` integration to Lambda ARN.
  * Adding route `GET /predict`.
  * Creating `$default` stage with `AutoDeploy=True`.
  * Invoking `lam.add_permission()` to grant API Gateway invoke rights on Lambda.

#### 3. [`credit-risk-demo.html`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/credit-risk-demo.html)
* Walk through the production UI architecture:
  * Zero-build single file HTML5/CSS3/Vanilla JS.
  * Section 01: Motivation & Cost Asymmetry explanation.
  * Section 02: System Architecture overview ([`system architecture.png`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/system%20architecture.png)).
  * Section 03: Interactive AWS Service Matrix.
  * Section 04: Live Decision Engine featuring real-time client-side ratio math, scenario presets (e.g., *Prime Homebuyer*, *Marginal Retail Borrower*, *High-Risk Speculator*), dynamic risk gauge, and fallback simulation engine.

#### 4. [`aws/iam_trust_policy.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/iam_trust_policy.json) & DynamoDB Audit Schema
* Explain the unified trust policy:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "glue.amazonaws.com",
          "sagemaker.amazonaws.com",
          "lambda.amazonaws.com",
          "states.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }]
  }
  ```
* Explain DynamoDB single-table audit item structure ([`aws/lambda_handler.py:L39-46`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/lambda_handler.py#L39-L46)):
  * `applicant_id`: UUID partition key ($O(1)$ query by applicant).
  * `timestamp`: UTC ISO string sort key (chronological decision history).
  * `inputs`: Complete serialized JSON string of submitted parameters.
  * `probability`: `Decimal(str(prob))` storing exact default risk.
  * `tier` & `decision`: Operational verdict for auditor review.

### 6.4 Slide-by-Slide Speaking Script
* **Slide 16: Content Delivery & Edge Security via CloudFront OAC**
  > *"Thank you, Person C. To deliver CreditIQ to users worldwide, we hosted our single-page application in an Amazon S3 bucket fronted by Amazon CloudFront CDN. Rather than exposing our S3 bucket publicly, we locked it down using AWS Origin Access Control with SigV4 request signing. All web traffic is encrypted under TLS 1.3, cached at edge locations, and protected from direct bucket tampering."*
* **Slide 17: Regulatory Compliance & Immutable Auditing on DynamoDB**
  > *"Under financial regulations like the Equal Credit Opportunity Act and Fair Credit Reporting Act, banks must prove exactly why an applicant was approved or rejected. In our Lambda function, before returning a verdict, every transaction is committed to an Amazon DynamoDB table. Keyed by `applicant_id` and timestamp, our audit store records the full input vector, the exact model probability, risk tier, and timestamp—persisting 1,000 out of 1,000 test requests with zero loss."*
* **Slide 18: Security Governance & CloudWatch Observability**
  > *"Security in CreditIQ adheres to strict IAM least privilege. As seen in `iam_trust_policy.json`, our services assume temporary runtime credentials using `sts:AssumeRole`—no permanent AWS access keys exist anywhere in our code. Amazon CloudWatch ingests unified log streams from Glue, SageMaker, and Lambda, monitoring API Gateway error rates and triggering automated alarms if anomalies occur."*
* **Slide 19: FinOps: Running Enterprise MLOps for $0.47**
  > *"A standout achievement of CreditIQ is its economics. As summarized in Table II of our paper, our entire evaluation workload—exploring 307,000 records in Athena, preprocessing in Glue, training, hosting serverless SageMaker endpoints, and executing 1,000 live inferences—cost a total of just $0.47 USD. Because every single service scales to zero when idle, a regional bank can run this infrastructure at essentially zero standby cost."*
* **Slide 20: Live Demonstration & Concluding Takeaways**
  > *"*(Switching to screen)* I will now demonstrate our live interface in `credit-risk-demo.html`. As we load the 'Marginal Retail Borrower' preset, the system calculates their debt-to-income and annuity ratios on the fly, passes the payload through API Gateway and Lambda to SageMaker, and returns a 38.4% default probability—correctly classified as Medium Risk for Underwriter Review and logged to DynamoDB in 73 milliseconds. In conclusion, CreditIQ proves that cost-sensitive machine learning and serverless cloud engineering can unite to deliver an auditable, enterprise-ready MLOps platform for under one dollar. Our team is now ready for questions."*

### 6.5 Viva & Committee Defense Q&A
1. **Q: Why use CloudFront with Origin Access Control (OAC) instead of just enabling S3 Static Website Hosting?**  
   *Answer*: Standard S3 website hosting requires disabling bucket block public access and making the entire bucket publicly readable over plain HTTP, exposing it to content snooping, scraping, and unauthorized bandwidth costs. CloudFront with OAC keeps the S3 bucket completely private, enforces HTTPS encryption, protects against DDoS attacks through AWS Shield standard, and caches assets globally across edge points of presence.
2. **Q: Why is DynamoDB preferred over relational Amazon RDS MySQL for audit logging?**  
   *Answer*: In lending applications, audit writes must never block or slow down user decisions. DynamoDB provides single-digit millisecond write latency (6 ms measured) with virtually infinite horizontal on-demand scaling. Its key-value document schema flexibly accommodates evolving input features without requiring costly database table schema migrations.
3. **Q: Why is the client-observed latency (284 ms) higher than the server-side latency (73 ms)?**  
   *Answer*: The server-side latency (73 ms) measures the internal AWS execution across API Gateway, Lambda, SageMaker, and DynamoDB in the `us-east-1` (North Virginia) data center. The remaining ~210 ms is the physical wide-area network (WAN) round-trip time between our client in Mumbai, India and North Virginia via transatlantic undersea fiber optic cables. Deploying in `ap-south-1` (Mumbai) would reduce total client latency to under 90 ms.

---

## 7. Master Cross-Team Transitions & Handoff Cues

To deliver a flawless, high-scoring presentation, each team member should use the following explicit verbal cues to hand over the microphone:

* **Person A $\rightarrow$ Person B**:  
  > *"Now that our data lake is established and our 192 features are clean and orchestrated, I will pass the presentation to Person B to explain our cost-sensitive machine learning models and threshold optimization."*
* **Person B $\rightarrow$ Person C**:  
  > *"With our Stacking Ensemble achieving a 0.7556 ROC-AUC and our optimal threshold established at 0.49, I will hand over to Person C to demonstrate how we containerized this model and deployed it onto an AWS serverless inference endpoint."*
* **Person C $\rightarrow$ Person D**:  
  > *"Now that our containerized SageMaker endpoint and low-latency Lambda scoring backend are live, I pass the floor to Person D to present our global edge delivery, audit compliance, cloud economics, and live platform demo."*

---

## 8. Master Summary Table

| Category | Person A | Person B | Person C | Person D |
| :--- | :--- | :--- | :--- | :--- |
| **Domain** | Data Engineering & Pipeline | Machine Learning & Optimization | Serving & Containerization | Delivery, Security & FinOps |
| **Assigned Paper Sections** | Sec I, I-A, I-B, II-A, II-B, II-C, II-F, III-A | Sec I (Math), I-A, II-D, Eq 2, II-E, IV-A, V-A | Sec II-D, III-A, IV-B, IV-C, V-B | Sec II-E, II-F, III-B, III-C, IV-D, V-C, VI, VII |
| **Assigned Codebase Files** | `athena_queries.sql`, `glue_preprocess.py`, `step_functions.json`, `01_exploration.ipynb`, `02_preprocessing.ipynb` | `03_base_models.ipynb`, `04_stacking.ipynb`, `05_threshold_optimization.ipynb`, `06_evaluation.ipynb`, `optimal_threshold.txt` | `predict_single.py`, `Dockerfile`, `serve.py`, `deploy_sagemaker.py`, `lambda_handler.py`, `predict_api.py` | `setup_cloudfront.py`, `setup_apigw.py`, `credit-risk-demo.html`, `iam_trust_policy.json`, DynamoDB & CloudWatch |
| **AWS Services Owned** | S3 Data Lake, Athena, Glue, Step Functions | Local Python / Scikit-learn / XGBoost / LightGBM | Amazon ECR, SageMaker Serverless, AWS Lambda | Amazon CloudFront (OAC), API Gateway, DynamoDB, IAM, CloudWatch |
| **Primary Metric / Value** | 307,511 rows, 9 financial ratios, 192 encoded features | ROC-AUC 0.7556, $\tau^* = 0.49$, 70.4% default recall | 73 ms server latency, 0.0 numerical drift, 3072 MB RAM | $0.47 total cost, 100% request success, 1,000 audit rows |

---

## 9. Live Demonstration Playbook (2 Minutes)

When Person D executes the live demonstration on [`credit-risk-demo.html`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/credit-risk-demo.html), follow this exact clickpath:

1. **Preset 1 (Prime Homebuyer)**:
   * Click **"Prime Homebuyer"** preset.
   * Observe: High income ($240,000), large credit ($600,000), long employment history (8 years), high credit bureau rating (`EXT_SOURCE` = 0.85).
   * Click **"Evaluate Credit Risk"**.
   * Gauge animates to **~12-15% (Low Risk - Automated Approval)**.
2. **Preset 2 (High-Risk Speculator)**:
   * Click **"High-Risk Speculator"** preset.
   * Observe: High credit-to-income ratio (credit $1,200,000 vs income $90,000), multiple social circle delinquencies, minimal employment.
   * Click **"Evaluate Credit Risk"**.
   * Gauge swings into the red to **~72-85% (High Risk - Immediate Rejection)**.
3. **Preset 3 (Marginal Retail Borrower)**:
   * Click **"Marginal Retail Borrower"** preset.
   * Observe: Moderate income, borderline credit score.
   * Click **"Evaluate Credit Risk"**.
   * Gauge lands at **~36-42% (Medium Risk - Routed for Underwriter Review)**.
   * Point out to the committee that this operational human-in-the-loop tiering directly reflects Table I and protects both bank capital and customer goodwill.
