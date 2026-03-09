# Part 1 Demo: S3 + CloudFront + Lambda (Cache Invalidation)

**Services:** Amazon S3, Amazon CloudFront, AWS Lambda
**Time:** ~40 minutes
**Region:** ap-south-2 (Hyderabad)

---

## Step 1: Create S3 Bucket

1. Go to **S3 Console → Create bucket**
2. **Bucket name:** `aws-workshop-demo-site` (must be globally unique — append a suffix if taken)
3. **Region:** ap-south-2
4. Leave all other settings as default (keep "Block all public access" checked)
5. Click **Create bucket**

---

## Step 2: Upload index.html to S3

1. Open your bucket → **Objects** tab → **Upload**
2. Click **Add files** → select `part1/index.html`
3. Click **Upload**

---

## Step 3: Create CloudFront Distribution

1. Go to **CloudFront Console → Create distribution**
2. **Origin domain:** select your S3 bucket from the dropdown
3. **Origin access:** select **Origin access control settings (recommended)**
   - Click **Create new OAC** → leave defaults → **Create**
4. **Viewer protocol policy:** Redirect HTTP to HTTPS
5. **Default root object:** `index.html`
6. **Price class:** Use only North America, Europe, Asia, Middle East, and Africa
7. Click **Create distribution**
8. Wait **3–5 minutes** for status to change from "Deploying" to "Enabled"

---

## Step 4: View the Website

1. Copy the **Distribution domain name** from CloudFront (e.g., `d1234abcdef.cloudfront.net`)
2. Open it in browser → site loads with the basic feedback form (no rating field)

---

## Step 5: Upload the Updated index.html (with Rating)

1. Inside `part1/with_rating/` there is another `index.html` that includes a rating dropdown
2. Go to S3 → your bucket → **Upload** → upload `part1/with_rating/index.html`
   - This overwrites the existing `index.html` in the bucket

---

## Step 6: See the Caching Problem

1. Refresh the **CloudFront URL** → ❌ still shows the old page without the rating field
2. The content is cached at CloudFront edge locations — it doesn't know S3 was updated

---

## Step 7: Manually Create Invalidation

1. Go to **CloudFront Console** → your distribution → **Invalidations** tab
2. Click **Create invalidation**
3. Add object path: `/index.html`
4. Click **Create invalidation**
5. Wait for status to change to **"Completed"** (~30–60 seconds)
6. Refresh the **CloudFront URL** → ✅ now shows the updated page with the rating dropdown

---

## Step 8: Set Up Lambda Function (Automate Invalidation)

### 8a. Create the Function

1. Go to **Lambda Console → Create function**
2. **Function name:** `CloudFrontCacheInvalidator`
3. **Runtime:** Python 3.13
4. Click **Create function**

### 8b. Add the Code

1. In the **Code** tab, replace default code with contents of `part1/lambda_function.py`:

```python
import boto3
import os
import time

def lambda_handler(event, context):
    distribution_id = os.environ['DISTRIBUTION_ID']

    records = event.get('Records', [])
    if not records:
        return {'statusCode': 200, 'body': 'No records in event'}

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
```

2. Click **Deploy**

### 8c. Set Environment Variable

1. Go to **Configuration** → **Environment variables** → **Edit**
2. Add:
   - **Key:** `DISTRIBUTION_ID`
   - **Value:** your CloudFront distribution ID (e.g., `E3OUV9H1GBDW02`)
3. Click **Save**

### 8d. Add IAM Permissions for CloudFront

1. Go to **Configuration** → **Permissions** → click the **Role name** link
2. In IAM, click **Add permissions** → **Create inline policy** → switch to **JSON**
3. Paste (replace `YOUR_ACCOUNT_ID` and `YOUR_DISTRIBUTION_ID`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "cloudfront:CreateInvalidation",
            "Resource": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
        }
    ]
}
```

4. Click **Next** → name it `cloudfront-invalidation-policy` → **Create policy**

### 8e. Add S3 Trigger

1. Back in Lambda console → click **Add trigger**
2. **Source:** S3
3. **Bucket:** select your static site bucket
4. **Event types:** All object create events
5. Acknowledge the recursive invocation warning → click **Add**

---

## Step 9: Verify Automated Invalidation

1. Upload the original `part1/index.html` (without rating) to S3 — this overwrites the current file
2. Go to **CloudFront Console** → your distribution → **Invalidations** tab
3. A new invalidation should appear automatically (created by Lambda)
4. Wait for status to change to **"Completed"**
5. Refresh the **CloudFront URL** → ✅ shows the old page without rating — invalidation was automated

---

## Files Reference

| File | Purpose |
|------|---------|
| `index.html` | Static website — basic feedback form (no rating) |
| `with_rating/index.html` | Static website — feedback form with rating dropdown |
| `lambda_function.py` | Lambda function — auto-invalidates CloudFront cache on S3 upload |
| `lambda-cloudfront-policy.json` | IAM policy for CloudFront invalidation permission |
