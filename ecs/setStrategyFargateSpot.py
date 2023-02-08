import subprocess as sp
import codecs
import time

profileName = 'default'
regionName = 'us-east-1'
cluster = 'prd-ecs-cluster-name'

#Take all services name in cluster 
file = open('services.txt','r')
log = codecs.open("response_strategy.csv","w+","utf-8")        
#Save header
log.write(f"service;status;response\n")

count = 1 # To set delay
for each in file:
    
    if count != 1:
        #Set delay because if a lot of services restart in the same time, may to crash services dependencies 
        time.sleep(2 * 60) 
    try:
        objServices = sp.check_output(f'aws ecs update-service --cluster {cluster} --service {each.strip()} --capacity-provider-strategy capacityProvider=FARGATE,weight=1,base=2 capacityProvider=FARGATE_SPOT,weight=1,base=0 --force-new-deployment > /dev/null', shell=True)
        #Save Ok
        log.write(f"{each.strip()};Ok;{objServices}\n") 
        print(each, 'ok', objServices)
        
    except sp.CalledProcessError as grepexc :
        #Save error
        log.write(f"{each.strip()};Error;{grepexc}\n") #Salva erro
        print(each, 'Error', grepexc)
    count += 1
    
log.close()