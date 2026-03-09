# Part 2 Demo: API Gateway + Lambda + DynamoDB (Feedback API)

**Services:** AWS Lambda, Amazon DynamoDB, Amazon API Gateway
**Time:** ~30 minutes
**Region:** ap-south-2 (Hyderabad)
**Prerequisite:** Part 1 completed (S3 bucket + CloudFront distribution with Lambda auto-invalidation)

---

## Step 1: Create DynamoDB Table

1. Go to **DynamoDB Console → Create table**
2. **Table name:** `WorkshopFeedback`
3. **Partition key:** `id` (String)
4. **Table settings:** Customize → **Billing mode:** On-demand
5. Click **Create table**

---

## Step 2: Create Lambda Function (Feedback API)

### 2a. Create the Function

1. Go to **Lambda Console → Create function**
2. **Function name:** `WorkshopFeedbackAPI`
3. **Runtime:** Python 3.13
4. Click **Create function**

### 2b. Add the Code

1. In the **Code** tab, replace default code with contents of `part2/feedback_api_lambda.py`:

```python
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
```

2. Click **Deploy**

### 2c. Set Environment Variables

1. Go to **Configuration** → **Environment variables** → **Edit**
2. Add:
   - **Key:** `TABLE_NAME` — **Value:** `WorkshopFeedback`
3. Click **Save**

### 2d. Add IAM Permissions for DynamoDB

1. Go to **Configuration** → **Permissions** → click the **Role name** link
2. In IAM, click **Add permissions** → **Create inline policy** → switch to **JSON**
3. Paste (replace `YOUR_ACCOUNT_ID`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:ap-south-2:YOUR_ACCOUNT_ID:table/WorkshopFeedback"
        }
    ]
}
```

4. Click **Next** → name it `dynamodb-access-policy` → **Create policy**

---

## Step 3: Create API Gateway

### 3a. Create the API

1. Go to **API Gateway Console → Create API → REST API** → **Build**
2. **API name:** `WorkshopFeedbackAPI`
3. Click **Create API**

### 3b. Create Resource

1. Click **Create Resource**
2. **Resource name:** `feedback`
3. ✅ Check **Enable CORS**
4. Click **Create Resource**

### 3c. Create GET Method

1. Select `/feedback` → click **Create Method**
2. **Method type:** GET
3. **Integration type:** Lambda Function
4. ✅ Check **Lambda Proxy Integration**
5. **Lambda function:** `WorkshopFeedbackAPI`
6. Click **Create Method**

### 3d. Create POST Method

1. Select `/feedback` → click **Create Method**
2. **Method type:** POST
3. **Integration type:** Lambda Function
4. ✅ Check **Lambda Proxy Integration**
5. **Lambda function:** `WorkshopFeedbackAPI`
6. Click **Create Method**

### 3e. Deploy the API

1. Click **Deploy API**
2. **Stage:** New Stage → **Stage name:** `prod`
3. Click **Deploy**
4. Copy the **Invoke URL** (e.g., `https://abc123.execute-api.ap-south-2.amazonaws.com/prod`)

---

## Step 4: Update index.html and Upload to S3

1. Open `part2/index.html` locally
2. Replace the `API_URL` value with your actual API Gateway invoke URL:
   ```javascript
   const API_URL = 'https://abc123.execute-api.ap-south-2.amazonaws.com/prod';
   ```
3. Upload this `index.html` to the S3 bucket (same bucket from Part 1)
4. Lambda auto-invalidation from Part 1 will clear the CloudFront cache

---

## Step 5: Test the Full Application

1. Open the **CloudFront URL** in browser
2. Fill in Name, Message, and Rating → click **Submit** → should show "✅ Feedback submitted!"
3. Click **Load Feedback** → should display the submitted feedback with star ratings
4. Go to **DynamoDB Console** → `WorkshopFeedback` table → **Explore table items** → verify the item appears with `id`, `name`, `message`, and `rating` fields

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `KeyError: 'httpMethod'` | Enable **Lambda Proxy Integration** on GET and POST methods, redeploy API |
| `AccessDenied` on DynamoDB | Attach `lambda-dynamodb-policy.json` to the Lambda role |
| Data not appearing in DynamoDB | Check region — Lambda and DynamoDB must be in the same region |
| CORS error in browser | Ensure CORS was enabled when creating the `/feedback` resource, redeploy API |

---

## Files Reference

| File | Purpose |
|------|---------|
| `feedback_api_lambda.py` | Lambda function — handles GET/POST for feedback |
| `lambda-dynamodb-policy.json` | IAM policy for DynamoDB read/write access |
| `index.html` | Static website with rating field and API Gateway URL |
