import json
import os
import requests

def sendEventDatadog(message):

    try:

        headers = {
            'Accept': 'application/json',
            'DD-API-KEY': os.environ.get('DD_API_KEY'),
            'Content-Type': 'application/json'
        }

        AlarmName = message['AlarmName']
        text = message['AlarmDescription']
        MetricName = message['Trigger']['MetricName']
        Region = message['Region']
        DimensionsValue = message['Trigger']['Dimensions'][0]['value']
        DimensionsName = message['Trigger']['Dimensions'][0]['name']
        alert_type = "error" if message['NewStateValue'] == "ALARM" else "success"

        url = "https://api.datadoghq.com/api/v1/events"
        
        payload = json.dumps({
            "title": AlarmName,
            "alert_type": alert_type,
            "host": "arn:aws:cloudwatch:us-east-1:414421394627",
            "priority": "normal",
            "text": text,
            "tags": [
                "team:CXP",
                "service:cloudwatch",
                f"MetricName:{MetricName}",
                f"Region:{Region}",
                f"DimensionsValue:{DimensionsValue}",
                f"DimensionsName:{DimensionsName}"
            ],
            "source_type_name": "amazon web services"
        })
        print('Iniciando envio do evento ao Datadog')
        response = requests.request("POST", url, headers=headers, data=payload)
        print('Resposta do evento:', response.text)
        return {
            'statusCode': 200,
            'body': response.text
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error sending event to Datadog')
        }

def lambda_handler(event, context):
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    sendEventDatadog(message)
