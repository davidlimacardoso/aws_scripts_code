import json
import boto3

ecs = boto3.client('ecs')
sns = boto3.client('sns')

cluster_services = {
    'my-cluster-api' : [
        'my-service-1',
        'my-service-2',
        'my-service-3'
    ]
}


def put_sns_aws_chatbot(title, description):

    if not isinstance(description, str):
        description = '\n'.join(description)
    
    message = {
        "version": "1.0",
        "source": "custom",
        "content": {
            "title": title,
            "description": description
        }
    }

    sns.publish(
            TopicArn='arn:aws:sns:us-east-1:xxxxxxxxx:awschatbot-channel-report',
            Message = json.dumps(message)
        )
    return {
        'statusCode': 200
    }

def check_service_running(cluster, service):
    response = ecs.describe_services(
        cluster=cluster,
        services=[service]
    )

    if response['services'][0]['desiredCount'] == 0:
        return 0

    return response['services'][0]['desiredCount']

def update_service(cluster, service, desiredCount):
    print(cluster, service, desiredCount)
    response = ecs.update_service(
        cluster=cluster,
        service=service,
        desiredCount=desiredCount
    )
    
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return False

    return True

def lambda_handler(event, context):
    
    action = event.get('action', None).lower()
    desiredCount = 1

    if action.lower() in ['stop', 'start']:
        
        result = []

        for cluster, services in cluster_services.items():
            for service in services:

                if check_service_running(cluster, service) > 0 and action == 'start' :
                    result.append('Service {} already started!'.format(service))
                
                elif check_service_running(cluster, service) == 0 and action == 'stop' :
                    result.append('Serviçe {} already stopped!'.format(service))

                else:
                    if action == 'stop':
                        desiredCount = 0

                    translate_action = {
                        'stop': 'stopped',
                        'start': 'started'
                    }

                    if update_service(cluster, service, desiredCount):
                        result.append('Service {} {} with success!'.format(service, translate_action[action]))
                    else:
                        result.append('Fail to {} service {}!'.format(translate_action[action]), service)
                    
            put_sns_aws_chatbot('ECS Cluster {}'.format(cluster) , result)

    else:
        put_sns_aws_chatbot('ECS Cluster', 'Invalid action!\n Only are accept "stop" or "start"!')

