import boto3
import codecs

#Save responses
file = codecs.open("data.txt","w+","utf-8")

#Set Region
region = 'us-east-1'

#Set AWS Resource
resource = 'ecs'
client = boto3.client(resource,region_name=region)

#List ECS Clusters
def list_prd_cluster():
    response = client.list_clusters(
        # maxResults=100   #Limit results 
    )
    
    #MATCH KEYWORDS (prod, dev,hml) is separate only specifics clusters 
    keywords = ['prd','prod'] 
    matching = [s for s in response['clusterArns'] if any(xs in s for xs in keywords)]
    return matching
    

#List ECS Services
def list_services(clusters):
    array = {}
    
    for cluster in clusters:
        
        response = client.list_services(
            cluster=cluster,
        )
        array[cluster] = response['serviceArns']
        
    return array


#List Tags on Services 
def list_tags_service(services):
    
    tags =[]
    for service in services:
        
        for s in service:
            
            try:
                response = client.list_tags_for_resource(
                    resourceArn=s,
                )
                tags.append(response['tags'])

            except:
                continue

# Trait cluster ARNS -- Descontinued
def helper(values, service):
    array = {}
    cluster = []
    
    for each in values:

        cluster.append(each.split('/')[1])
        
    array['cluster'] = cluster
    print('\n',array)


clusters = list_prd_cluster()
services = list_services(clusters)

#Foreach services and list your tags
for s in services:
    for x in services[s]:
        try:
                response = client.list_tags_for_resource(
                resourceArn=x,
                )
                print(response['tags'])

        except:
            continue

# print(helper(clusters,'cluster'))
file.close()


