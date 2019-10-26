import os

# to run locally, start docker, then
# $ sam local start-api

# This will start a web service listening at http://localhost:3000
# with the Lambdas defined in install/template.yml

# If ENV='prd', deploy_lambdas.py will push code to AWS and update the lambdas in the cloud.
# If ENV='dev', run 'sam local start-api' to serve lambdas at localhost.
ENV='prd'

INSTALL_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(INSTALL_DIR, '..')

# Running deploy_lambdas.py will zip up Lambda code and place it into this S3 bucket
S3_BUCKET = 'helperbees'

# CLEAN_BUILD=False is faster when running deploy_lambdas.py
# if CLEAN_BUILD=False, use existing functions.zip and just update files in "/functions/*.py"
# if CLEAN_BUILD=True, delete functions.zip and start fresh, adding all files in /lib
CLEAN_BUILD = False 

# ENV='dev' is faster when running deploy_lambdas.py.
# ENV='prd' makes updated code available on the live site (helperbees.org) when running deploy_lambdas.py
# if ENV='prd', update function definitions on AWS Lambda
if ENV=='prd':
    API_BASE_URL = 'https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev'
elif ENV=='dev':
    API_BASE_URL = 'http://127.0.0.1:3000'
