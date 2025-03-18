# 

### Invoke Function
```
@Amazon Q lambda invoke --payload {"action": "status", "instance": "bastion","env": "prd" } --function-name amazon-q-chat-on-off-ec2-instances --region us-east-1
```

### Alias to Function
```
@Amazon Q alias create ec2 lambda invoke --payload {"action": "$action", "instance": "$instance","env": "$env" } --function-name amazon-q-chat-on-off-ec2-instances --region us-east-1
```

### Invoke Function by Alias
```
@Amazon Q run lydians status webserver prd
@Amazon Q run lydians start webserver prd
@Amazon Q run lydians stop webserver prd
``


