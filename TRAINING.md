# Retraining the Model: Step-by-Step (Laptop Only)

> **Context for whoever (or whichever AI agent) is reading this:**
> This repo is a credit-risk prediction project (Home Credit Default Risk dataset). The trained model
> files were lost, and they are needed to deploy the model on AWS (see `aws/README_AWS.md`, Account B).
> Your only job is to **re-run the existing notebooks unchanged** to regenerate two files:
>
> - `models/preprocessor.pkl`
> - `models/stacked/stacked_model.pkl`
>
> **Do NOT change any notebook code, hyperparameters, or `random_state` values.** No tuning, no new features,
> no refactoring. This is just "run what already exists". Everything runs locally; no AWS needed.
>
> Expected total time: **~30–60 minutes**, mostly waiting. Needs ~8 GB RAM and ~2 GB free disk.

---

## Step 1: Install Python
- Install **Python 3.12** from https://www.python.org/downloads/ (on Windows, tick **"Add python.exe to PATH"**
  in the installer).
- Check in a new terminal: `python --version` → `Python 3.12.x`.
- (3.11 or 3.13 also work. Just remember which version you used; Step 8 needs it.)

## Step 2: Get the repo
```
git clone <repo-url>
cd credit-risk-prediction-project
```
(Or, if you already have it: `git pull`.) **All commands below are run from this repo root folder** unless stated otherwise.

## Step 3: Create a virtual environment and install libraries
Windows (PowerShell):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
macOS / Linux:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- If PowerShell says running scripts is disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, then activate again.
- Check: `python -c "import sklearn, xgboost, lightgbm; print('ok')"` → `ok`.

## Step 4: Download the dataset
1. Go to https://www.kaggle.com/c/home-credit-default-risk/data (log in or create a free Kaggle account).
2. If asked, click **"I Understand and Accept"** / **Join Competition** to accept the rules (needed to download).
3. Download **`application_train.csv`** (~160 MB; it may come as a `.zip`, so extract it).
   You only need this one file, not the whole competition download.
4. Put it at exactly: `data/raw/application_train.csv`

## Step 5: Create the output folders
These are git-ignored, so they don't exist after cloning. Create them:

Windows (PowerShell):
```
mkdir data\raw, data\processed, models\base, models\stacked -Force
```
macOS / Linux:
```
mkdir -p data/raw data/processed models/base models/stacked
```
(Do this **before** Step 4's file copy if `data/raw` doesn't exist yet.)

Folder layout should now be:
```
data/raw/application_train.csv
data/processed/        (empty)
models/base/           (empty)
models/stacked/        (empty)
```

## Step 6: Run the notebooks
The notebooks use relative paths like `../data/...`, so **run them from inside the `notebooks/` folder**.

```
cd notebooks
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 02_preprocessing.ipynb
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 04_stacking.ipynb
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 05_threshold_optimization.ipynb
cd ..
```

| Notebook | Required? | Time | Produces |
|---|---|---|---|
| `02_preprocessing` | **Yes** | 1–2 min | `models/preprocessor.pkl`, `models/feature_columns.json`, `data/processed/*.csv` |
| `04_stacking` | **Yes** | **20–45 min** (looks frozen; it isn't) | `models/stacked/stacked_model.pkl`, `notebooks/stacked_probabilities.csv` |
| `05_threshold_optimization` | Yes (seconds) | <1 min | `notebooks/optimal_threshold.txt` (should be ≈0.49) |
| `03_base_models` | Optional | 10–20 min | `models/base/*.pkl`, ROC chart (only for the report) |
| `06_evaluation` | Optional (run after 03) | <1 min | final charts in `reports/figures/` |

- Alternative: open them in Jupyter (`jupyter notebook`, then click a notebook → **Run → Run All Cells**), in the
  same order. Either way is fine.
- `ConvergenceWarning` messages from Logistic Regression are **normal**; ignore them.
- `--inplace` saves the run outputs into the notebooks. That's fine.

## Step 7: Check it worked
1. These two files must exist (the stacked model is usually tens of MB or more):
   - `models/preprocessor.pkl`
   - `models/stacked/stacked_model.pkl`
2. The stacking notebook printed `Stacked ROC AUC:` around **0.75–0.76**. (Check the output cell if you
   used Jupyter; otherwise open `notebooks/04_stacking.ipynb` in VS Code/Jupyter to see it.)
3. Smoke test from the **repo root** (works in PowerShell and bash):
   ```
   python -c "from predict_single import predict; print(predict({'AMT_CREDIT': 500000, 'AMT_INCOME_TOTAL': 180000, 'DAYS_EMPLOYED': -1000}))"
   ```
   Expected: something like `{'probability': 0.3..., 'decision': '...', 'tier': '...'}`.
   If you see `{'error': ...}` instead, something went wrong; see Troubleshooting.

## Step 8: Record library versions (important for AWS)
SageMaker must load the model with the **exact same library versions** it was trained with. Run:
```
python --version
pip show scikit-learn xgboost lightgbm
```
Then edit two files in the repo:

1. `aws/sagemaker/requirements.txt`: pin the three versions it printed, e.g.:
   ```
   scikit-learn==1.6.1
   xgboost==2.1.3
   lightgbm==4.5.0
   ```
   (Keep the other lines: `pandas`, `numpy`, `joblib`, `flask`.)
2. `aws/sagemaker/Dockerfile`: set the first `FROM` line to your Python version, e.g. Python 3.12.x →
   `FROM python:3.12-slim`

Commit these two small edits (`git add aws/sagemaker/requirements.txt aws/sagemaker/Dockerfile` → commit → push).

## Step 9: Hand off the model files
- The `.pkl` files are **git-ignored on purpose** (too big for git). **Don't force-add them.**
- If you are also the **Account B** person in `aws/README_AWS.md`: you're done. Keep them where they are and
  continue with section B2.
- Otherwise: send these two files to the Account B person (Google Drive, OneDrive, USB...):
  - `models/preprocessor.pkl`
  - `models/stacked/stacked_model.pkl`

  They must place them at exactly the same paths in their copy of the repo. They also need your Step 8 commit
  (pull it), since the versions must match the files you trained.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `FileNotFoundError: ../data/raw/application_train.csv` | You're not inside `notebooks/` when running, or the CSV isn't at `data/raw/application_train.csv`. |
| `FileNotFoundError: ../models/...` or `../data/processed/...` | The folders from Step 5 are missing. Create them and re-run. |
| `ModuleNotFoundError: xgboost` / `lightgbm` / `sklearn` | The virtual environment isn't active (Step 3). Activate it and `pip install -r requirements.txt`. |
| `jupyter: command not found` | Same as above (venv not active), or run `pip install jupyter nbconvert`. |
| `MemoryError` / laptop freezes during 04 | Close other apps (browsers!) and re-run 04. Needs ~8 GB RAM. |
| 04 has been running 30+ min with no output | Normal. It trains 4 models × 6 times. Up to ~1 hour on slower laptops is still fine. |
| Smoke test returns `{'error': ...}` | Make sure you ran it from the repo root, and that both `.pkl` files exist. |
