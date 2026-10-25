import boto3

apigw = boto3.client('apigatewayv2', region_name='us-east-1')
lam = boto3.client('lambda', region_name='us-east-1')
api_name = 'credit-risk-api'
fn_name = 'credit-risk-predict'

apis = apigw.get_apis()['Items']
target_api = next((a for a in apis if a['Name'] == api_name), None)

fn_arn = lam.get_function(FunctionName=fn_name)['Configuration']['FunctionArn']

api_id = target_api['ApiId']
print(f'API ID: {api_id}')

# 2. Check/create integration
integrations = apigw.get_integrations(ApiId=api_id)['Items']
if not integrations:
    integration = apigw.create_integration(
        ApiId=api_id,
        IntegrationType='AWS_PROXY',
        IntegrationUri=fn_arn,
        PayloadFormatVersion='2.0'
    )
    integration_id = integration['IntegrationId']
else:
    integration_id = integrations[0]['IntegrationId']

# 3. Check/create route GET /predict
routes = apigw.get_routes(ApiId=api_id)['Items']
target_route = next((r for r in routes if r['RouteKey'] == 'GET /predict'), None)
if not target_route:
    apigw.create_route(
        ApiId=api_id,
        RouteKey='GET /predict',
        Target=f'integrations/{integration_id}'
    )
    print('Created route GET /predict')

# 4. Check/create stage $default with autoDeploy
stages = apigw.get_stages(ApiId=api_id)['Items']
target_stage = next((s for s in stages if s['StageName'] == '$default'), None)
if not target_stage:
    apigw.create_stage(
        ApiId=api_id,
        StageName='$default',
        AutoDeploy=True
    )
    print('Created $default stage')
else:
    print('Stage $default already exists')

# 5. Grant Lambda invoke permission to API Gateway
try:
    lam.add_permission(
        FunctionName=fn_name,
        StatementId='apigateway-invoke-permission',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:us-east-1:190493315867:{api_id}/*/*/predict'
    )
    print('Added Lambda invoke permission')
except lam.exceptions.ResourceConflictException:
    print('Lambda invoke permission already exists')

endpoint_url = target_api.get('ApiEndpoint') or f'https://{api_id}.execute-api.us-east-1.amazonaws.com'
print('API Invoke URL:', endpoint_url)
