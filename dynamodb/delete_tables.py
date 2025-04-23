import boto3

def delete_dynamodb_table(table_name):
    # Inicializa o cliente do DynamoDB
    dynamodb = boto3.client('dynamodb',region_name='us-east-1')

    try:
        # Obtém as informações da tabela
        table_info = dynamodb.describe_table(TableName=table_name)
        
        # Verifica se a proteção contra exclusão está habilitada
        if table_info['Table'].get('DeletionProtectionEnabled', False):
            print(f"Desativando proteção contra exclusão para a tabela '{table_name}'...")
            dynamodb.update_table(
                TableName=table_name,
                DeletionProtectionEnabled=False
            )
        
        # Exclui a tabela
        print(f"Excluindo a tabela '{table_name}'...")
        dynamodb.delete_table(TableName=table_name)
        print(f"Tabela '{table_name}' excluída com sucesso.")
    
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"A tabela '{table_name}' não foi encontrada.")
    except Exception as e:
        print(f"Erro ao excluir a tabela '{table_name}': {e}")

if __name__ == "__main__":
    # Lista de tabelas a serem excluídas
    tables_to_delete = [
        'table_1',
        'table_2',
    ]

    for table in tables_to_delete:
        delete_dynamodb_table(table)
