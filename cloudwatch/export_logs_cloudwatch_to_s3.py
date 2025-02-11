import boto3
import datetime
import argparse
import time
import logging # Add logs
from botocore.exceptions import ClientError # Clean up error exceptions

""" 
  TO START SCRIPT EXECUTE THE SCRIPT AND LOG GROUP 
  Ex: python export_logs_cloudwatch_to_s3.py /ecs/demo-tsk-app-api
"""

################### Logging Configuration ###########################
# logging.basicConfig(level=logging.INFO)
timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a handler to print to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a handler to save to a file
file_handler = logging.FileHandler(f'logs/{timestamp}.log')
file_handler.setLevel(logging.INFO)

# Define the format of the logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


logs_client = boto3.client('logs')
s3_client = boto3.client('s3')

# Bucket
s3_bucket = 'ame-prd-log-groups-cloudwatch'

# 3 years ago
# three_years_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 365)
three_years_ago = datetime.datetime.now() - datetime.timedelta(days=2 * 365)

# Cutoff date based on retention period of 1827 days
retention_period_days = 1827
retention_cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_period_days)

# Export logs to S3
def export_logs_to_s3(log_group_name, from_time, to_time):
    # Ensure from_time is not earlier than retention_cutoff_date
    current_time = max(from_time, retention_cutoff_date)
    
    while current_time < to_time:
        if current_time.month == 12:
            next_month = current_time.replace(year=current_time.year + 1, month=1, day=1)
        else:
            next_month = current_time.replace(month=current_time.month + 1, day=1)

        export_to_time = min(next_month, to_time)

        log_streams_exist = check_log_streams_exist(log_group_name, current_time, export_to_time)

        if log_streams_exist:
            prefix = f'{log_group_name.strip("/")}/{current_time.year}/{current_time.month:02}'

            try:

                logging.info(f'Trying to create task: {log_group_name}, Year: {current_time.year}, Month: {current_time.month:02}')
                response = logs_client.create_export_task(
                    taskName=f'export_logs_{log_group_name}_{current_time.year}_{current_time.month:02}',
                    logGroupName=log_group_name,
                    fromTime=int(current_time.timestamp() * 1000),  # Convert to milliseconds
                    to=int(export_to_time.timestamp() * 1000),  # Convert to milliseconds
                    destination=s3_bucket,
                    destinationPrefix=prefix
                )
                
                # Validate running the task ID
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    logging.info(f'Task created for log group: {log_group_name}, Year: {current_time.year}, Month: {current_time.month:02}, Task ID: {response["taskId"]}')
                    
                    while True:
                        try:
                            task_status = logs_client.describe_export_tasks(taskId=response['taskId'])
                            if task_status['exportTasks'][0]['status']['code'] == 'COMPLETED':
                                logging.info(f'Task completed for log group: {log_group_name}, Year: {current_time.year}, Month: {current_time.month:02}, Task ID: {response["taskId"]}')
                                # logging.info("--------TEST DELETE---------")
                                delete_log_streams(log_group_name, current_time, export_to_time)
                                break
                            else:
                                logging.info(f'Task in progress for log group: {log_group_name}, Year: {current_time.year}, Month: {current_time.month:02}, Task ID: {response["taskId"]}')
                                time.sleep(60)  # Wait for 60 seconds before checking again
                        except ClientError as e:
                            logging.error(f'Error describing export task: {e}')
                            break
            except logs_client.exceptions.LimitExceededException:
                logging.error('LimitExceededException: Waiting before retrying...')
                time.sleep(60)  # Wait for 60 seconds before trying again
            
        current_time = next_month

