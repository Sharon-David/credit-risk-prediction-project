# CreditIQ: Cloud Computing Presentation & Architecture Walkthrough
**An Enterprise Cloud-Native MLOps & Serverless Decision Platform on AWS**  
*Cloud Computing Course Final Presentation & 4-Person Role Division Guide*

---

## 1. Executive Summary & Cloud Team Distribution Matrix

This master document divides the cloud computing infrastructure, serverless architecture, and codebase of **CreditIQ**—as documented in the IEEE research paper ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex)) and the GitHub repository—across **four presenters (Person A, Person B, Person C, and Person D)**.

**Core Directive**: This presentation is **100% focused on Cloud Computing, Serverless Architecture, Cloud Security, Distributed Systems, and FinOps**. All heavy machine learning modeling details (such as model weights, ROC comparisons, and base learner algorithms) are treated as a pre-packaged application workload (`model.tar.gz`) hosted and served on AWS.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CREDITIQ AWS CLOUD COMPUTING ARCHITECTURE                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

   [ PERSON A: STORAGE & ANALYTICS ]            [ PERSON B: SERVERLESS ETL & ORCHESTRATION ]
   • Amazon S3 Data Lake (raw/, processed/)     • AWS Glue (Serverless Python Shell ETL)
   • Amazon Athena (Serverless SQL Analytics)   • AWS Step Functions (State Machine Orchestrator)
   • Schema-on-Read (OpenCSVSerde)              • Amazon States Language (.sync Integration)
   • S3 Storage Classes & Zero-Server EDA       • DPU Economics & Fault-Tolerant Retries
                  │                                            │
                  ▼                                            ▼
   ┌──────────────────────────────┐             ┌──────────────────────────────┐
   │ Amazon S3 Storage Prefixes   │             │ AWS Glue ETL Job             │
   │ raw/  processed/  athena/    │             │ 1 min 52 s (DPU-minutes)     │
   └──────────────┬───────────────┘             └──────────────┬───────────────┘
                  │                                            │
                  └─────────────────────┬──────────────────────┘
                                        │ Packaged as model.tar.gz into S3
                                        ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │            [ PERSON C: CLOUD CONTAINERIZATION & SERVERLESS HOSTING ]     │
   │            • Amazon Elastic Container Registry (ECR) Private Repo         │
   │            • Custom Docker Image (Python 3.13-slim + OpenMP libgomp1)     │
   │            • Amazon SageMaker Serverless Inference Endpoint (3072 MB RAM) │
   │            • Scale-to-Zero Compute Economics & Cold-Start Analysis (9.8s) │
   └────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │            [ PERSON D: API ROUTING, FAAS, AUDIT, CDN & FINOPS ]          │
   │            • Amazon API Gateway (HTTP API $default Route GET /predict)    │
   │            • AWS Lambda (Event-Driven FaaS Boto3 Orchestrator)            │
   │            • Amazon DynamoDB (NoSQL Single-Table Audit Store, 6 ms write) │
   │            • Amazon CloudFront CDN (Origin Access Control SigV4 Security) │
   │            • AWS IAM (Least Privilege Trust Policies) + Amazon CloudWatch │
   │            • FinOps Analysis: $0.47 Total Evaluation Cost & Free Tier     │
   └──────────────────────────────────────────────────────────────────────────┘
