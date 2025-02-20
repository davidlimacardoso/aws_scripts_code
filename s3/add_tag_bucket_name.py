import boto3

def tag_s3_bucket(bucket_name):
    # Create an S3 client
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Define the new tag
    new_tag = {
        'Key': 'Name',
        'Value': bucket_name
    }

    try:
        # Retrieve existing tags for the bucket
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        current_tags = response['TagSet']

        # Check if the 'Name' tag already exists and update if necessary
        for tag in current_tags:
            if tag['Key'] == 'Name':
                tag['Value'] = bucket_name
                break
        else:
            # If the 'Name' tag does not exist, add the new tag
            current_tags.append(new_tag)

        # Update the bucket's tags
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': current_tags
            }
        )
        
        print(f'Tag "Name" added to bucket "{bucket_name}".')
    
    except s3_client.exceptions.NoSuchTagSet:
        # If there are no tags, create a new set of tags
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [new_tag]
            }
        )
        print(f'Tag "Name" created in bucket "{bucket_name}".')
    
    except Exception as e:
        print(f'Error adding tag to bucket "{bucket_name}": {e}')

def tag_all_buckets():
    # Create an S3 client
    s3_client = boto3.client('s3', region_name='us-east-1')

    try:
        # List all buckets
        response = s3_client.list_buckets()
        buckets = response['Buckets']
        
        # Loop through each bucket and add the tag
        for bucket in buckets:
            bucket_name = bucket['Name']
            tag_s3_bucket(bucket_name)

    except Exception as e:
        print(f'Error listing buckets: {e}')

if __name__ == "__main__":
    tag_all_buckets()
