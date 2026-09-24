# Credit Risk Prediction Project

A machine-learning system that predicts the probability that a loan applicant will
default, based on the [Home Credit Default Risk](https://www.kaggle.com/c/home-credit-default-risk)
style dataset (`application_train.csv`). The project trains several base classifiers,
combines them into a stacked ensemble, picks a cost-optimal decision threshold, and
serves the final model through a small FastAPI backend with an HTML/JS demo front end.

## What it does

Given an applicant's financial and demographic details (income, credit amount,
employment history, external bureau scores, family situation, etc.), the system
outputs:

- A **probability of default** (0–1).
- A **decision**: `Approve (Low Risk)`, `Review (Medium Risk)`, or `Reject (High Risk)`.
- A **risk tier**: `low`, `medium`, or `high`.

## Architecture

The project is organized as a linear ML pipeline (implemented as Jupyter notebooks)
that produces artifacts consumed by a lightweight prediction API:

```
data/raw/application_train.csv
        │
        ▼
01_data_exploration.ipynb      (EDA: shape, missingness, target imbalance, distributions)
        │
        ▼
02_preprocessing.ipynb          (sampling, cleaning, feature engineering, train/test split,
        │                        ColumnTransformer fit → preprocessor.pkl)
        ▼
03_base_models.ipynb            (trains 5 base classifiers, saves each + ROC plot)
        │
        ▼
04_stacking.ipynb               (StackingClassifier over the base models → stacked_model.pkl)
        │
        ▼
05_threshold_optimization.ipynb (cost-based search for the decision threshold that
        │                        minimizes business cost → optimal_threshold.txt)
        ▼
06_evaluation.ipynb             (final metrics, confusion matrix, ROC comparison plots)

        │
        ▼
predict_single.py   ── loads stacked_model.pkl + preprocessor.pkl, rebuilds engineered
                        features from raw input, returns probability/decision/tier
        │
        ▼
predict_api.py       ── FastAPI app; GET /predict shells out to predict_single.py,
                         GET / serves credit-risk-demo.html
        │
        ▼
credit-risk-demo.html ── static single-page form UI that calls the API and renders
                          the risk verdict
```

### Directory layout

```
├── notebooks/                  # The actual ML pipeline (see above)
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_base_models.ipynb
│   ├── 04_stacking.ipynb
│   ├── 05_threshold_optimization.ipynb
│   ├── 06_evaluation.ipynb
│   ├── base_probabilities.csv       # test-set probs from each base model
│   ├── stacked_probabilities.csv    # test-set probs from the stacked ensemble
│   └── optimal_threshold.txt        # cost-optimized threshold (currently ≈0.49)
├── data/                        # NOT checked in (see .gitignore) — raw/processed CSVs
├── models/                      # NOT checked in — preprocessor.pkl, base/*.pkl,
│                                  stacked/stacked_model.pkl, feature_columns.json
├── reports/figures/             # Saved PNG charts (ROC curves, cost curve, confusion matrix)
├── src/                         # Placeholder module scaffolding (see "Known issues")
│   ├── __init__.py
│   ├── main.py
│   ├── data_preprocessing.py
│   ├── model_training.py
│   ├── threshold_optimizer.py
│   └── evaluation.py
├── predict_single.py            # CLI/importable single-record prediction
├── predict_api.py               # FastAPI web server
├── credit-risk-demo.html        # Front-end demo UI ("CreditIQ")
└── requirements.txt
```

## Machine learning pipeline (detail)

**1. Data exploration** (`01_data_exploration.ipynb`)
Loads `application_train.csv`, inspects shape/dtypes/missingness, plots the (highly
imbalanced) `TARGET` distribution, income distribution, and credit amount by target.

**2. Preprocessing & feature engineering** (`02_preprocessing.ipynb`)
- Samples 40% of the data (stratified by `TARGET`) for tractability.
- Replaces the sentinel value `365243` in `DAYS_EMPLOYED` with `NaN`.
- Engineers 9 new features: `CREDIT_INCOME_RATIO`, `ANNUITY_INCOME_RATIO`,
  `EMPLOYED_AGE_RATIO`, `CREDIT_DURATION_RATIO`, `GOODS_CREDIT_RATIO`, `AGE_YEARS`,
  `YEARS_EMPLOYED`, `INCOME_PER_PERSON`, `DOC_COUNT`.
