import boto3
import pandas as pd
from datetime import datetime

def get_dynamodb_tables_and_backups(region_name='us-east-1'):
    """
    Lista as tabelas do DynamoDB e seus backups (tanto de usuário quanto do AWS Backup),
    salvando os resultados em um arquivo Excel.

    Args:
        region_name (str): A região da AWS.
    """

    dynamodb = boto3.client('dynamodb', region_name=region_name)
    backup_client = boto3.client('backup', region_name=region_name)

    # Obter a lista de todas as tabelas do DynamoDB
    table_names = []
    paginator = dynamodb.get_paginator('list_tables')
    for page in paginator.paginate():
        table_names.extend(page['TableNames'])

    table_data = []

    for table_name in table_names:

        if not table_name.startswith('prod_'):
            continue
        print(f"Verificando a tabela: {table_name}")

        # Obter informações da tabela
        table_description = dynamodb.describe_table(TableName=table_name)['Table']
        table_arn = table_description['TableArn']
        table_size_gb = round(table_description['TableSizeBytes'] / (1024 ** 3), 2)  # Convert bytes to GB
        table_creation_date = table_description['CreationDateTime'].strftime('%Y-%m-%d %H:%M:%S')

        # Obter backups de usuário (on-demand)
        user_backups = []
        backup_paginator = dynamodb.get_paginator('list_backups')
        for page in backup_paginator.paginate(TableName=table_name):
            for backup in page['BackupSummaries']:
                user_backups.append(backup)

        # Obter backups do AWS Backup
        aws_backups = []
        try:
            backup_paginator = backup_client.get_paginator('list_recovery_points_by_resource')
            for page in backup_paginator.paginate(ResourceArn=table_arn):
                for recovery_point in page['RecoveryPoints']:
                    aws_backups.append(recovery_point)
        except Exception as e:
            print(f"Erro ao listar backups do AWS Backup para {table_name}: {e}")
            aws_backups = []
        
        total_backups = len(aws_backups)

        # Determinar a data do último backup
        last_backup_date = None
        all_backup_dates = []

        # Adicionar datas dos backups de usuário
        for backup in user_backups:
            try:
                all_backup_dates.append(backup['BackupCreationDateTime'])
            except Exception as e:
                print(f"Erro ao obter data de backup de usuário para {table_name}: {e}, backup: {backup}")

        # Adicionar datas dos backups do AWS Backup
        for backup in aws_backups:
            try:
                if 'CreationTime' in backup:
                    all_backup_dates.append(backup['CreationTime'])
                elif 'CreationDate' in backup:
                    all_backup_dates.append(backup['CreationDate'])
                elif 'BackupCreateDate' in backup:  # Usar chave alternativa se existir
                    all_backup_dates.append(backup['BackupCreateDate'])
                else:
                    print(f"Aviso: Nenhuma chave de data de criação encontrada para backup: {backup}")
            except Exception as e:
                print(f"Erro ao obter data de backup do AWS Backup para {table_name}: {e}, backup: {backup}")

        if all_backup_dates:
            try:
                last_backup_date = max(all_backup_dates).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"Erro ao formatar a data do último backup para {table_name}: {e}, datas: {all_backup_dates}")
                last_backup_date = "Erro ao determinar a data"
        else:
            last_backup_date = "Nenhum backup encontrado"

        # Armazenar os dados da tabela e seus backups
        table_data.append({
            'TableName': table_name,
            'TableArn': table_arn,
            'TableSizeGB': table_size_gb,
            'TableCreationDate': table_creation_date,
            'TotalBackups': total_backups,
            'LastBackupDate': last_backup_date
        })

    # Criar um DataFrame do pandas
    df = pd.DataFrame(table_data)

    # Salvar o DataFrame em um arquivo Excel
    excel_filename = 'dynamodb_tables_and_backups.xlsx'
    df.to_excel(excel_filename, index=False)
    print(f"Dados salvos em {excel_filename}")

# Exemplo de uso
if __name__ == "__main__":
    get_dynamodb_tables_and_backups(region_name='us-east-1')
