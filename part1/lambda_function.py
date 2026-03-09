import boto3
import os
import time

def lambda_handler(event, context):
    distribution_id = os.environ['DISTRIBUTION_ID']

    records = event.get('Records', [])
    if not records:
        return {'statusCode': 200, 'body': 'No records in event — use S3 trigger or S3 Put test template'}

    paths = []
    for record in records:
        key = record['s3']['object']['key']
        paths.append('/' + key)

    cloudfront = boto3.client('cloudfront')
    cloudfront.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            'Paths': {'Quantity': len(paths), 'Items': paths},
            'CallerReference': str(time.time())
        }
    )

    return {'statusCode': 200, 'body': f'Invalidated: {paths}'}
