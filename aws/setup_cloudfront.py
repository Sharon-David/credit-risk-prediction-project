import boto3, json, time

cf = boto3.client('cloudfront')
s3 = boto3.client('s3', region_name='us-east-1')

bucket_name = 'credit-risk-web-aranck'
account_id = '190493315867'

# 1. Create or get Origin Access Control (OAC)
oac_name = 'credit-risk-web-oac'
oac_id = None
try:
    oacs = cf.list_origin_access_controls()['OriginAccessControlList']
    for item in oacs.get('Items', []):
        if item['Name'] == oac_name:
            oac_id = item['Id']
            break
except Exception as e:
    print('Checking OACs:', e)

if not oac_id:
    print('Creating OAC...')
    resp = cf.create_origin_access_control(
        OriginAccessControlConfig={
            'Name': oac_name,
            'Description': 'OAC for credit-risk-web-aranck',
            'SigningProtocol': 'sigv4',
            'SigningBehavior': 'always',
            'OriginAccessControlOriginType': 's3'
        }
    )
    oac_id = resp['OriginAccessControl']['Id']

print(f'OAC ID: {oac_id}')

# 2. Check if Distribution already exists
dist_id = None
dist_domain = None
try:
    dists = cf.list_distributions()['DistributionList']
    for d in dists.get('Items', []):
        if d.get('Comment') == 'Credit Risk Demo Website':
            dist_id = d['Id']
            dist_domain = d['DomainName']
            print(f'Found existing CloudFront distribution: {dist_id} ({dist_domain})')
            break
except Exception as e:
    print('Checking distributions:', e)

if not dist_id:
    print('Creating CloudFront distribution...')
    s3_domain = f'{bucket_name}.s3.us-east-1.amazonaws.com'
    origin_id = f'S3-{bucket_name}'
    
    dist_config = {
        'CallerReference': str(int(time.time())),
        'Comment': 'Credit Risk Demo Website',
        'DefaultRootObject': 'credit-risk-demo.html',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': origin_id,
                    'DomainName': s3_domain,
                    'S3OriginConfig': {'OriginAccessIdentity': ''},
                    'OriginAccessControlId': oac_id
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': origin_id,
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD'],
                'CachedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD']
                }
            },
            'CachePolicyId': '658327ea-f89d-4fab-a63d-7e88639e58f6' # Managed-CachingOptimized
        },
        'Enabled': True
    }
    
    resp = cf.create_distribution(DistributionConfig=dist_config)
    dist_id = resp['Distribution']['Id']
    dist_domain = resp['Distribution']['DomainName']
    print(f'Created CloudFront distribution: {dist_id}')

print(f'CloudFront Domain: https://{dist_domain}')

# 3. Update S3 Bucket Policy to allow CloudFront OAC
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipalReadOnly",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{account_id}:distribution/{dist_id}"
                }
            }
        }
    ]
}

s3.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy)
)
print('Updated S3 bucket policy for CloudFront access.')