- Drops `SK_ID_CURR` and any column with >45% missing values.
- Builds a `ColumnTransformer`: numeric columns → median-impute + standard-scale;
  categorical columns → constant-impute (`"missing"`) + one-hot encode
  (`handle_unknown="ignore"`).
- Splits 80/20 train/test (stratified), fits/transforms, and persists:
  `models/preprocessor.pkl`, `data/processed/{X,y}_{train,test}.csv` (processed),
  plus raw (untransformed) splits, and `models/feature_columns.json`.

**3. Base models** (`03_base_models.ipynb`)
Trains 5 classifiers on the processed data: Logistic Regression (`class_weight=balanced`,
saga solver), Random Forest, Gradient Boosting, XGBoost (`scale_pos_weight` set from
class ratio), and LightGBM. Each model is scored by ROC-AUC, saved to `models/base/`,
and an ROC comparison plot is saved to `reports/figures/03_base_models_roc.png`.

**4. Stacking ensemble** (`04_stacking.ipynb`)
Combines the same 4 model families (LR, RF, XGB, LGBM) as base estimators inside a
scikit-learn `StackingClassifier` with a Logistic Regression final estimator (5-fold
CV). The fitted ensemble is saved to `models/stacked/stacked_model.pkl` and its
test-set probabilities to `notebooks/stacked_probabilities.csv`.

**5. Threshold optimization** (`05_threshold_optimization.ipynb`)
Defines a business cost matrix — false positive (approving a defaulter) costs 12,000,
false negative (rejecting a good applicant) costs 2,500 — and scans thresholds from
0.02 to 0.50 to find the one that minimizes total expected cost. The result is saved
to `notebooks/optimal_threshold.txt` (currently **≈0.49**).

**6. Evaluation** (`06_evaluation.ipynb`)
Loads the saved probabilities and optimal threshold, prints a classification report
and confusion matrix at that threshold, and saves the final ROC comparison
(`06_final_roc_all_models.png`) and confusion-matrix heatmap
(`06_confusion_matrix_optimal.png`) to `reports/figures/`.

## Serving layer

**`predict_single.py`**
- Loads `models/stacked/stacked_model.pkl` and `models/preprocessor.pkl` at import time.
- Defines `EXACT_COLUMNS` (the exact column order/set the preprocessor was fit on) and
  `DEFAULTS` (a full default record so a caller can supply only the fields they know).
- `predict(inputs: dict)`: merges the caller's inputs over `DEFAULTS`, recomputes the
  engineered ratio/derived features from the raw fields, transforms with the saved
  preprocessor, and calls `model.predict_proba`.
- Applies **hardcoded** risk-tier thresholds: `>=0.25` → Reject/high,
  `>=0.15` → Review/medium, else → Approve/low.
- Runnable as a CLI: `python predict_single.py '{"AMT_CREDIT": 500000, ...}'` (JSON arg),
  with a legacy 3-positional-argument fallback (`credit income days_employed`).

**`predict_api.py`**
- FastAPI app with permissive CORS (`allow_origins=["*"]`).
- `GET /` serves `credit-risk-demo.html`.
- `GET /predict` accepts applicant fields as query parameters (with sensible defaults),
  builds an input dict, and calls `predict_single.py` in a **subprocess** (passing the
  JSON payload as a CLI argument) rather than importing `predict()` directly.

**`credit-risk-demo.html`** ("CreditIQ")
A single-page, no-build-step HTML/CSS/JS form UI (styled with Google Fonts DM
Serif/Sans/Mono). Collects applicant details, calls
`http://localhost:8000/predict` with them as query params, and renders the returned
probability/decision/tier.

## `src/` package

`src/__init__.py`, `main.py`, `data_preprocessing.py`, `model_training.py`,
`threshold_optimizer.py`, and `evaluation.py` exist but are **all empty files**. They
appear to be intended module-ized counterparts of the notebook logic, but the actual
implementation currently lives entirely in the notebooks. See "Known issues" below.

