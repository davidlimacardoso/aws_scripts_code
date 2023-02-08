import subprocess as sp
import json
import codecs

profileName = 'default'
regionName = 'us-east-1'

log = codecs.open("response.csv","w+","utf-8")       
#CSV Header 
log.write(f"cluster;service;desiredCount;runningCount;pendingCount;capacityProviderStrategy\n") 

#List Clusters
objClusters = sp.getoutput(f'aws ecs list-clusters --profile {profileName} --region {regionName}')

for cluster in json.loads(objClusters)['clusterArns']:
    cluster = cluster.split('cluster/')[1]
    
    #Eg. to take only prod cluster 
    if 'prod' in cluster:
        print(cluster)
        
        #List Services
        objServices = sp.getoutput(f'aws ecs list-services --cluster {cluster} --profile {profileName} --region {regionName}')
        for service in  json.loads(objServices)['serviceArns']:
            service = service.split(f'service/')[1]
            try:
                service = service.split(f'{cluster}/')[1]
            except:
                pass
            
            # print('\t', f"{service}")
            
            objDetails = sp.getoutput(f'aws ecs describe-services --services {service} --cluster {cluster} --profile {profileName} --region {regionName}')
            objDetails = json.loads(objDetails)['services'][0]
                        
            capacityProviderStrategy = ''
            try:
                capacityProviderStrategy = objDetails['capacityProviderStrategy']
            except: 
                capacityProviderStrategy = objDetails['launchType']
            
            print('\t',service, 'desiredCount:',objDetails['desiredCount'],'runningCount:', objDetails['runningCount'],'pendingCount:','pendingCount:',objDetails['pendingCount'],'capacityProviderStrategy:',capacityProviderStrategy)
            #Trait and save responses to CSV
            log.write(f"{cluster};{service};{objDetails['desiredCount']};{objDetails['runningCount']};{objDetails['pendingCount']};{capacityProviderStrategy}\n")
        break
log.close()