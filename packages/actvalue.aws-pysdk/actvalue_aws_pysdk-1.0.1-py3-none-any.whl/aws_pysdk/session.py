import os
import boto3
from aws_lambda_powertools.utilities import parameters

# AWS init
AWS_PROFILE = os.getenv('AWSPROFILE', 'default')
AWS_REGION = os.getenv('AWSREGION', 'eu-west-1')
ENV = os.getenv('ENV', 'development')

# Initialize session with profile if needed
if AWS_PROFILE != 'default' and ENV == 'development':
    session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
else:
    session = boto3.Session(region_name=AWS_REGION)

# Client init
s3 = session.client('s3')
ssm_provider = parameters.SSMProvider(boto3_session=session)
lambda_client = session.client('lambda')