# Remove log streams
def delete_log_streams(log_group_name, from_time, to_time):
    # Ensure from_time is not earlier than retention_cutoff_date
    logging.info(f'\nDeleting {log_group_name} with creation from time {from_time} to time {to_time}')
    from_time = max(from_time, retention_cutoff_date)
    paginator = logs_client.get_paginator('describe_log_streams')

    for page in paginator.paginate(logGroupName=log_group_name):
        for stream in page['logStreams']:
            try:
                stream_creation_time = datetime.datetime.fromtimestamp(stream['creationTime'] / 1000)

                if from_time <= stream_creation_time <= to_time:
                    log_stream_name = stream['logStreamName']
                    # logging.info(f'Found log stream: {log_stream_name} with creation time {stream_creation_time}')

                    # Delete the log stream
                    logging.info(f'Deleting log stream: {log_stream_name}')
                    logs_client.delete_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)

            except Exception as e:
                logging.error(f'Error processing log stream {stream["logStreamName"]}: {e}')

    add_tag_to_log_group(log_group_name, 'moved_to_bucket', s3_bucket)

# Add tag to log group
def add_tag_to_log_group(log_group_name, key, value):
    try:
        logs_client.tag_log_group(
            logGroupName=log_group_name,
            tags={key: value}
        )
        logging.info(f'Tag added to log group: {log_group_name}, Key: {key}, Value: {value}')
    except Exception as e:
        logging.error(f'Error adding tag to log group {log_group_name}: {e}')


# Check for the existence of log streams in the time range
def check_log_streams_exist(log_group_name, start_time, end_time):
    paginator = logs_client.get_paginator('describe_log_streams')
    try:
        for page in paginator.paginate(logGroupName=log_group_name):
            for stream in page['logStreams']:
                # Creation timestamp of the log stream
                stream_creation_time = datetime.datetime.fromtimestamp(stream['creationTime'] / 1000)

                # Validating if the log stream is within the range we are interested in
                if start_time <= stream_creation_time <= end_time:
                    return True
    except logs_client.exceptions.ResourceNotFoundException:
        pass  # No log streams found for the log group

    return False

# Manage logs
def manage_log_group(log_group_name):
    # Get details of the log group
    response = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)

    for log_group in response['logGroups']:
        if log_group['logGroupName'] == log_group_name:
            # Checking if log group starts with /ecs/
            if log_group_name.startswith('/ecs/'):
                creation_time = datetime.datetime.fromtimestamp(log_group['creationTime'] / 1000)
                retention_in_days = log_group.get('retentionInDays', None)

                # Retention time is greater than 1 year
                if retention_in_days and retention_in_days > 365:
                    # Check if the log group is older than three years
                    if creation_time < three_years_ago:
                        logging.info(f'Processing log group: {log_group_name}, Creation time: {creation_time}')

                        # Set the time range for export
                        from_time = creation_time
                        to_time = three_years_ago

                        # Export logs to S3
                        export_logs_to_s3(log_group_name, from_time, to_time)

                        # # Wait for the completion of exports
                        # while True:
                        #     running_tasks = check_running_export_tasks(log_group_name)
                        #     if not running_tasks:
                        #         break
                        #     logging.info(f'Waiting for {log_group_name} with {len(running_tasks)} export tasks to complete...')
                        #     time.sleep(60)
                        # # Remove the corresponding log streams
                        # delete_log_streams(log_group_name, from_time, to_time)

                    else:
                        logging.error(f'Log group {log_group_name} is not older than three years.')
                else:
                    logging.error(f'Log group {log_group_name} has a retention period of less than one year.')
            else:
                logging.error(f'Log group {log_group_name} does not start with /ecs/.')
            break
    else:
        logging.error(f'Log group {log_group_name} not found.')

# Check running export tasks
def check_running_export_tasks(log_group_name):
    response = logs_client.describe_export_tasks(
        statusCode='RUNNING'
    )
    running_tasks = [
        task for task in response['exportTasks']
        if task['logGroupName'] == log_group_name
    ]
    return running_tasks

# Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a specific CloudWatch log group.')
    parser.add_argument('log_group_name', type=str, help='The name of the log group to process.')

    args = parser.parse_args()

    manage_log_group(args.log_group_name)
