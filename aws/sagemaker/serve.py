# Minimal SageMaker inference server: hosts the EXISTING stacked_model.pkl + preprocessor.pkl.
# SageMaker extracts model.tar.gz to /opt/ml/model, which contains models/stacked/stacked_model.pkl
# and models/preprocessor.pkl. predict_single.py loads those relative paths, so chdir there first.
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
