-- Athena exploration (bare minimum). Replace <BUCKET> with your bucket name.
-- raw/ must contain only application_train.csv.
-- OpenCSVSerde maps columns by position, so only the first 19 columns of the CSV are declared.

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
LOCATION 's3://credit-risk-web-aranck/raw/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- 1. Row count
SELECT COUNT(*) AS n_rows FROM credit_risk.application_train;

-- 2. Class imbalance
SELECT target, COUNT(*) AS n FROM credit_risk.application_train GROUP BY target;

-- 3. Missing values (empty strings in CSV)
SELECT
  SUM(CASE WHEN amt_annuity = '' THEN 1 ELSE 0 END)     AS missing_annuity,
  SUM(CASE WHEN amt_goods_price = '' THEN 1 ELSE 0 END) AS missing_goods_price,
  SUM(CASE WHEN name_type_suite = '' THEN 1 ELSE 0 END) AS missing_type_suite
FROM credit_risk.application_train;

-- 4. Average income / credit by target, plus the 365243 DAYS_EMPLOYED sentinel count
SELECT target,
  AVG(CAST(amt_income_total AS double)) AS avg_income,
  AVG(CAST(amt_credit AS double))       AS avg_credit,
  SUM(CASE WHEN days_employed = '365243' THEN 1 ELSE 0 END) AS sentinel_days_employed
FROM credit_risk.application_train GROUP BY target;
