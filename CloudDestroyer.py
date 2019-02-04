import boto3
import random
import string
import Config
import json
import datetime


print "-> CLOUD MANAGER"
print "-> Running CloudDestroyer"

organizationClient = boto3.client('organizations', aws_access_key_id=Config.ROOT_ACCESS_ID, aws_secret_access_key=Config.ROOT_ACCESS_KEY)


all_accounts = [];
response = organizationClient.list_accounts()
nextToken = "ok";
while True:
        for account in response['Accounts']:
                all_accounts.append(account)
        if 'NextToken' in response.keys():
                nextToken = response['NextToken']
                response = organizationClient.list_accounts(NextToken = nextToken)
        else:
                break;


for account in all_accounts:
        accountId = account['Id']
        accountName = account['Name']
        
        if accountName in Config.ACCOUNTS:

                print ''
                print ' > Working with: ' + accountId + ' AWS Account (' + accountName + ')'

                #Assuming role in child AWS account
                stsClient = boto3.client('sts', aws_access_key_id=Config.ROOT_ACCESS_ID, aws_secret_access_key=Config.ROOT_ACCESS_KEY)
                newCredentials = stsClient.assume_role(
                    RoleArn='arn:aws:iam::' + accountId + ':role/AdminAccessRole',
                    RoleSessionName='AdminAccessRole',
                )

                #Creatin the group
                stepfunctions = boto3.client('stepfunctions', aws_access_key_id=Config.ROOT_ACCESS_ID, aws_secret_access_key=Config.ROOT_ACCESS_KEY);
                
                data = {}
                data["AccessKeyId"] = newCredentials["Credentials"]["AccessKeyId"]
                data["SecretAccessKey"] = newCredentials["Credentials"]["SecretAccessKey"]
                data["SessionToken"] = newCredentials["Credentials"]["SessionToken"]
                
                name = datetime.datetime.now().strftime("%m-%d-%H-%M-%S") + "-" + accountName
 
                stepfunctions.start_execution( stateMachineArn=Config.DESTROYER_ARN, name=name, input=json.dumps(data))          

print 'CLOUD MANAGER -> END'

