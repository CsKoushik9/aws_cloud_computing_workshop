# ☁️ AWS Cloud Computing Workshop

A hands-on workshop introducing core AWS services by building a static website with a serverless feedback system.

**Audience:** College Students
**Duration:** ~90 minutes
**Prerequisites:** Basic programming knowledge, AWS Free Tier account
**Region:** ap-south-2 (Hyderabad)

---

## Architecture

```
User → CloudFront (CDN) → S3 (Static Website)
         ↓
       Feedback Form → API Gateway → Lambda → DynamoDB

S3 Upload → Lambda (Auto Cache Invalidation) → CloudFront
```

## Services Covered

| Service | Role |
|---------|------|
| S3 | Hosts the static HTML website |
| CloudFront | CDN — delivers the site globally via edge caches |
| Lambda | 1) Auto-invalidates CloudFront cache on S3 upload 2) Feedback API backend |
| DynamoDB | Stores feedback data (NoSQL) |
| API Gateway | REST API endpoint for the feedback form |

---

## Workshop Structure

### Part 1: S3 + CloudFront + Lambda (Cache Invalidation) — ~40 min

Host a static website on S3, serve it via CloudFront, and automate cache invalidation using Lambda.

➡️ [Part 1 Demo Steps](part1/demo-part1-steps.md)

### Part 2: API Gateway + Lambda + DynamoDB (Feedback API) — ~30 min

Build a serverless backend API that stores and retrieves feedback from DynamoDB.

➡️ [Part 2 Demo Steps](part2/demo-part2-steps.md)

---

## Project Structure

```
cloud_computing_workshop/
├── README.md
├── part1/
│   ├── demo-part1-steps.md          # Part 1 step-by-step instructions
│   ├── index.html                    # Static site (basic — no rating)
│   ├── lambda_function.py            # CloudFront cache invalidation Lambda
│   ├── lambda-cloudfront-policy.json # IAM policy for Lambda
│   └── with_rating/
│       └── index.html                # Static site (with rating dropdown)
├── part2/
│   ├── demo-part2-steps.md           # Part 2 step-by-step instructions
│   ├── index.html                    # Static site with API Gateway integration
│   ├── feedback_api_lambda.py        # Feedback API Lambda function
│   └── lambda-dynamodb-policy.json   # IAM policy for DynamoDB access
└── aws-workshop-proposal.md          # Full workshop proposal document
```

---

## Cleanup (After Workshop)

Delete all resources to avoid charges:

1. Empty and delete the S3 bucket
2. Disable and delete the CloudFront distribution
3. Delete both Lambda functions (`CloudFrontCacheInvalidator`, `WorkshopFeedbackAPI`)
4. Delete the DynamoDB table (`WorkshopFeedback`)
5. Delete the API Gateway (`WorkshopFeedbackAPI`)
6. Delete IAM inline policies added to Lambda roles

---

## License

This project is for educational purposes.
