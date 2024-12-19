import json
import boto3
from datetime import datetime as dt
import os

region = 'us-east-1'
queue_url = f'{os.environ['queue_url']}'
sns_arn = f'{os.environ['sns_topic']}'

def sqs():
    return boto3.client('sqs', region_name=region)

def sns():
    return boto3.client('sns', region_name=region)

def read_queue_msgs():
    messages = []
    receipt_handles = []
    
    while True:
        # Receba mensagens da fila SQS
        response = sqs().receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10  # Long polling
        )

        # Verifique se há mensagens na resposta
        if 'Messages' in response:
            for message in response['Messages']:
                message_body = json.loads(message['Body'])
                messages.append(message_body)
                receipt_handles.append(message['ReceiptHandle'])  # Salva o ReceiptHandle
        else:
            print("Nenhuma mensagem na fila.")
            break

    return messages, receipt_handles

def delete_messages(receipt_handles):
    for handle in receipt_handles:
        sqs().delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=handle
        )
        print(f'Mensagem com ReceiptHandle {handle} deletada.')

def lambda_handler(event, context):
    messages, receipt_handles = read_queue_msgs()
    message_text = ""

    for message in messages:
        timestamp = message['createdAt'][:26] + 'Z'
        message_text += (
            f"Doc: {message['docUuid']}\n"
            f"Valor: {message['amountInCents']}\n"
            f"Chave: {message['key']}\n"
            f"Arquivo: {message['fileId']}\n"
            f"Criação: {dt.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M:%S')}\n"
            "`----------------------------------------------------`\n"
        )
    
    print(message_text)
    
    try:

        # Publica a mensagem no tópico SNS para AWS chatbot consumir
        response = sns().publish(
            TopicArn=sns_arn,
            Message=json.dumps({
                "version": "1.0",
                "source": "custom",
                "content": {
                    "title": "SVR - Falha no Resgate de Saldo, Chave Pix Inválida!",
                    "description": message_text
                }
            })
        )
    
        # Verifica se o SNS publicou com sucesso
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            delete_messages(receipt_handles)  # Deleta mensagens apenas se o SNS enviou com sucesso

    except Exception as e:
        print(f"Erro ao publicar no SNS: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Mensagem enviada com sucesso!')
    }

# if __name__ == '__main__':
#    lambda_handler(1, 1)