```

### Team Master Allocation Matrix

| Presenter | Cloud Domain | Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex)) | Assigned Codebase Files | AWS Services Owned & Key Cloud Metrics |
| :--- | :--- | :--- | :--- | :--- |
| **Person A** | **Storage & Serverless Analytics** | **Sec I** (Cloud MLOps Lifecycle Fig. 1), **Sec I-A/B** (Literature & Cloud Systems Gap), **Sec II-A** (160 MB Data Ingestion), **Sec II-B** (Layer 1: S3 & Athena), **Sec III-B** (Amazon S3, Amazon Athena), **Sec IV-B** (Table VI: Athena Query Benchmarks), **Sec III-C** (S3 & Athena Cost) | [`aws/athena_queries.sql`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/athena_queries.sql)<br>S3 Data Lake Architecture (`s3://credit-risk-data-aranck/`) | **Amazon S3, Amazon Athena**<br>• 11 nines durability<br>• Zero compute provisioning<br>• 158.4 MB scanned in 1.9s ($0.01 cost) |
| **Person B** | **Serverless ETL & Workflow Automation** | **Sec II-C** (Layer 2: Preprocessing in Glue), **Sec II-F** (Layer 5: Orchestration via Step Functions), **Sec III-B** (AWS Glue, AWS Step Functions), **Sec IV-B** (Table VI: Glue & Step Functions Pipeline Timings), **Sec III-C** (Glue & Step Functions Cost), **Sec V-C** (Automated Retries & Silent Failure Elimination) | [`aws/glue_preprocess.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/glue_preprocess.py)<br>[`aws/step_functions.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/step_functions.json) | **AWS Glue, AWS Step Functions**<br>• DPU-minute serverless compute<br>• 1 min 52 s ETL duration<br>• Synchronous state machine (`startJobRun.sync`) |
| **Person C** | **Cloud Containerization & Model Hosting** | **Sec II-D** (Layer 4: SageMaker Serverless Hosting & ECR), **Sec II-D** (SageMaker `/ping` and `/invocations` Contract), **Sec III-A/B** (Docker, Amazon ECR, Amazon SageMaker Serverless), **Sec IV-B** (Table VI: Endpoint Creation 4m 18s), **Sec IV-C** (Table V & VI: Compute Latency 41 ms), **Sec V-B** (Serverless Trade-Offs & Cold Start Analysis) | [`aws/sagemaker/Dockerfile`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/Dockerfile)<br>[`aws/sagemaker/serve.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/serve.py)<br>[`aws/deploy_sagemaker.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/deploy_sagemaker.py)<br>[`predict_single.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/predict_single.py) | **Amazon ECR, Amazon SageMaker Serverless**<br>• Custom Linux container (Python 3.13-slim)<br>• 3072 MB RAM, Max Concurrency = 2<br>• Scale-to-zero compute ($0 idle cost)<br>• 9.8s cold start vs 41 ms warm compute |
| **Person D** | **API Routing, FaaS, Audit, CDN & FinOps** | **Sec II-E** (Layer 4: API Routing & DynamoDB Auditing), **Sec II-F** (Layer 5: IAM Least Privilege & CloudWatch), **Sec III-B** (CloudFront OAC, API Gateway, DynamoDB, IAM, CloudWatch), **Sec III-C** (Table II: $0.47 FinOps Cost Model), **Sec IV-C** (Latency Breakdown Table V & VI), **Sec IV-D** (Operational Comparison Table VII), **Sec V-C, VI, VII** (Edge Latency, Governance, Future Scope) | [`aws/setup_apigw.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_apigw.py)<br>[`aws/setup_cloudfront.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_cloudfront.py)<br>[`aws/lambda_handler.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/lambda_handler.py)<br>[`aws/iam_trust_policy.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/iam_trust_policy.json)<br>[`credit-risk-demo.html`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/credit-risk-demo.html) | **API Gateway, Lambda, DynamoDB, CloudFront, IAM, CloudWatch**<br>• Global Edge Distribution (OAC SigV4)<br>• 73 ms total server-side latency<br>• Single-table NoSQL audit persistence<br>• Total evaluation cost: **$0.47 USD** |

---

## 2. Master Presentation Agenda & Timing (20 Minutes Total)

```
[00:00 - 05:00]  Person A: Cloud Motivation, Data Lake Architecture & Serverless SQL Analytics
[05:00 - 10:00]  Person B: Serverless ETL, Distributed Data Processing & Workflow State Machines
[10:00 - 15:00]  Person C: Cloud Containerization, Amazon ECR & SageMaker Serverless Infrastructure
[15:00 - 20:00]  Person D: Event-Driven FaaS, NoSQL Auditing, Global Edge CDN, FinOps & Live Demo
[20:00 - 25:00]  Committee Q&A & Technical Cloud Defense (All Presenters)
```

---

## 3. Person A: Storage Architecture, Serverless Data Lake & Interactive Analytics

### 3.1 Role & Cloud Mission
* **Presenter Role**: Cloud Storage Architect & Data Lake Engineer
* **Mission**: Explain the foundational role of cloud computing in financial MLOps, detail the serverless Data Lake architecture on Amazon S3, explain object storage design (keys, prefixes, durability), and demonstrate how Amazon Athena executes interactive, schema-on-read SQL analytics with zero provisioned compute clusters.

### 3.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section I: INTRODUCTION & CLOUD MLOPS LIFECYCLE (Lines 92–108)**
  * The cloud computing paradigm shift in enterprise finance: moving from monolithic always-on servers to decoupled, managed cloud services.
  * Problems with traditional servers: idle capacity during quiet hours wastes money, while sudden spikes cause hardware bottlenecks.
  * The Cloud MLOps Lifecycle: Fig. 1 ([`flowchart.png`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/system%20architecture.png)) showing managed cloud services mapped onto each phase: Storage (S3) $\rightarrow$ Ingestion & Querying (Athena) $\rightarrow$ ETL (Glue) $\rightarrow$ Orchestration (Step Functions) $\rightarrow$ Container Registry (ECR) $\rightarrow$ Serverless Compute (SageMaker + Lambda) $\rightarrow$ Gateway (API Gateway) $\rightarrow$ Edge CDN (CloudFront) $\rightarrow$ Audit Store (DynamoDB) $\rightarrow$ Observability (CloudWatch).
* **Section I-A & I-B: Literature Review & Cloud Systems Engineering Gap (Lines 109–120)**
  * Citations: Casimiro et al. (2023) on separating data ingestion from model execution in cloud-native platforms; Jiao et al. (2020) on reference architectures for cloud big data.
  * Cloud Engineering Gap: Most data science implementations rely on local, unmanaged notebooks. CreditIQ bridges the gap by implementing an enterprise, multi-service AWS architecture that scales elastically and requires zero manual infrastructure maintenance.
* **Section II-A: Data Lake Ingestion (Lines 131–133)**
  * Centralized cloud ingestion: 160 MB raw tabular dataset (`application_train.csv`) containing 307,511 applicant records and 122 attributes stored in an S3 Data Lake.
* **Section II-B: Layer 1: Data Lake and Exploratory Querying (Lines 134–136)**
  * Partitioned S3 prefix structure:
    * `s3://credit-risk-data-aranck/raw/`: Original immutable CSV records.
    * `s3://credit-risk-data-aranck/processed/`: Transformed datasets output by ETL jobs.
    * `s3://credit-risk-data-aranck/athena-results/`: Execution logs and query output buffers.
    * `s3://credit-risk-data-aranck/models/`: Serialized model artifacts (`model.tar.gz`).
  * Amazon Athena: Serverless query engine using Presto distributed SQL under the hood.
  * External table mapping using Apache Hive `OpenCSVSerde` serializer/deserializer.
* **Section III-B: AWS Service Breakdown: Amazon S3 & Amazon Athena (Lines 202–205)**
  * Amazon S3: Designed for 11 nines ($99.999999999\%$) durability, virtually infinite scalability, and direct integration with all AWS compute services without network bottlenecks.
  * Amazon Athena: Schema-on-read execution; charges $5.00 per terabyte scanned; zero idle spend; no cluster provisioning or shutdown steps.
* **Section IV-B: Table VI Pipeline Execution Summary (Lines 301–318)**
  * Athena row count query: completed in **1.9 seconds**, scanning 158.4 MB.
  * Athena class distribution query: completed in **2.3 seconds**.
* **Section III-C: Cost Analysis (Table II) (Lines 224–248)**
  * S3 storage cost: **$0.01 USD**.
  * Athena interactive query cost: **$0.01 USD**.

### 3.3 Codebase Walkthrough & File Splits
Person A must open and explain the following repository file:

#### [`aws/athena_queries.sql`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/athena_queries.sql)
* **Lines 1–18: DDL External Table Definition**:
  ```sql
  CREATE DATABASE IF NOT EXISTS credit_risk;

  CREATE EXTERNAL TABLE IF NOT EXISTS credit_risk.application_train (
    sk_id_curr string, target string, name_contract_type string, code_gender string,
    flag_own_car string, flag_own_realty string, cnt_children string, amt_income_total string,
    amt_credit string, amt_annuity string, amt_goods_price string, name_type_suite string,
    name_income_type string, name_education_type string, name_family_status string,
    name_housing_type string, region_population_relative string, days_birth string,
    days_employed string
  )
  ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
  LOCATION 's3://credit-risk-data-aranck/raw/'
  TBLPROPERTIES ('skip.header.line.count'='1');
  ```
  *Cloud Walkthrough Points*:
  1. Explain **External Table** semantics: Athena does not own the data or copy it into a proprietary database storage engine. S3 remains the authoritative source of truth. If the table is dropped, raw S3 files remain completely untouched.
  2. Explain **OpenCSVSerde**: The serializer/deserializer treats raw CSV lines as structured positional fields on the fly. No data ingestion pipelines or staging relational tables are required.
  3. Explain **S3 Location**: Athena mounts the S3 bucket URI directly. S3 transparently handles distributed parallel chunk reading across AWS internal networks.
* **Lines 19–37: Serverless Analytical Queries**:
  ```sql
  -- 1. Row count verification (307,511 rows)
  SELECT COUNT(*) AS n_rows FROM credit_risk.application_train;

  -- 2. Class imbalance distribution
  SELECT target, COUNT(*) AS n FROM credit_risk.application_train GROUP BY target;

  -- 3. Serverless missing value aggregation
  SELECT
    SUM(CASE WHEN amt_annuity = '' THEN 1 ELSE 0 END)     AS missing_annuity,
    SUM(CASE WHEN amt_goods_price = '' THEN 1 ELSE 0 END) AS missing_goods_price
  FROM credit_risk.application_train;

  -- 4. Anomaly and sentinel detection without data transfer
  SELECT target,
    AVG(CAST(amt_income_total AS double)) AS avg_income,
    SUM(CASE WHEN days_employed = '365243' THEN 1 ELSE 0 END) AS sentinel_days_employed
  FROM credit_risk.application_train GROUP BY target;
  ```
  *Cloud Walkthrough Points*:
  1. Contrast this with traditional architectures: To perform this analysis in a legacy stack, an engineer would have had to provision an Amazon EC2 instance or spin up an Amazon RDS PostgreSQL database, pay for provisioning time, wait for cluster bootup, and pay for 24/7 idle uptime.
  2. With Athena, these 4 queries scanned 158.4 MB of raw data, completed in under 2.5 seconds each, and cost less than **$0.01 USD**.

### 3.4 Slide-by-Slide Speaking Script
* **Slide 1: Cloud Architecture Overview & Paradigm Shift**
  > *"Good morning committee members. In modern cloud computing, financial institutions cannot afford the architectural liabilities of monolithic, always-on servers. Traditional VM-based architectures waste thousands of dollars during idle hours and become single points of failure under peak traffic. In CreditIQ, we engineered a 100% serverless, cloud-native architecture on AWS. I will begin by presenting our foundational storage tier: our Amazon S3 Data Lake and Amazon Athena serverless analytics engine."*
* **Slide 2: Decoupled Storage: The Amazon S3 Data Lake**
  > *"Cloud-native design dictates the complete separation of storage from compute. As shown in our architecture diagram, Amazon S3 serves as our centralized, durable data lake. We structured our bucket into logically isolated prefixes: `raw/` for immutable applicant records, `processed/` for ETL transformed data, `athena-results/` for query buffers, and `models/` for versioned application artifacts. S3 provides 11 nines of durability, high-throughput parallel object retrieval, and zero server maintenance."*
* **Slide 3: Serverless Interactive Analytics with Amazon Athena**
  > *"To inspect our 160 MB dataset containing 307,511 rows without provisioning expensive relational database instances or Spark clusters, we utilized Amazon Athena. Athena is a serverless interactive query service that operates directly on S3. Using the Apache Hive OpenCSVSerde serializer, we defined a logical schema over our raw CSV files. This is schema-on-read: the data stays in S3, and compute is allocated ephemerally only for the duration of the query."*
* **Slide 4: Query Execution Benchmarks & Cloud Efficiency**
  > *"As documented in Table VI of our research paper, our Athena row count and distribution queries executed in 1.9 and 2.3 seconds respectively, scanning 158.4 MB. Athena charges strictly $5.00 per terabyte scanned. Because our query engine scales down to zero instantly upon execution, our entire exploratory analytical workload cost exactly $0.01 USD. No databases were left running, and no CPU cycles were wasted."*
* **Slide 5: Storage-to-Compute Pipeline Handoff**
  > *"By establishing S3 as our decoupled single source of truth, any downstream cloud service can consume the data asynchronously. Now, my teammate Person B will explain how our serverless ETL service, AWS Glue, processes this data and how AWS Step Functions orchestrates the entire workflow."*

### 3.5 Viva & Committee Defense Q&A
1. **Q: Why use Amazon Athena instead of provisioning an Amazon RDS MySQL or PostgreSQL database?**  
   *Answer*: Amazon RDS requires provisioning dedicated virtual machines (EC2) and attached EBS block storage, which incur continuous 24/7 billing even when no queries are being executed. Furthermore, loading 307,000 rows into RDS requires building an ingestion pipeline and managing database connection pools. Athena is 100% serverless, requires zero instance management, queries raw files directly in S3 via schema-on-read, and costs strictly $5.00 per TB scanned, costing less than $0.01 for our entire workload.
2. **Q: What is the architectural purpose of S3 prefixes (e.g., `raw/`, `processed/`)?**  
   *Answer*: Amazon S3 is a flat object store; prefixes act as logical partitions that organize data without directory overhead. In enterprise cloud pipelines, prefix separation enforces strict security boundaries (e.g., IAM policies can restrict write access to `raw/` while granting write permissions to `processed/` for ETL roles) and enables granular S3 lifecycle rules to transition older query results in `athena-results/` to cheaper S3 Glacier storage automatically.
3. **Q: How does Hive `OpenCSVSerde` handle data types in Athena?**  
   *Answer*: `OpenCSVSerde` reads all incoming CSV fields as raw strings, preventing type-cast failures during initial file parsing. Explicit casting (e.g., `CAST(amt_income_total AS double)`) is performed dynamically at query runtime inside the SQL engine. This guarantees that malformed rows or corrupt characters do not break the entire table schema.

---

## 4. Person B: Serverless ETL, Distributed Data Processing & Workflow Orchestration

### 4.1 Role & Cloud Mission
* **Presenter Role**: Cloud Automation & Workflow Orchestration Engineer
* **Mission**: Detail the serverless ETL layer built on AWS Glue, justify the selection of Python Shell jobs over heavy Spark clusters, explain S3-to-S3 streaming data transformation, and demonstrate how AWS Step Functions orchestrates the cloud pipeline using the Amazon States Language with synchronous error handling and automatic retry policies.

### 4.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section II-C: Layer 2: Preprocessing & Data Transformation in the Cloud (Lines 137–143)**
  * AWS Glue serverless Python Shell ETL job: Triggered automatically to read raw data from S3, clean anomalous values, drop sparse columns, and write clean outputs back to the `processed/` prefix.
  * S3-to-S3 decoupled data processing: Compute never traverses a permanent server; intermediate data streams directly through memory.
* **Section II-F: Layer 5: Orchestration (AWS Step Functions) (Lines 182–184)**
  * AWS Step Functions: Serverless state machine coordinating cloud microservices.
  * Synchronous task execution using `startJobRun.sync`.
  * Deterministic error handling: Catching `States.ALL` and routing to an explicit `PipelineFailed` state to eliminate silent pipeline failures.
* **Section III-B: AWS Service Breakdown: AWS Glue & AWS Step Functions (Lines 206–207, 218–219)**
  * AWS Glue: Serverless data integration service billed on a DPU-minute (Data Processing Unit) basis. Eliminates the need to configure, tune, or maintain cluster nodes.
  * AWS Step Functions: Visual workflow orchestrator written in Amazon States Language. Replaces fragile cron jobs and unmonitored bash scripts with auditable state transitions.
* **Section IV-B: Table VI Pipeline Stage Execution Summary (Lines 301–318)**
  * AWS Glue preprocessing execution: **1 minute 52 seconds**, achieving clean S3 output.
  * AWS Step Functions state machine execution: **2 minutes 31 seconds** (including cold initialization and state transitions), completing with 100% success.
* **Section III-C: Cost Analysis (Table II) (Lines 224–248)**
  * AWS Glue DPU compute cost: **$0.03 USD**.
  * AWS Step Functions state transitions: **$0.00 USD** (Fully covered under AWS Free Tier of 4,000 monthly transitions).
* **Section V-C: Operational & Architectural Benefits (Lines 446–458)**
  * Decoupling ETL from serving: Retraining and preprocessing can run asynchronously without impacting live API availability.

### 4.3 Codebase Walkthrough & File Splits
Person B must open and explain the following repository files:

#### 1. [`aws/glue_preprocess.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/glue_preprocess.py)
* **Lines 1–24: Serverless Glue Python Shell Script**:
  ```python
  import io
  import boto3
  import numpy as np
  import pandas as pd

  s3 = boto3.client("s3")

  # Stream directly from S3 Data Lake into memory buffer
  df = pd.read_csv(s3.get_object(Bucket=BUCKET, Key="raw/application_train.csv")["Body"])

  # Serverless ETL transformation
  df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
  df["CREDIT_INCOME_RATIO"]  = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"]
  df["ANNUITY_INCOME_RATIO"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"]
  df = df.drop(columns=df.columns[df.isnull().mean() > 0.45])

  # Write back to S3 processed prefix
  buf = io.StringIO()
  df.to_csv(buf, index=False)
  s3.put_object(Bucket=BUCKET, Key="processed/application_clean.csv", Body=buf.getvalue())
  print("Done:", df.shape)
  ```
  *Cloud Walkthrough Points*:
  1. Explain **Serverless Streaming**: The script uses `boto3` to stream the S3 object body into memory without ever saving temporary files to a local hard disk.
  2. Explain **Glue Python Shell vs PySpark**: For a 160 MB dataset, provisioning an Apache Spark cluster on AWS EMR or standard AWS Glue Spark requires 2 to 5 minutes of master/worker node spin-up time and charges a minimum of 2 DPUs. Glue Python Shell provisions in under 10 seconds, runs on a fraction of a DPU (0.0625 DPU), and executes in 1 minute 52 seconds, keeping costs at $0.03.
  3. Explain **Automated Output**: The output is written directly to `s3://.../processed/application_clean.csv`, ready for model retraining or downstream analytics.

#### 2. [`aws/step_functions.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/step_functions.json)
* **Lines 1–29: Amazon States Language Definition**:
  ```json
  {
    "Comment": "CreditIQ Serverless ETL State Machine",
    "StartAt": "GluePreprocess",
    "States": {
      "GluePreprocess": {
        "Type": "Task",
        "Resource": "arn:aws:states:::glue:startJobRun.sync",
        "Parameters": {
          "JobName": "credit-risk-preprocess"
        },
        "Catch": [
          {
            "ErrorEquals": [
              "States.ALL"
            ],
            "Next": "PipelineFailed"
          }
        ],
        "Next": "Done"
      },
      "Done": {
        "Type": "Succeed"
      },
      "PipelineFailed": {
        "Type": "Fail",
        "Error": "PipelineFailed"
      }
    }
  }
  ```
  *Cloud Walkthrough Points*:
  1. Explain **Synchronous Orchestration (`startJobRun.sync`)**: Standard asynchronous job calls trigger a job and return immediately, leaving the state machine unaware of whether the job succeeded or crashed. The `.sync` integration pauses the state machine execution, continuously polling the Glue API in the background until the job reaches a terminal state.
  2. Explain **Fault Tolerance & Catch Blocks**: If the Glue job runs out of memory, hits an IAM permission exception, or fails due to corrupt input data, the `Catch` block traps `States.ALL` and transitions cleanly to `PipelineFailed`.
  3. Explain **Visual Execution History**: AWS Step Functions records every state transition with exact timestamps, input payloads, and error outputs in the AWS Console, eliminating the silent pipeline failures that plague ad-hoc cron jobs.

### 4.4 Slide-by-Slide Speaking Script
* **Slide 6: The Need for Cloud-Native ETL & Orchestration**
  > *"Thank you, Person A. Once raw data arrives in an S3 Data Lake, relying on manual Python scripts or fragile cron jobs to clean it is unacceptable in an enterprise environment. If a cron job fails silently at 2 AM, downstream production models receive stale or corrupt data. In CreditIQ, we engineered an automated, serverless ETL and workflow orchestration pipeline using AWS Glue and AWS Step Functions."*
* **Slide 7: Serverless Data Integration with AWS Glue**
  > *"To transform our raw dataset, we deployed an AWS Glue Python Shell job. Many cloud projects make the mistake of launching large Apache Spark clusters (like Amazon EMR) for moderate tabular datasets, incurring heavy node-booting overhead. Our Glue Python Shell job allocates fractional DPU capacity on demand, streams the CSV directly from S3, cleans data anomalies, computes engineered ratios, and writes the sanitized output back to S3 in just 1 minute and 52 seconds."*
* **Slide 8: Workflow Orchestration with AWS Step Functions**
  > *"To coordinate this execution deterministically, we defined an AWS Step Functions state machine using the Amazon States Language. Step Functions acts as our distributed coordinator. Rather than polling Glue manually, we utilized the synchronous `startJobRun.sync` task integration. The state machine triggers the Glue job, maintains execution state, and monitors job progress natively."*
* **Slide 9: Fault Tolerance & Error Catching**
  > *"Resilience is a core tenet of cloud architecture. As defined in our JSON state machine, our task includes a `Catch` block configured for `States.ALL`. If the ETL process encounters a corrupted record or network timeout, the state machine captures the error stack trace, halts downstream execution, and routes to an explicit `PipelineFailed` state. This guarantees zero silent failures and provides an immutable visual audit trail in CloudWatch."*
* **Slide 10: Serverless FinOps & Execution Handoff**
  > *"Our entire ETL and orchestration workflow executed in 2 minutes and 31 seconds. Step Functions cost $0.00 under the AWS Free Tier, and AWS Glue cost just $0.03 USD. With our data cleaned and stored back in S3, Person C will now demonstrate how we containerized our application and deployed it to a serverless compute endpoint on Amazon SageMaker."*

### 4.5 Viva & Committee Defense Q&A
1. **Q: Why choose AWS Glue Python Shell instead of AWS Glue Apache Spark or Amazon EMR?**  
   *Answer*: Apache Spark is designed for multi-gigabyte or terabyte distributed datasets. For our 160 MB dataset, spinning up an EMR cluster or Glue Spark job takes 3 to 5 minutes just to provision worker nodes and allocate JVM executors, with a minimum billing of 2 DPUs. Glue Python Shell boots in seconds, runs on 0.0625 DPU, completes in 1 minute 52 seconds, and costs only $0.03, optimizing both compute latency and cost.
2. **Q: How does the `.sync` suffix in `arn:aws:states:::glue:startJobRun.sync` alter Step Functions behavior?**  
   *Answer*: Without `.sync`, Step Functions initiates the Glue job asynchronously and immediately moves to the next state, even though the data is not yet cleaned. By appending `.sync`, Step Functions assumes task management responsibility: it suspends the state machine, monitors Glue job status events, and only advances to `Done` once Glue returns a `SUCCEEDED` status code.
3. **Q: What happens if an ETL job fails during execution? How does Step Functions handle it?**  
   *Answer*: The state machine's `Catch` block intercepts the failure exception via `States.ALL`. Instead of terminating abruptly or hanging indefinitely, it routes execution to the `PipelineFailed` state. This triggers an automated CloudWatch metric and can emit an Amazon SNS alert to on-call DevOps engineers while preventing bad data from overwriting production stores.

---

## 5. Person C: Cloud Containerization & Serverless Model Hosting Infrastructure

### 5.1 Role & Cloud Mission
* **Presenter Role**: Cloud Containerization & Serverless Infrastructure Engineer
* **Mission**: Detail the packaging of application workloads into Amazon Elastic Container Registry (ECR), explain Linux container optimization in Docker (`python:3.13-slim` and OpenMP `libgomp1`), demonstrate the SageMaker REST contract (`/ping` and `/invocations`), analyze Amazon SageMaker Serverless Endpoint configuration, and explain the architectural trade-offs of scale-to-zero compute versus cold starts.

### 5.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section II-D: Layer 4: Model Hosting (Amazon SageMaker) (Lines 154–156)**
  * Packaging application artifacts into `model.tar.gz` and uploading to Amazon S3.
  * Registering the container image in Amazon Elastic Container Registry (ECR).
  * Amazon SageMaker Serverless Inference endpoint: Provisioning compute on demand with automatic scale-to-zero capability.
  * Memory allocation: Configured for **3072 MB** memory and **MaxConcurrency = 2**.
  * The SageMaker HTTP Contract: Implementing `/ping` for endpoint health probes and `/invocations` for real-time inference requests.
* **Section III-A & III-B: Cloud Technology Stack: Docker, ECR & SageMaker (Lines 188–208)**
  * Docker: Standardizing application dependencies to eliminate "works on my machine" issues across cloud environments.
  * Amazon ECR: Fully managed private container registry providing secure image storage, vulnerability scanning, and high-speed VPC image pulls.
  * Amazon SageMaker Serverless: Eliminates the requirement to manage EC2 instances or autoscaling groups; charges strictly for compute seconds utilized per request.
* **Section IV-B: Table VI Pipeline Execution Summary (Lines 301–318)**
  * SageMaker serverless endpoint provisioning: completed in **4 minutes 18 seconds**, transitioning to `InService`.
* **Section IV-C: Latency & Compute Breakdown (Tables V & VI) (Lines 320–362)**
  * Median server-side compute breakdown:
    * SageMaker internal endpoint overhead: **11 ms**
    * In-container application execution: **41 ms**
    * Total server-side response: **73 ms**
* **Section V-B: Discussion: Serverless Trade-Offs & Cold Start Analysis (Lines 429–445)**
  * The Serverless Cold Start: An average of **9.8 seconds** across 10 cold invocations while AWS provisions the container environment and loads artifacts into RAM.
  * Contrast with warm requests: Once initialized, subsequent requests execute in a median of **73 ms**.
  * Scale-to-zero economics: The 9.8-second initial latency is easily tolerated within API Gateway's 29-second timeout limit, saving hundreds of dollars per year compared to always-on provisioned EC2 instances.
* **Section III-C: Cost Analysis (Table II) (Lines 224–248)**
  * SageMaker Serverless compute cost: **$0.38 USD** for 1,000 evaluations.
  * Amazon ECR private repository storage: **$0.04 USD**.

### 5.3 Codebase Walkthrough & File Splits
Person C must open and explain the following repository files:

#### 1. [`aws/sagemaker/Dockerfile`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/Dockerfile)
* **Lines 1–11: Optimized Container Image Definition**:
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
  *Cloud Walkthrough Points*:
  1. Explain **Base Image Selection (`python:3.13-slim`)**: Rather than using bloated standard images (1.5+ GB), `slim` minimizes the attack surface and reduces image pull latency across AWS networks.
  2. Explain **OpenMP (`libgomp1`)**: High-performance multi-threaded compute libraries in Linux require OpenMP. Without `libgomp1`, compiled C++ inference backends crash on container startup.
  3. Explain **Layer Pruning**: Removing cached package archives (`rm -rf /var/lib/apt/lists/*`) and uninstalling unnecessary CUDA GPU libraries (`pip uninstall -y nvidia-nccl-cu12`) shrinks the final container image to ~400 MB, speeding up serverless container provisioning.

#### 2. [`aws/sagemaker/serve.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/sagemaker/serve.py)
* **Lines 1–23: SageMaker Container HTTP Contract**:
  ```python
  import os
  import json
  os.chdir("/opt/ml/model")

  from flask import Flask, request
  import predict_single

  app = Flask(__name__)

  @app.get("/ping")
  def ping():
      return "", 200

  @app.post("/invocations")
  def invocations():
      result = predict_single.predict(request.get_json(force=True))
      return json.dumps(result), 200, {"Content-Type": "application/json"}

  app.run(host="0.0.0.0", port=8080)
  ```
  *Cloud Walkthrough Points*:
  1. Explain **SageMaker Filesystem Standard (`/opt/ml/model`)**: When SageMaker initializes an endpoint, it downloads `model.tar.gz` from S3 and extracts it into `/opt/ml/model`. The script sets its working directory here so serialized models load via native relative paths.
  2. Explain **The `/ping` Health Probe**: SageMaker's internal load balancer polls `GET /ping` on port 8080. The endpoint only transitions to `InService` once the container returns HTTP 200.
  3. Explain **The `/invocations` Route**: Handles incoming prediction payloads forwarded by AWS Lambda, deserializing JSON, executing inference, and returning JSON responses.

#### 3. [`aws/deploy_sagemaker.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/deploy_sagemaker.py)
* **Lines 1–44: Infrastructure-as-Code Deployment**:
  ```python
  # 1. Package model artifacts and upload to S3 Data Lake
  with tarfile.open("model.tar.gz", "w:gz") as tar:
      tar.add("models/stacked/stacked_model.pkl", arcname="models/stacked/stacked_model.pkl")
      tar.add("models/preprocessor.pkl", arcname="models/preprocessor.pkl")
  boto3.client("s3").upload_file("model.tar.gz", BUCKET, "models/model.tar.gz")

  # 2. Register SageMaker Model with ECR image & S3 artifact
  sm.create_model(
      ModelName=name,
      ExecutionRoleArn=role_arn,
      PrimaryContainer={"Image": image_uri, "ModelDataUrl": f"s3://{BUCKET}/models/model.tar.gz"},
  )

  # 3. Configure Serverless Endpoint (3072 MB RAM, MaxConcurrency 2)
  sm.create_endpoint_config(
      EndpointConfigName=name,
      ProductionVariants=[{
          "VariantName": "AllTraffic",
          "ModelName": name,
          "ServerlessConfig": {"MemorySizeInMB": 3072, "MaxConcurrency": 2},
      }],
  )

  # 4. Create or update the live endpoint
  sm.create_endpoint(EndpointName=endpoint, EndpointConfigName=name)
  ```
  *Cloud Walkthrough Points*:
  1. Explain **Automated Provisioning**: The entire deployment is defined programmatically via Boto3, replacing error-prone manual AWS Console clicks.
  2. Explain **`ServerlessConfig`**: We allocate 3072 MB of ephemeral RAM. Memory allocation in serverless compute directly dictates the vCPU proportion assigned to the container, optimizing scoring execution down to 41 ms.

### 5.4 Slide-by-Slide Speaking Script
* **Slide 11: The Cloud Hosting Dilemma**
  > *"Thank you, Person B. In traditional cloud architectures, hosting a microservice requires provisioning an Amazon EC2 instance or an Amazon EKS Kubernetes cluster. An `m5.large` instance runs 24 hours a day, 7 days a week—costing upwards of $70 per month even if zero requests arrive on weekends. In CreditIQ, we eliminated idle compute spend entirely by architecting a serverless container hosting solution on Amazon SageMaker."*
* **Slide 12: Custom Linux Containerization via Amazon ECR**
  > *"Pre-built cloud machine learning containers often suffer from bloat and dependency mismatch. To achieve full control, we authored a custom Docker container based on `python:3.13-slim`. We installed the Linux OpenMP library `libgomp1` for multi-threaded CPU parallelization, stripped unused GPU drivers, and implemented SageMaker's standard `/ping` and `/invocations` REST contract in Flask. We pushed our image to a private Amazon Elastic Container Registry (ECR) repository."*
* **Slide 13: Amazon SageMaker Serverless Inference**
  > *"Using our Infrastructure-as-Code script in `deploy_sagemaker.py`, we created a SageMaker Serverless Endpoint configured with 3072 MB of memory and a maximum concurrency of 2. Unlike provisioned endpoints, serverless endpoints scale dynamically to zero when no loan applications are being processed. AWS charges us strictly for the compute duration used during active requests, measured down to the millisecond."*
* **Slide 14: Serverless Cold Start Analysis & Trade-Offs**
  > *"A fundamental concept in cloud computing is the serverless cold start. As evaluated in Section V-B of our paper, when our endpoint is called after an idle period, AWS provisions a micro-VM, pulls the container, and loads artifacts into memory—incurring a 9.8-second cold start. In retail banking, a 10-second wait on an initial morning application is well within API Gateway's 29-second timeout. Once warm, all subsequent requests execute in just 41 milliseconds of compute time."*
* **Slide 15: Compute Efficiency & Gateway Handoff**
  > *"Across 1,000 warm evaluation requests, SageMaker added just 11 ms of internal routing overhead and cost only $0.38 USD. With our containerized compute engine deployed and running, Person D will now explain how we route traffic securely from the global edge using API Gateway, Lambda, CloudFront, and DynamoDB."*

### 5.5 Viva & Committee Defense Q&A
1. **Q: Why use Amazon SageMaker Serverless Inference instead of deploying the container on AWS Fargate or an EC2 instance?**  
   *Answer*: EC2 instances require paying for 24/7 compute regardless of incoming traffic, resulting in high idle costs. AWS Fargate still requires managing an Application Load Balancer ($16/month baseline) and configuring autoscaling rules with minimum task counts. SageMaker Serverless Inference scales to true zero with zero infrastructure management, provides built-in TLS endpoints, and charges strictly per millisecond of compute used during inference.
2. **Q: How does memory allocation in SageMaker Serverless impact compute performance?**  
   *Answer*: In AWS serverless architectures (both Lambda and SageMaker Serverless), vCPU allocation scales proportionally with configured memory. Allocating 3072 MB gives our container dedicated virtual CPU threads, allowing multi-threaded C++ libraries in LightGBM and scikit-learn to execute in parallel, reducing model inference time to 41 ms.
3. **Q: How can a bank eliminate the 9.8-second cold start during peak business hours?**  
   *Answer*: SageMaker Serverless supports provisioned concurrency, which maintains a pre-warmed pool of container instances during scheduled business hours (e.g., 9 AM to 5 PM). Alternatively, a simple CloudWatch Event Rule can trigger a scheduled warm-up ping every 5 minutes to keep the container active in memory.

---

## 6. Person D: Serverless API Routing, Database Auditing, Edge CDN & Cloud FinOps

### 6.1 Role & Cloud Mission
* **Presenter Role**: Cloud Architect, Security, Compliance & FinOps Lead
* **Mission**: Detail the event-driven FaaS layer in AWS Lambda, explain low-latency API Gateway HTTP API routing, demonstrate immutable compliance auditing on Amazon DynamoDB, present edge delivery via Amazon CloudFront with Origin Access Control (OAC), walk through IAM security and CloudWatch observability, and deliver the final FinOps cost analysis and live platform demonstration.

### 6.2 Assigned Paper Sections ([`reference.tex`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/reference.tex))
* **Section II-E: Layer 4: API Routing & Auditing (Lines 179–181)**
  * Amazon API Gateway HTTP API: Low-latency `$default` auto-deploy route handling `GET /predict`.
  * AWS Lambda: Lightweight serverless event handler connecting API Gateway, SageMaker, and DynamoDB.
  * Amazon DynamoDB Single-Table Audit Store: Partition Key `applicant_id` (UUID), Sort Key `timestamp` (UTC ISO-8601).
  * Persisting raw inputs, computed default probability, risk tier, and operational decision to fulfill FCRA (Fair Credit Reporting Act) and ECOA regulatory audit compliance.
* **Section II-F: Layer 5: Security Governance & Observability (Lines 182–184)**
  * AWS IAM Least Privilege: `sts:AssumeRole` trust policy granting ephemeral execution permissions to Glue, SageMaker, Lambda, and Step Functions. Zero long-lived AWS secret keys hardcoded in code.
  * Amazon CloudWatch: Centralized log groups (`/aws/lambda/...`, `/aws/sagemaker/...`), API Gateway latency metrics, Lambda invocation error alarms.
* **Section III-B: CloudFront CDN with Origin Access Control (Lines 212–215)**
  * Amazon CloudFront CDN: Distributing the single-page application ([`credit-risk-demo.html`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/credit-risk-demo.html)) globally across edge locations over HTTPS.
  * Origin Access Control (OAC SigV4): Keeping the hosting S3 bucket 100% private, preventing direct public S3 bucket exposure.
* **Section IV-C: Tables V & VI: Server-Side Latency Breakdown (Lines 320–362)**
  * End-to-end server-side execution across AWS components:
    * API Gateway routing: **6 ms**
    * Lambda execution overhead: **9 ms**
    * SageMaker endpoint overhead: **11 ms**
    * In-container scoring: **41 ms**
    * DynamoDB PutItem audit write: **6 ms**
    * **Total Server-Side Median Latency: 73 ms**
  * Client-observed latency analysis: 284 ms median due to physical transatlantic WAN round-trip from Mumbai to `us-east-1` (North Virginia).
* **Section IV-D: Operational Reliability & Scalability (Table VII) (Lines 363–386)**
  * 100% request success rate over 1,000 warm requests.
  * Sustained throughput of **21.4 requests/second** under concurrency limit 2.
  * Exactly 1,000 out of 1,000 audit records persisted to DynamoDB.
* **Section III-C: Table II: Cloud FinOps & Cost Analysis (Lines 224–248)**
  * S3: $0.01 | Athena: $0.01 | Glue: $0.03 | SageMaker: $0.38 | ECR: $0.04
  * Lambda, API Gateway, DynamoDB, CloudFront, Step Functions, CloudWatch: **$0.00** (Free Tier)
  * **Total Evaluation Cost: $0.47 USD**
* **Section V-C, VI & VII: Operational Benefits, Future Scope & Conclusion (Lines 446–475)**
  * Multi-region active-active deployment (`ap-south-1` + `us-east-1`) to cut WAN latency.
  * Amazon Cognito OAuth2 JWT authentication and AWS KMS customer-managed key encryption.

### 6.3 Codebase Walkthrough & File Splits
Person D must open and explain the following repository files:

#### 1. [`aws/lambda_handler.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/lambda_handler.py)
* **Lines 1–53: Event-Driven FaaS Orchestrator**:
  ```python
  import json, uuid, datetime
  from decimal import Decimal
  import boto3

  sm = boto3.client("sagemaker-runtime")
  table = boto3.resource("dynamodb").Table("credit-risk-audit")

  def handler(event, context):
      q = event.get("queryStringParameters") or {}
      inputs = {NUM[k]: float(v) for k, v in q.items() if k in NUM}
      inputs.update({STR[k]: v for k, v in q.items() if k in STR})

      # 1. Invoke SageMaker Serverless Endpoint via Boto3
      resp = sm.invoke_endpoint(
          EndpointName="credit-risk-endpoint",
          ContentType="application/json",
          Body=json.dumps(inputs)
      )
      result = json.loads(resp["Body"].read())

      # 2. Asynchronous Immutable Audit Write to DynamoDB
      table.put_item(Item={
          "applicant_id": q.get("applicant_id", str(uuid.uuid4())),
          "timestamp": datetime.datetime.utcnow().isoformat(),
          "inputs": json.dumps(inputs),
          "probability": Decimal(str(result.get("probability", -1))),
          "tier": result.get("tier", "error"),
          "decision": result.get("decision", result.get("error", "")),
      })

      # 3. Return CORS-Compliant JSON Response
      return {
          "statusCode": 200,
          "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
          "body": json.dumps(result),
      }
  ```
  *Cloud Walkthrough Points*:
  1. Explain **Thin FaaS Architecture**: Lambda does not load heavy ML libraries or models into memory, keeping the deployment package tiny (<5 KB) and execution duration under 9 ms.
  2. Explain **Decimal Conversion for DynamoDB**: DynamoDB does not support standard IEEE floating point types; Lambda converts float probabilities to Python `Decimal` to ensure exact financial precision.
  3. Explain **CORS Headers**: Injects `Access-Control-Allow-Origin: *` to enable cross-origin browser requests from CloudFront.

#### 2. [`aws/setup_apigw.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_apigw.py)
* **Lines 1–68: HTTP API Gateway Automation**:
  * Creates HTTP API `credit-risk-api` (6 ms routing overhead vs 30+ ms in legacy REST APIs).
  * Creates `AWS_PROXY` integration to Lambda ARN with Payload Format Version 2.0.
  * Adds route `GET /predict` on `$default` stage with `AutoDeploy=True`.
  * Grants Lambda invoke permissions via `lam.add_permission()` using Principal `apigateway.amazonaws.com`.

#### 3. [`aws/setup_cloudfront.py`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/setup_cloudfront.py)
* **Lines 1–100: CloudFront CDN & Origin Access Control (OAC)**:
  ```python
  # Create SigV4 Origin Access Control
  resp = cf.create_origin_access_control(
      OriginAccessControlConfig={
          'Name': 'credit-risk-web-oac',
          'SigningProtocol': 'sigv4',
          'SigningBehavior': 'always',
          'OriginAccessControlOriginType': 's3'
      }
  )
  # Lock S3 Bucket Policy to CloudFront Service Principal ONLY
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
  *Cloud Walkthrough Points*:
  1. Explain **Origin Access Control (OAC)**: The S3 bucket has Block Public Access 100% enabled. Direct HTTP requests to S3 are denied. Only CloudFront edge servers possessing signed SigV4 headers can fetch the web application.

#### 4. [`aws/iam_trust_policy.json`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/aws/iam_trust_policy.json)
* Explain the centralized `sts:AssumeRole` trust policy:
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
  *Cloud Walkthrough Points*: Zero hardcoded access keys. Services assume IAM roles ephemerally with short-lived STS tokens.

### 6.4 Slide-by-Slide Speaking Script
* **Slide 16: Event-Driven Serverless Compute with AWS Lambda**
  > *"Thank you, Person C. In our serving path, we deployed a serverless compute layer using AWS Lambda behind an Amazon API Gateway HTTP API. HTTP API is AWS's modern, lightweight gateway variant that cuts routing latency to just 6 milliseconds. When an applicant submits a loan request, API Gateway triggers our Lambda function, which extracts parameters, invokes the SageMaker Serverless endpoint, logs the transaction to DynamoDB, and returns a CORS-compliant response in just 9 ms."*
* **Slide 17: Regulatory Audit Logging on Amazon DynamoDB**
  > *"Banking regulations such as FCRA and ECOA require lenders to provide an unalterable audit trail explaining every credit decision. We implemented a single-table NoSQL audit store on Amazon DynamoDB using on-demand capacity. Keyed by `applicant_id` as partition key and a UTC ISO timestamp as sort key, DynamoDB commits the full input vector, default probability, risk tier, and final verdict in an average write time of just 6 milliseconds, persisting 1,000 out of 1,000 test transactions with zero loss."*
* **Slide 18: Global Edge Delivery & S3 Origin Access Control**
  > *"To serve our web client globally, we hosted our single-page application in an S3 bucket distributed by Amazon CloudFront CDN. Many cloud projects leave S3 buckets publicly readable, creating severe security vulnerabilities. In `setup_cloudfront.py`, we implemented AWS Origin Access Control with SigV4 signing. Our S3 bucket blocks all public access; only CloudFront edge servers can retrieve the files over encrypted TLS 1.3, providing global edge caching and automated DDoS protection via AWS Shield."*
* **Slide 19: Security Governance & CloudWatch Observability**
  > *"Security across CreditIQ follows strict IAM least privilege. As defined in `iam_trust_policy.json`, our services assume temporary runtime credentials using `sts:AssumeRole`—no permanent access keys or secrets exist anywhere in our code. Amazon CloudWatch aggregates unified log streams from Glue, SageMaker, and Lambda, monitoring API Gateway error rates and triggering automated alarms on anomalous Lambda execution failures."*
* **Slide 20: FinOps Economics & Live Demonstration**
  > *"*(Switching to screen)* Finally, we examine the economics of CreditIQ. As shown in Table II, our entire evaluation workload—including S3 data lake storage, Athena querying, Glue ETL, SageMaker serverless compute, and 1,000 live API transactions—cost a grand total of just **$0.47 USD**. Because every single component scales to zero when idle, standby costs are exactly $0.00. I will now demonstrate our live interface in `credit-risk-demo.html`: submitting a request routes across CloudFront, API Gateway, Lambda, and SageMaker, returning our operational decision and logging to DynamoDB in 73 ms. CreditIQ demonstrates that serverless cloud computing can deliver enterprise-grade scalability, auditability, and security for under fifty cents. Our team is now ready for your questions."*

### 6.5 Viva & Committee Defense Q&A
1. **Q: Why use API Gateway HTTP API instead of API Gateway REST API?**  
   *Answer*: API Gateway HTTP APIs are purpose-built for low-latency, serverless proxy routing. They deliver up to a 60% reduction in latency (6 ms median vs 30+ ms in REST API) and are 71% cheaper ($1.00 per million calls vs $3.50 in REST APIs) while supporting native OpenID Connect/OAuth2 authentication and automatic CORS handling.
2. **Q: Why use Origin Access Control (OAC) instead of the older Origin Access Identity (OAI)?**  
   *Answer*: OAI is a legacy mechanism that does not support AWS Signature Version 4 (SigV4), does not support KMS server-side encryption, and does not work in newer AWS regions. OAC supports SigV4 signing, provides granular IAM policy support with AWS service principals, and ensures all traffic between CloudFront and S3 is cryptographically signed and authenticated.
3. **Q: Why is DynamoDB single-table design superior to Amazon RDS PostgreSQL for this audit logging workload?**  
   *Answer*: In loan processing, audit persistence is in the critical serving path. RDS MySQL or PostgreSQL requires maintaining connection pools, managing schema migrations, and handling disk storage limits. DynamoDB provides single-digit millisecond write latency (6 ms measured), handles infinite on-demand write scaling, and stores schema-flexible JSON payloads without requiring schema migration scripts.

---

## 7. Master Cross-Team Transitions & Handoff Cues

To demonstrate seamless team cohesion during the presentation, use these verbal handoff cues:

* **Person A $\rightarrow$ Person B**:  
  > *"Now that our S3 Data Lake is established and our serverless Athena exploration is verified, I pass the floor to Person B to explain our automated ETL pipeline in AWS Glue and workflow orchestration in AWS Step Functions."*
* **Person B $\rightarrow$ Person C**:  
  > *"With our data cleaned, transformed, and orchestrated with zero silent failures, I hand over to Person C to demonstrate how we packaged our application into Amazon ECR and deployed a serverless inference endpoint on Amazon SageMaker."*
* **Person C $\rightarrow$ Person D**:  
  > *"Now that our serverless container endpoint is deployed with scale-to-zero compute, I pass the floor to Person D to present our API Gateway routing, DynamoDB auditing, CloudFront edge delivery, FinOps cost analysis, and live system demonstration."*

---

## 8. Master Cloud Computing Comparison Table

| Dimension | Person A: Storage & Analytics | Person B: Serverless ETL & Orchestration | Person C: Containerization & Hosting | Person D: FaaS, Audit, CDN & FinOps |
| :--- | :--- | :--- | :--- | :--- |
| **AWS Services** | Amazon S3, Amazon Athena | AWS Glue, AWS Step Functions | Amazon ECR, SageMaker Serverless | API Gateway, Lambda, DynamoDB, CloudFront, IAM, CloudWatch |
| **Cloud Computing Model** | Decoupled Object Storage & Schema-on-Read SQL | Serverless ETL & State Machine Orchestrator | Container Registry & Serverless Inference Compute | Event-Driven FaaS, NoSQL Key-Value, Global CDN Edge |
| **Assigned Codebase Files** | `athena_queries.sql`, S3 Data Lake layout | `glue_preprocess.py`, `step_functions.json` | `Dockerfile`, `serve.py`, `deploy_sagemaker.py`, `predict_single.py` | `setup_apigw.py`, `setup_cloudfront.py`, `lambda_handler.py`, `iam_trust_policy.json`, `credit-risk-demo.html` |
| **Execution Model** | Ephemeral queries billed per TB scanned | DPU-minute compute with synchronous state transition | Scale-to-zero container instance (3072 MB RAM) | Millisecond micro-billing with global edge caching |
| **Key Performance Metric** | 158.4 MB scanned in 1.9s ($0.01 cost) | 1 min 52 s ETL duration, 100% state machine success | 41 ms compute time, 9.8s cold start, 0.0 drift | 73 ms server-side latency, 1,000/1,000 audit persistence |
| **FinOps Evaluation Cost** | $0.02 USD (S3 + Athena) | $0.03 USD (Glue + Step Functions) | $0.42 USD (SageMaker + ECR) | $0.00 USD (Covered under AWS Free Tier) |

---

## 9. Live Cloud Architecture Demonstration (2 Minutes)

When Person D presents the live system using [`credit-risk-demo.html`](file:///c:/Users/asus/Documents/Repositories/credit-risk-prediction-project/credit-risk-demo.html), follow this exact technical narrative:

1. **Edge Request via CloudFront CDN**:
   * Open the browser and show the address bar loading over secure HTTPS via CloudFront edge distribution.
   * Highlight that the underlying S3 bucket is completely private via Origin Access Control (SigV4).
2. **API Gateway & Lambda Invocation**:
   * Select the **"Marginal Retail Borrower"** scenario preset.
   * Click **"Evaluate Credit Risk"**.
   * Show that the browser fires a `GET /predict` HTTPS call to API Gateway, which invokes AWS Lambda with query parameters.
3. **SageMaker Container Compute**:
   * Point out the returned server-side response: SageMaker executed the in-container scoring in 41 ms, returning a default probability of ~38.4% (Medium Risk / Underwriter Review).
4. **DynamoDB Audit Persistence**:
   * Explain that before Lambda returned the HTTP 200 response, it committed a permanent audit record into DynamoDB containing the applicant UUID, full parameters, probability, and timestamp in 6 ms.
5. **Total Measured Server-Side Latency**:
   * Point to the benchmark: **73 ms** total server-side round trip across 4 managed cloud services, costing a fraction of a cent per invocation.
