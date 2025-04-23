import boto3
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook

def copy_backup_daily_to_yearly(region, recovery_point_arn, vault_name):
    """
    Copia os backups diários do DynamoDB para o vault de backup anual.

    Args:
        region_name (str): A região da AWS.
    """
    print(f"{recovery_point_arn} - {vault_name}")

    IdempotencyToken = f"{recovery_point_arn.split(':')[-1]}-{datetime.now().strftime('%Y-%m-%d')}"

    backup_client = boto3.client('backup', region_name=region)

    # Copia o ponto de recuperação para o vault de backup anual
    try:
        response = backup_client.start_copy_job(
            RecoveryPointArn=recovery_point_arn,
            SourceBackupVaultName=vault_name,
            DestinationBackupVaultArn='arn:aws:backup:us-east-1:xxxxxxxxxx:backup-vault:lock-vault-yearly-backup-nosql',
            IamRoleArn='arn:aws:iam::xxxxxxx:role/service-role/AWSBackupDefaultServiceRole',
            IdempotencyToken=IdempotencyToken,
            Lifecycle={
                'MoveToColdStorageAfterDays': 7,
                'DeleteAfterDays': 1825,
                'OptInToArchiveForSupportedResources': False
            }
        )
        if 'ResponseMetadata' in response:
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(f"Backup copiado com sucesso: {response}")
            else:
                print(f"Erro ao copiar o backup: {response}")
    except Exception as e:
        print(f"Erro ao copiar o backup: {e}")



def match_tables_get_latest_backup(vault_region, match_tables):


    table_data = []
    collect_backup_creation_date = []

    for each in vault_region:
        region = each['region']
        vault_name = each['vault_name']

        backup_client = boto3.client('backup', region_name=region)
        try:
            backup_paginator = backup_client.get_paginator('list_recovery_points_by_backup_vault')
            
            for page in backup_paginator.paginate(BackupVaultName=vault_name):

                for recovery_point in page['RecoveryPoints']:
                    table_name = recovery_point['ResourceArn'].split(':')[-1].replace('table/', '')
                    
                    if table_name in match_tables:
                        
                        # Verifica se o ponto de recuperação é mais recente que 30 dias
                        if recovery_point['Lifecycle']['DeleteAfterDays'] < 30:

                            collect_backup_creation_date.append({
                                'Region': region,
                                'TableName': table_name,
                                'CreationDate': recovery_point['CreationDate'],
                                'RecoveryPointArn': recovery_point['RecoveryPointArn']
                            })
                            

            # Agrupar backups por tabela e pegar o mais recente
            if collect_backup_creation_date:
                latest_backups = {}
                
                for backup in collect_backup_creation_date:
                    table_name = backup['TableName']
                    creation_date = backup['CreationDate']

                    # Verifica se já existe um backup registrado para a tabela
                    if table_name not in latest_backups:
                        latest_backups[table_name] = backup
                    else:
                        # Compara as datas e mantém o mais recente
                        if creation_date > latest_backups[table_name]['CreationDate']:
                            latest_backups[table_name] = backup

                # Adiciona os backups mais recentes à lista final
                for backup in latest_backups.values():
                    table_data.append({
                        'tableName': backup['TableName'],
                        'backupRegion': backup['Region'],
                        'vaultName': vault_name,
                        'CreationDate': backup['CreationDate'],
                        'RecoveryPointArn': backup['RecoveryPointArn']
                    })

    
        except Exception as e:
            print(f"{e}")


    for backup in table_data:
        copy_backup_daily_to_yearly(
                backup['backupRegion'],
                backup['RecoveryPointArn'],
                backup['vaultName']
            )

if __name__ == "__main__":

    match_tables = [
        'prod_tabela_1',
        'prod_tabela_2'
    ]

    vault_region = [
        {'region': 'us-east-1', 'vault_name': 'lock-vault-daily-backup-nosql'}
    ]

    match_tables_get_latest_backup(vault_region, match_tables)
