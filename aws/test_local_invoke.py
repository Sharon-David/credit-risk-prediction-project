import urllib.request
import json
import time

url = "http://localhost:8080/invocations"
data = {"AMT_CREDIT": 500000, "AMT_INCOME_TOTAL": 180000}
req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as resp:
        print("Response:", resp.read().decode())
except Exception as e:
    print("Error:", e)
