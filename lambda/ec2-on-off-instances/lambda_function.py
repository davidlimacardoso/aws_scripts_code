import boto3
import json

ec2 = boto3.client('ec2', region_name='us-east-1')

def lambda_handler(event, context):

  """ Function to start and stop EC2 instances based on tags """
  """ Tags: ON-OFF: true """

  while not event.get('action', None) or event['action'] not in ['start', 'stop'] :
    return {
      'statusCode': 400,
      'body': json.dumps({'error': 'action key and value is required'})
    }

  action = event.get('action', None)

  try:

    response = ec2.describe_instances(
      Filters=[
        {
          'Name': 'tag:ON-OFF',
          'Values': ['true']
        }
      ]
    ).get('Reservations', [])
  
    instanceIds = []
    for r in response:
      for i in r['Instances']:
        instanceIds.append(i['InstanceId'])

  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({'error': str(e)})
    }

  try:

    result = {}
    response = {}
    if action == 'stop':
      result = ec2.stop_instances(InstanceIds=instanceIds)
      for r in result['StoppingInstances']:
        response[r['InstanceId']] = r['CurrentState']['Name']
      
    else:
      result = ec2.start_instances(InstanceIds=instanceIds)
      for r in result['StartingInstances']:
        response[r['InstanceId']] = r['CurrentState']['Name']
    
    return {
      'statusCode': 200,
      'body': json.dumps(response, default=str) 
    }

  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({'error': str(e)})
    }
