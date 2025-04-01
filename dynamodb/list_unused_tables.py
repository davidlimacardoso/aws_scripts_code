import boto3
from datetime import datetime, timedelta
import pandas as pd

def get_unused_dynamodb_tables(region_name='us-east-1', days=30):
    """
    Lista as tabelas do DynamoDB que não tiveram atividade de leitura, escrita ou query
    nos últimos 'days' dias e salva em um arquivo Excel.

    Args:
        region_name (str): A região da AWS.
        days (int): O número de dias para verificar a inatividade.

    Returns:
        list: Uma lista de nomes de tabelas não utilizadas.
    """

    dynamodb = boto3.client('dynamodb', region_name=region_name)
    cloudwatch = boto3.client('cloudwatch', region_name=region_name)

    # Obter a lista de todas as tabelas do DynamoDB
    table_names = []
    paginator = dynamodb.get_paginator('list_tables')
    for page in paginator.paginate():
        table_names.extend(page['TableNames'])

    unused_tables = []
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    table_data = []  # Lista para armazenar os dados das tabelas

    for table_name in table_names:
        # Ignorar tabelas que não começam com 'prod_'
        if not table_name.startswith('prod_'):
            continue
        print(f"Verificando a tabela: {table_name}")

        # Consultar as métricas de leitura, escrita e query do CloudWatch
        read_response = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'm1',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/DynamoDB',
                            'MetricName': 'ConsumedReadCapacityUnits',
                            'Dimensions': [
                                {
                                    'Name': 'TableName',
                                    'Value': table_name
                                },
                            ]
                        },
                        'Period': 86400,  # 1 dia
                        'Stat': 'Sum',
                    },
                    'ReturnData': True,
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
        )

        write_response = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'm2',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/DynamoDB',
                            'MetricName': 'ConsumedWriteCapacityUnits',
                            'Dimensions': [
                                {
                                    'Name': 'TableName',
                                    'Value': table_name
                                },
                            ]
                        },
                        'Period': 86400,  # 1 dia
                        'Stat': 'Sum',
                    },
                    'ReturnData': True,
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
        )
        
        query_response = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'm3',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/DynamoDB',
                            'MetricName': 'SuccessfulRequests',
                            'Dimensions': [
                                {
                                    'Name': 'TableName',
                                    'Value': table_name
                                },
                                {
                                    'Name': 'Operation',
                                    'Value': 'Query'
                                }
                            ]
                        },
                        'Period': 86400,  # 1 dia
                        'Stat': 'Sum',
                    },
                    'ReturnData': True,
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
        )

        # Verificar se houve alguma atividade de leitura, escrita ou query
        read_values = read_response['MetricDataResults'][0]['Values']
        write_values = write_response['MetricDataResults'][0]['Values']
        query_values = query_response['MetricDataResults'][0]['Values']


        total_read = sum(read_values) if read_values else 0
        total_write = sum(write_values) if write_values else 0
        total_query = sum(query_values) if query_values else 0

        is_unused = total_read == 0 and total_write == 0 and total_query == 0
        if is_unused:
            unused_tables.append(table_name)

        translate_is_unused = 'Sim' if is_unused else 'Não'

        # Armazenar os dados da tabela
        table_data.append({
            'TableName': table_name,
            'TotalReadCapacityUnits': total_read,
            'TotalWriteCapacityUnits': total_write,
            'TotalQueryRequests': total_query,
            'IsUnused': translate_is_unused
        })

    # Criar um DataFrame do pandas
    df = pd.DataFrame(table_data)

    # Salvar o DataFrame em um arquivo Excel
    excel_filename = 'dynamodb_table_unusage.xlsx'
    df.to_excel(excel_filename, index=False)
    print(f"Dados salvos em {excel_filename}")

    return unused_tables

# Exemplo de uso
if __name__ == "__main__":
    days = 90

    unused_tables = get_unused_dynamodb_tables(region_name='us-east-1', days=days)
    if unused_tables:
        print(f"Tabelas do DynamoDB não utilizadas nos últimos {days} dias:")
        for table_name in unused_tables:
            print(f"- {table_name}")
    else:
        print(f"Nenhuma tabela do DynamoDB não utilizada encontrada nos últimos {days} dias.")
