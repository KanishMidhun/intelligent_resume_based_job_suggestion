import boto3
import json
from botocore.config import Config
from config import AWS_REGION, RESUME_LAMBDA, S3_BUCKET

boto_cfg = Config(retries={'max_attempts': 3})

lambda_client = boto3.client("lambda", region_name=AWS_REGION, config=boto_cfg)
s3_client = boto3.client("s3", region_name=AWS_REGION)

def upload_to_s3(file, filename):
    s3_client.upload_fileobj(
        file,
        S3_BUCKET,
        f"ui_uploads/{filename}",
        ExtraArgs={"ContentType": "application/pdf"}
    )
    return f"ui_uploads/{filename}"

def trigger_resume_lambda(s3_key, user_id):
    payload = {
        "user_id": user_id,
        "s3_key": s3_key
    }
    lambda_client.invoke(
        FunctionName=RESUME_LAMBDA,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8")

    )
