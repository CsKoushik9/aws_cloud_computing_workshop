import json
import boto3
import os
import time

table = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION']).Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    method = event['httpMethod']

    if method == 'POST':
        body = json.loads(event['body'])
        body['id'] = str(int(time.time() * 1000))
        table.put_item(Item=body)
        return response(200, {'status': 'saved'})

    elif method == 'GET':
        items = table.scan()['Items']
        return response(200, items)

    return response(400, {'error': 'Unsupported method'})

def response(code, body):
    return {
        'statusCode': code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body)
    }
