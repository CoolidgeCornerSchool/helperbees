import os

# to run locall
# start docker
# $ sam local start-api


ENV='prd'

INSTALL_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(INSTALL_DIR, '..')
S3_BUCKET = 'helperbees'

if ENV=='prd':
    API_BASE_URL = 'https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev'
elif ENV=='dev':
    API_BASE_URL = 'http://127.0.0.1:3000'
