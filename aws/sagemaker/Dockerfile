# Build from the REPO ROOT:  docker build --provenance=false -f aws/sagemaker/Dockerfile -t credit-risk .
# Library versions (requirements.txt) are what must match the trained model; Python 3.13 is fine.
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY aws/sagemaker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && pip uninstall -y nvidia-nccl-cu12
COPY predict_single.py /app/predict_single.py
COPY notebooks/optimal_threshold.txt /app/notebooks/optimal_threshold.txt
COPY aws/sagemaker/serve.py /app/serve.py
ENTRYPOINT ["python", "/app/serve.py"]
