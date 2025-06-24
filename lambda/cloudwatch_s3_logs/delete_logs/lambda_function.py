import boto3
import json

BUCKET = "log-groups-cloudwatch"
REGION = "us-east-1"
ACCOUNT_ID = "xxxxxxxxxxxxxxx"
SQS_QUEUE = "ops-delete-cloudwatch-oldest-logs"
SQS_QUEUE_URL = f"https://sqs.{REGION}.amazonaws.com/{ACCOUNT_ID}/{SQS_QUEUE}"

s3 = boto3.client("s3", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)

def delete_s3_prefix(prefix):
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        objects = page.get("Contents", [])
        if objects:
            delete_keys = [{"Key": obj["Key"]} for obj in objects]
            response = s3.delete_objects(Bucket=BUCKET, Delete={"Objects": delete_keys})
            print(response)
            print(f"Deleted {len(delete_keys)} objects from {prefix}")

def process_queue():
    while True:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2
        )
        # print(response)
        messages = response.get("Messages", [])
        
        if not messages:
            print("No more messages in the queue.")
            break

        for msg in messages:
            try:
                body = msg["Body"]
                # Fix single quotes to double quotes if necessary
                if body.startswith("{'") or body.startswith("[{'"):
                    body = body.replace("'", '"')
                data = json.loads(body)
                prefix = data.get("path")
                if prefix:
                    print(f"Deleting S3 prefix: {prefix}")
                    delete_s3_prefix(prefix)
            except Exception as e:
                print(f"Error processing message: {e}")

            # Delete message from queue after processing
            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=msg["ReceiptHandle"]
            )

def lambda_handler(event, context):
    process_queue()
