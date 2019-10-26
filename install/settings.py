import os

# to run locall
# start docker
# $ sam local start-api


ENV='prd'

INSTALL_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(INSTALL_DIR, '..')
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
