NEW_ACCOUNTS = [
        ["Email1","Account1"],
        ["Email2","Account2"]
        ]

import boto3
import random
import string
import Config


print "-> CLOUD MANAGER"
print "-> Creating new AWS Accounts"

organizationClient = boto3.client('organizations', aws_access_key_id=Config.ROOT_ACCESS_ID, aws_secret_access_key=Config.ROOT_ACCESS_KEY)

for account in NEW_ACCOUNTS:
        response = organizationClient.create_account(
                Email=account[0],
                AccountName=account[1],
                RoleName='AdminAccessRole',
                IamUserAccessToBilling='ALLOW'
        )
        print "Creating " + account[1] + "(" + account[0] + ") AWS account"



print 'CLOUD MANAGER -> END'

