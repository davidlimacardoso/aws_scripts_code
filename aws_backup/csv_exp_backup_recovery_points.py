from pathlib import Path
import boto3
import pandas as pd

region = "us-west-2"

def backup():
    return boto3.client('backup',region_name=region)

# Extract recovery poin id inside recovery point ARN
def extract_recovery_point_id(arn):
    if not arn:
        return None
    # List of possible identifiers to split on
    identifiers = [
        'cluster-snapshot:',
        'recovery-point:',
        'snapshot:',
        'backup:'
    ]
    
    for identifier in identifiers:
        if identifier in arn:
            return arn.split(identifier)[-1]
        
    return arn.split(':')[-1]

def main():
    output = []
    bkp = backup()
    vaults = bkp.list_backup_vaults()

    for vault in vaults.get('BackupVaultList', []):
        describe = bkp.list_recovery_points_by_backup_vault(
            BackupVaultName=vault.get('BackupVaultName')
        )
        for point in describe.get('RecoveryPoints'):
           
            output.append({
                'backup account': vault.get('BackupVaultArn').split(':')[4] ,
                'status block vault': vault.get('Locked') ,
                'vault name': point.get('BackupVaultName'),
                'recovery point id': extract_recovery_point_id(point.get('RecoveryPointArn')),
                'resource name': point.get('ResourceName'),
                'resource id': point.get('ResourceArn').split(':')[-1] ,
                'resource type': point.get('ResourceType'),
                'lifecycle delete after days': point.get('Lifecycle',{}).get('DeleteAfterDays',None),
                'source backup account': point.get('SourceBackupVaultArn').split(':')[4] if point.get('SourceBackupVaultArn') else None,
                'creation timestamp': point.get('CreationDate'),
                'creation date': point.get('CreationDate').strftime('%Y-%m-%d'),
                'status': point.get('Status')
            })

    export_file_name = "aws_backup_export_list.csv"
    df = pd.DataFrame(output)
    filePath = Path(export_file_name)
    filePath.parent.mkdir(parents=True, exist_ok=True)  
    df.to_csv(filePath, sep=';',header=True, index=False,doublequote=True)

    print(f"Export Generated in ${export_file_name}!")
    

if __name__ == "__main__":
    main()
