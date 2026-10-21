# Build from the REPO ROOT:  docker build --provenance=false -f aws/sagemaker/Dockerfile -t credit-risk .
# Match the Python version the model was trained with (the __pycache__ suggests 3.13).
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY aws/sagemaker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY predict_single.py /app/predict_single.py
COPY notebooks/optimal_threshold.txt /app/notebooks/optimal_threshold.txt
COPY aws/sagemaker/serve.py /app/serve.py
ENTRYPOINT ["python", "/app/serve.py"]
