# Glue Python Shell job (demo only): light cleaning of the raw CSV, writes processed/application_clean.csv.
# The hosted model + preprocessor are the existing ones from this repo; this job does not feed them.
BUCKET = "credit-risk-data-aranck"   # <-- CHANGE THIS to your bucket name

import io
import boto3
import numpy as np
import pandas as pd

s3 = boto3.client("s3")

df = pd.read_csv(s3.get_object(Bucket=BUCKET, Key="raw/application_train.csv")["Body"])

# Same basic cleaning as notebook 02: fix the 365243 sentinel, add 2 ratio features, drop >45%-missing columns
df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
df["CREDIT_INCOME_RATIO"]  = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"]
df["ANNUITY_INCOME_RATIO"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"]
df = df.drop(columns=df.columns[df.isnull().mean() > 0.45])

buf = io.StringIO()
df.to_csv(buf, index=False)
s3.put_object(Bucket=BUCKET, Key="processed/application_clean.csv", Body=buf.getvalue())
print("Done:", df.shape)
