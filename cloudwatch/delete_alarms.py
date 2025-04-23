import boto3

def delete_cloudwatch_alarms_by_prefix(prefix_names):
    # Initialize CloudWatch client
    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

    try:

        # List all alarms using a paginator
        paginator = cloudwatch.get_paginator('describe_alarms')
        for page in paginator.paginate():
            alarms = page.get('MetricAlarms', [])

            for alarm in alarms:
                alarm_name = alarm['AlarmName']

                for prefix in prefix_names:
                    # Check if the alarm name starts with the specified DynamoDB table prefix
                    if alarm_name.startswith(prefix):
                        # Delete the alarm
                        print(f"Deleting alarm: {alarm_name}")
                        response = cloudwatch.delete_alarms(AlarmNames=[alarm_name])

                        print(response)
                

        print("All matching alarms have been deleted.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with your prefix names
    prefix_names = [
        'match_name_1',
        'match_name_2'

    ]
    # Call the function to delete alarms with the specified prefixes
    delete_cloudwatch_alarms_by_prefix(prefix_names)
