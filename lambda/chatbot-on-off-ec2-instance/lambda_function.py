import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')
snsArn = 'arn:aws:sns:us-east-1:xxxxxxxxxx:chatbot-on-off-instance'

def instancesToExecute(env, instance, action):
   
    instanceId = {
        "hml": {
            "bastion": "i-02d414736fb454b73",
            "webserver": "i-02d414736fb454b73"
        },
        "prd": {
            "bastion": "i-02d414736fb454b73",
            "webserver": "i-02d414736fb454b73"
        }
    }

    return instanceId.get(env, {}).get(instance, None)

def sendSns(title, message):
    # Envia uma mensagem customizada para o SNS topic > AWS Chatbot
    sns = boto3.client('sns', region_name='us-east-1')
    message = {
        "version": "1.0",
        "source": "custom",
        "content": {
            "title": title,
            "description": message
        }
    }
    try:
        sns.publish(TopicArn=snsArn, Message = json.dumps(message))
        exit()
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    

def checkInstanceStatus(env, instance, action):
    instanceId = instancesToExecute(env, instance, 'status')
    result = ec2.describe_instances(InstanceIds=[instanceId])
    status = result['Reservations'][0]['Instances'][0]['State']['Name']
    message = ''

    if status == 'running' and action == 'start':
        print(f'A instância {instance} ({instanceId}) do ambiente {env} já está *ligada*')
        message = f'A instância {instance} ({instanceId}) do ambiente {env} já está * ligada *'
        sendSns('Ação não permitida!', message)
        exit()
    
    if status == 'stopped' and action == 'stop':
        print(f'A instância {instance} ({instanceId}) do ambiente {env} já está *desligada*')
        message = f'A instância {instance} ({instanceId}) do ambiente {env} já está * desligada *'
        sendSns('Ação não permitida!', message)
        exit()


def lambda_handler(event, context):
    print(event)

    """ Function to start and stop EC2 instances """

    if not event.get('action') or event['action'] not in ['start', 'stop', 'status']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Ação inválida! Favor inserir status, start ou stop!'})
        }

    if not event.get('instance') or event['instance'] not in ['rdp', 'processamento']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Favor inserir a instância correta rdp ou processamento!'})
        }

    if not event.get('env') or event['env'] not in ['hml', 'prd']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Favor inserir o ambiente correto hml ou prd!'})
        }

    """ Get the action, instance and environment """
    action = event.get('action', None)
    instance = event.get('instance', None)
    env = event.get('env', None)

    """ Get the instance id """
    instanceId = instancesToExecute(env, instance, action)
    print(f"Action: {action}")
    print(f"Id da instancia {instance} do ambiente de {env} é {instanceId}...")

    """ Get the status of the instances """

    instanceId = instancesToExecute(env, instance, action)
    message = ''

    if action == 'status':
       
        try:
            result = ec2.describe_instances(InstanceIds=[instanceId])
            status = result['Reservations'][0]['Instances'][0]['State']['Name']
            message = f'A instância {instance} ({instanceId}) do ambiente {env} está * {status} *'
            print(message)
            sendSns('Status da instância', message)

        except Exception as e:
            print(e)
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
        
    else:
        """ Start or stop the instances """

        
        checkInstanceStatus(env, instance, action)

        try:

          result = {}
          response = {}
          if action == 'stop':
            result = ec2.stop_instances(InstanceIds=[instanceId])
            for r in result['StoppingInstances']:
              response[r['InstanceId']] = r['CurrentState']['Name']
              message = f'A instância { instance.upper() } ({instanceId}) do ambiente {env} está sendo * desligada *'

          if action == 'start':
            result = ec2.start_instances(InstanceIds=[instanceId])
            for r in result['StartingInstances']:
              response[r['InstanceId']] = r['CurrentState']['Name']
              message = f'A instância { instance.upper() } ({instanceId}) do ambiente {env} está sendo * ligada *\nAguarde alguns minutos para acessar o ambiente...'
          
          print(response)
          print(message)
          sendSns(f'Ação executada *{action}*', message)

        except Exception as e:
          print(e)
          message = f'Erro ao executar a ação {action} na instância {instance} ({instanceId}) do ambiente {env}\n{str(e)}'
          return {
            'statusCode': 500,
            'body': message
          }

# if __name__ == '__main__':
#     lambda_handler({
#         "action": "start",
#         "instance": "bastion",
#         "env": "hml"
#     }, None)
