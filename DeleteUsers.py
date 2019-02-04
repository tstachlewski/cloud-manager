import boto3
import random
import string
import Config


print "-> CLOUD MANAGER"
print "-> Creating new User group in AWS Accounts"

organizationClient = boto3.client('organizations', aws_access_key_id=Config.ROOT_ACCESS_ID, aws_secret_access_key=Config.ROOT_ACCESS_KEY)


iterator = 0

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

                iterator = iterator + 1
                print '[' + str(iterator) + "]"
                print ' > Working with account (' + accountName + ')'
                
                print ''
                print ' > Working with: ' + accountId + ' AWS Account (' + accountName + ')'

                #Assuming role in child AWS account
                stsClient = boto3.client('sts', aws_access_key_id=Config.ROOT_ACCESS_ID, aws_secret_access_key=Config.ROOT_ACCESS_KEY)
                newCredentials = stsClient.assume_role(
                    RoleArn='arn:aws:iam::' + accountId + ':role/AdminAccessRole',
                    RoleSessionName='AdminAccessRole',
                )

                iam = boto3.client('iam',aws_access_key_id = newCredentials["Credentials"]["AccessKeyId"], aws_secret_access_key = newCredentials["Credentials"]["SecretAccessKey"], aws_session_token = newCredentials["Credentials"]["SessionToken"]) 
                
                users = iam.list_users()["Users"]
                for user in users:
                        groups = iam.list_groups_for_user( UserName=user["UserName"] )["Groups"]
                        for group in groups:
                                iam.remove_user_from_group( GroupName=group["GroupName"], UserName=user["UserName"] )
                        
                        keys = iam.list_access_keys(UserName = user["UserName"])['AccessKeyMetadata']
                        for key in keys:
                                iam.delete_access_key(UserName = user["UserName"],AccessKeyId = key['AccessKeyId'])

                        
                        try:
                                iam.delete_login_profile(UserName = user["UserName"]);
                        except:
                                ok = "ok";
                                
                        iam.delete_user( UserName=user["UserName"] )
                        print("Deleting User (" + user["UserName"] + ")")
                
                groups = iam.list_groups()["Groups"]
                for group in groups:
                        
                        policies = iam.list_attached_group_policies( GroupName=group["GroupName"] )["AttachedPolicies"]
                        for policy in policies:
                                response = iam.detach_group_policy( GroupName=group["GroupName"], PolicyArn=policy["PolicyArn"])

                        print("Deleting Group: " + group["GroupName"]);
                        iam.delete_group( GroupName= group["GroupName"] )
                        
                roles = iam.list_roles()["Roles"]
                for role in roles:
                        role_name = role["RoleName"] 

                        if not role_name.startswith("AWSServiceRoleFor"):
                                if not role_name.startswith("AWSReservedSSO"):
                                        if "AdminAccessRole" != role_name:
                                                policies = iam.list_attached_role_policies( RoleName=role_name )["AttachedPolicies"]
                                                for policy in policies:
                                                        policy_arn = policy["PolicyArn"]
                                                        iam.detach_role_policy( RoleName=role_name, PolicyArn= policy_arn )
                                                        
                                                profiles = iam.list_instance_profiles_for_role( RoleName= role_name )["InstanceProfiles"]
                                                for profile in profiles:
                                                        response = iam.remove_role_from_instance_profile( InstanceProfileName=profile['InstanceProfileName'], RoleName= role_name )
                                                        iam.delete_instance_profile( InstanceProfileName=profile['InstanceProfileName'] )
        
                                                policies = iam.list_role_policies( RoleName=role_name )["PolicyNames"]
                                                for policy in policies:
                                                        iam.delete_role_policy( RoleName=role_name, PolicyName=policy )
                                                
                                                print ("Deleting IAM Role (" + role_name + ")")
                                                
                                                iam.delete_role( RoleName=role_name )

print 'CLOUD MANAGER -> END'

