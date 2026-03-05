from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json

app = FastAPI()

# Allow CORS – this lets your HTML page talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # For testing — allows any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict")
def predict(credit: float, income: float, days: float):
    try:
        result = subprocess.run(
            ["python", "-W", "ignore", "predict_single.py", str(credit), str(income), str(days)],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout.strip())
    except Exception as e:
        return {"error": str(e)}