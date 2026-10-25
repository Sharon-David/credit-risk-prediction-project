import boto3, time

sm = boto3.client('sagemaker', region_name='us-east-1')
endpoint_name = 'credit-risk-endpoint'

print(f"Waiting for endpoint '{endpoint_name}' to become InService...")
start_time = time.time()
while True:
    try:
        desc = sm.describe_endpoint(EndpointName=endpoint_name)
        status = desc['EndpointStatus']
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Status: {status}")
        if status == 'InService':
            print(f"SUCCESS: Endpoint {endpoint_name} is InService!")
            break
        elif status in ('Failed', 'Deleting'):
            print(f"FAILED: Endpoint entered status: {status}")
            print("Failure reason:", desc.get('FailureReason'))
            break
    except Exception as e:
        print("Error checking status:", e)
    time.sleep(20)