## Setup & usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
pip install xgboost lightgbm   # required by the notebooks but missing from requirements.txt
```

### 2. Get the data
Place the raw dataset at `data/raw/application_train.csv` (not included in the repo —
see `.gitignore`).

### 3. Run the pipeline
Execute the notebooks in order (01 → 06) from the `notebooks/` directory. This
populates `data/processed/`, `models/`, and `reports/figures/`.

### 4. Serve predictions
```bash
uvicorn predict_api:app --reload --port 8000
```
Then open `http://localhost:8000/` for the demo UI, or call the API directly, e.g.:
```
GET http://localhost:8000/predict?credit=500000&income=180000&days_employed=1000
```

### 5. Single prediction via CLI
```bash
python predict_single.py '{"AMT_CREDIT": 500000, "AMT_INCOME_TOTAL": 180000, "DAYS_EMPLOYED": -1000}'
```

## Known issues / bugs found during review

1. **Inconsistent decision threshold.** The pipeline computes a cost-optimized
   threshold (`notebooks/optimal_threshold.txt`, currently **≈0.49**) in notebook 05,
   but `predict_single.py` never reads that file — it uses hardcoded, seemingly
   arbitrary tiers (`0.25` / `0.15`). The threshold analysis in the notebooks is
   effectively disconnected from the serving code, so production decisions do not
   reflect the cost optimization the project performs.

2. **`def_60` form field is never sent — it silently duplicates `def_30`.**
   In `credit-risk-demo.html`, the fetch URL builder has:
   ```js
   ...&def_30=${def_30}&def_60=${def_30}`;
   ```
   There is no `def_60` input element in the form at all, and the JS variable `def_30`
   is used for both query parameters. So `DEF_60_CNT_SOCIAL_CIRCLE` can never be set
   by the user from the UI — it always mirrors `DEF_30_CNT_SOCIAL_CIRCLE`.

3. **Empty `src/` modules.** `src/main.py`, `data_preprocessing.py`,
   `model_training.py`, `threshold_optimizer.py`, `evaluation.py`, and `__init__.py`
   are all zero-byte files. They add the appearance of a modular package structure
   but contain no code — all real logic lives in the notebooks and the two
   top-level `predict_*.py` scripts. This is dead/misleading scaffolding unless the
   intent is to eventually refactor notebook logic into these modules.

4. **`requirements.txt` is missing `xgboost` and `lightgbm`,** both of which are
   imported directly in `03_base_models.ipynb` and `04_stacking.ipynb`. A fresh
   `pip install -r requirements.txt` will not be sufficient to run the pipeline.

5. **Prediction served via subprocess, not a function call.** `predict_api.py`
   shells out to `python predict_single.py <json>` for every request instead of
   importing and calling `predict()` in-process. This works, but pays process-startup
   and model-reload cost on every single request (the model/preprocessor are
   reloaded from disk each time), and depends on `sys.executable` and the current
   working directory being correct at request time. It also passes the JSON payload
   as a raw command-line argument, which is fine here since inputs are numeric/simple
   strings, but is a pattern that would need care (shell/arg-escaping) if inputs ever
   included attacker-controlled special characters.

6. **CORS is fully open** (`allow_origins=["*"]`, `allow_credentials=True`). This is
   reasonable for a local demo but should be tightened before any real deployment.

7. **Data leakage risk in sampling order.** In `02_preprocessing.ipynb`, the 40%
   stratified sample is drawn before the train/test split, which is fine, but the
   `ColumnTransformer` imputers/scalers are correctly fit only on `X_train` — no
   leakage there. However, engineered ratio features (e.g. `CREDIT_INCOME_RATIO`)
   are computed on the full sampled dataframe *before* the split, which is safe here
   since they're deterministic row-wise transforms with no cross-row statistics, so
   this is **not** actually a leakage bug — noted only because it's worth
   double-checking if new engineered features are added later that use aggregates.

8. **`models/`, `data/`, and `*.pkl` files are all git-ignored**, meaning this
   repository is not runnable out-of-the-box from a fresh clone — the notebooks must
   be re-run (and the raw CSV manually obtained) to regenerate every artifact
   `predict_single.py` and `predict_api.py` depend on.

No syntax errors were found in the non-empty Python files, and the notebooks execute
in a straightforward linear order with consistent file paths between steps.
