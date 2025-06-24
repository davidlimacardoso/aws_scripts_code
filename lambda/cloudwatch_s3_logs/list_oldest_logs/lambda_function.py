import boto3
import concurrent.futures
import json
from datetime import datetime, timezone

BUCKET = "log-groups-cloudwatch"
REGION = "us-east-1"
ACCOUNT_ID = "xxxxxxxxxxx"
SQS_QUEUE = "ops-delete-cloudwatch-oldest-logs"
SQS_QUEUE_URL = f"https://sqs.{REGION}.amazonaws.com/{ACCOUNT_ID}/{SQS_QUEUE}"

# Calculate reference year and month: 5 years ago from now
now = datetime.now(timezone.utc)
REF_YEAR = now.year - 5
REF_MONTH = now.month - 1

s3 = boto3.client("s3", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)

def list_prefixes(bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/"):
        for cp in page.get("CommonPrefixes", []):
            yield cp["Prefix"]

def process_month(month_path):
    parts = month_path.strip("/").split("/")
    if len(parts) < 4:
        return
    try:
        year = int(parts[-2])
        month = int(parts[-1])
    except ValueError:
        return
    if (year < REF_YEAR) or (year == REF_YEAR and month <= REF_MONTH):
        message_body = {"path": month_path}
        return message_body

def send_messages(messages):
    if not messages:
        return
    # Send in batches of 10 (SQS limit)
    batch_size = 10
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i+batch_size]
        entries = [{"Id": str(j), "MessageBody": str(msg)} for j, msg in enumerate(batch)]
        try:
            response = sqs.send_message_batch(QueueUrl=SQS_QUEUE_URL, Entries=entries)
            print(f"Sent {len(batch)} messages.")
        except Exception as e:
            print(f"Failed to send messages: {e}")

def lambda_handler(event, context):

    if not event.get('prefix') or event['prefix'] == "":
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Please, insert a valid bucket prefix! ex: aws/lambda/... ecs/'})
        }

    PREFIX = event.get('prefix', None)
    print(f"Starting to process {PREFIX}...")

    services = list(list_prefixes(BUCKET, PREFIX))
    all_messages = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        future_to_month = {executor.submit(list_prefixes, BUCKET, service): service for service in services}
        
        for future in concurrent.futures.as_completed(future_to_month):
            service = future_to_month[future]
            try:
                years = list(future.result())
                for year_path in years:
                    months = list(list_prefixes(BUCKET, year_path))
                    month_messages = executor.map(process_month, months)
                    all_messages.extend(filter(None, month_messages))
            except Exception as e:
                print(f"Error processing service {service}: {e}")
    print(all_messages)
    send_messages(all_messages)
    return {"statusCode": 200, "body": "Code running with success!"}
