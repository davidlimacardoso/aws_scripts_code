import json, boto3, codecs

file = codecs.open("response_messages.txt","w+","utf-8")
file.write('status_code;message_id;body\n')

#Set Region
region = 'us-east-1'
#Set Queue Name
queueName = 'partner-prd-call-queue'

# Get the service resource
sqs = boto3.resource('sqs',region_name=region)

# Get the queue. This returns an SQS.Queue instance
queue = sqs.get_queue_by_name(QueueName=queueName)

#Send messages
def send_message(msg):
    response = queue.send_message(MessageBody=msg)
    print(response.get('MessageId'))
    print(response.get('MD5OfMessageBody'))
    return response

#Your messages body here!
messages = []


for  msg in messages:
    response = send_message(json.dumps(msg))
    print(f"{response.get('ResponseMetadata')['HTTPStatusCode']} - messageId:{response.get('MessageId')}")
    file.write(f"{response.get('ResponseMetadata')['HTTPStatusCode']};messageId:{response.get('MessageId')};{msg}\n")
    
    
file.close()