import boto3
import random
import string
import Config


print "-> CLOUD MANAGER"

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

iterator = 0

for account in all_accounts:
        accountId = account['Id']
        accountName = account['Name']
        
        if accountName in Config.ACCOUNTS:

                iterator = iterator + 1
                print '[' + str(iterator) + "]"
                print ' > Working with account (' + accountName + ')'

                #Assuming role in child AWS account
                stsClient = boto3.client('sts', aws_access_key_id=Config.ROOT_ACCESS_ID, aws_secret_access_key=Config.ROOT_ACCESS_KEY)
                newCredentials = stsClient.assume_role(
                    RoleArn='arn:aws:iam::' + accountId + ':role/AdminAccessRole',
                    RoleSessionName='AdminAccessRole',
                )

                #Creatin the group
                iam = boto3.client('iam',aws_access_key_id = newCredentials["Credentials"]["AccessKeyId"], aws_secret_access_key = newCredentials["Credentials"]["SecretAccessKey"], aws_session_token = newCredentials["Credentials"]["SessionToken"]) 

                #Creatin the group
                iam = boto3.client('iam',aws_access_key_id = newCredentials["Credentials"]["AccessKeyId"], aws_secret_access_key = newCredentials["Credentials"]["SecretAccessKey"], aws_session_token = newCredentials["Credentials"]["SessionToken"]) 
                iam.create_group(GroupName = Config.USERS_GROUP_NAME)

                #Attaching policies to the group
                iam.attach_group_policy(GroupName = Config.USERS_GROUP_NAME, PolicyArn = "arn:aws:iam::aws:policy/AdministratorAccess")
                #iam.attach_group_policy(GroupName = Config.USERS_GROUP_NAME, PolicyArn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess")
                #iam.attach_group_policy(GroupName = Config.USERS_GROUP_NAME, PolicyArn = "arn:aws:iam::aws:policy/AmazonS3FullAccess")
                #iam.attach_group_policy(GroupName = Config.USERS_GROUP_NAME, PolicyArn = "arn:aws:iam::aws:policy/AmazonPollyFullAccess")

                #Creating admin user
                password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
                iam.create_user(UserName = Config.USER)
                iam.create_login_profile(UserName = Config.USER, Password=password, PasswordResetRequired=False)
                iam.add_user_to_group(GroupName = Config.USERS_GROUP_NAME, UserName = Config.USER)
                #keys = iam.create_access_key(UserName = Config.USER)['AccessKey']
                print ' Link: https://console.aws.amazon.com/console/home'
                print ' - Account: ' + accountId
                print ' - Login: ' + Config.USER
                print ' - Password: ' + password
                #print ' - AccessKeyId: ' + keys['AccessKeyId']
                #print ' - SecretAccessKey: ' + keys['SecretAccessKey']
                print ''
                
                
print 'CLOUD MANAGER -> END'

