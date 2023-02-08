import boto3
import json
from botocore.exceptions import ClientError

secret_name = "name_of_secret_manager"
region = "us-east-1"

def get_secret():

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = json.loads(get_secret_value_response['SecretString'])
        return secret['API_KEY']
    
    except ClientError as e:
        return e


print(get_secret())