import boto3
import pandas as pd

def list_s3_buckets_to_csv(output_file):
    # Create an S3 client
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    data = []

    try:
        # List all buckets
        response = s3_client.list_buckets()
        buckets = response['Buckets']
        
        # Loop through each bucket
        for bucket in buckets:
            bucket_name = bucket['Name']
            print(f'Bucket: {bucket_name}')
            bucket_info = {
                'Bucket Name': bucket_name,
                'Storage Class': 'N/A',  # Default value
                'Lifecycle Rules': 'N/A'  # Default value
            }
            
            # Get the default storage class
            try:
                objects_response = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in objects_response and len(objects_response['Contents']) > 0:
                    first_object = objects_response['Contents'][0]
                    bucket_info['Storage Class'] = first_object.get('StorageClass', 'N/A')
            except Exception as e:
                bucket_info['Storage Class'] = f'Error: {str(e)}'

            # Get the lifecycle rules
            try:
                lifecycle_response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
                rules = lifecycle_response.get('Rules', [])
                if rules:
                    rule_ids = [rule['ID'] for rule in rules]
                    bucket_info['Lifecycle Rules'] = ', '.join(rule_ids)
                print(f'Lifecycle Rules: {bucket_info["Lifecycle Rules"]}')
            except s3_client.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                    bucket_info['Lifecycle Rules'] = 'No lifecycle configuration'
                else:
                    bucket_info['Lifecycle Rules'] = f'Error: {str(e)}'

            data.append(bucket_info)

        # Create a pandas DataFrame and save it to CSV
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f'Data saved to {output_file}.')

    except Exception as e:
        print(f'Error listing buckets: {e}')

if __name__ == "__main__":
    output_file = 's3_buckets_info.csv'  # Name of the output CSV file
    list_s3_buckets_to_csv(output_file)
