# Glue Python Shell job: notebook 02 logic, condensed. Writes processed splits to s3://<BUCKET>/processed/.
# Does NOT touch models/ (the hosted model + preprocessor are the existing ones from this repo).
BUCKET = "credit-risk-yourname"   # <-- CHANGE THIS to your bucket name

import io
import boto3
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

s3 = boto3.client("s3")

def write_csv(df, key):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())

df = pd.read_csv(s3.get_object(Bucket=BUCKET, Key="raw/application_train.csv")["Body"])

# 40% stratified sample
df, _ = train_test_split(df, train_size=0.40, random_state=42, stratify=df["TARGET"])

# Cleaning + 9 engineered features
df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
df["CREDIT_INCOME_RATIO"]   = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"]
df["ANNUITY_INCOME_RATIO"]  = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"]
df["EMPLOYED_AGE_RATIO"]    = df["DAYS_EMPLOYED"] / df["DAYS_BIRTH"]
df["CREDIT_DURATION_RATIO"] = df["AMT_CREDIT"] / df["AMT_ANNUITY"].replace(0, np.nan)
df["GOODS_CREDIT_RATIO"]    = df["AMT_GOODS_PRICE"] / df["AMT_CREDIT"].replace(0, np.nan)
df["AGE_YEARS"]             = (-df["DAYS_BIRTH"] / 365).round(1)
df["YEARS_EMPLOYED"]        = (-df["DAYS_EMPLOYED"] / 365).round(1)
df["INCOME_PER_PERSON"]     = df["AMT_INCOME_TOTAL"] / df["CNT_FAM_MEMBERS"].replace(0, np.nan)
df["DOC_COUNT"]             = df.filter(like="FLAG_DOCUMENT_").sum(axis=1)

# Drop ID + columns with >45% missing
df = df.drop(columns=["SK_ID_CURR"] + df.columns[df.isnull().mean() > 0.45].tolist())

X = df.drop("TARGET", axis=1)
y = df["TARGET"]
num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
cat_cols = X.select_dtypes(include=["object"]).columns.tolist()

preprocessor = ColumnTransformer([
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), num_cols),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
], remainder="drop", sparse_threshold=0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)
X_train_proc = preprocessor.fit_transform(X_train)
X_test_proc = preprocessor.transform(X_test)

write_csv(pd.DataFrame(X_train_proc), "processed/X_train.csv")
write_csv(pd.DataFrame(X_test_proc), "processed/X_test.csv")
write_csv(y_train.to_frame(), "processed/y_train.csv")
write_csv(y_test.to_frame(), "processed/y_test.csv")
print("Done:", X_train_proc.shape, X_test_proc.shape)
