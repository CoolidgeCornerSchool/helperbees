import boto3
import json
from base_model import response
from common import API_ID, response

client = boto3.client('apigateway')

# GET /swagger
def get_swagger(event, context):
    export = client.get_export(restApiId=API_ID,
                               stageName='dev',
                               exportType='oas30',
                               accepts='application/json')
    body = export['body'].read().decode('utf8')
    swagger = patch_base_path(json.loads(body))
    return response(200, swagger)

# This fixes what seems to be a bug in AWS client.get_export.
# The value of basePath is '/dev', but it should be 'dev'.
# The extra slash breaks petstore.swagger.io, so we remove it here.

def patch_base_path(swagger):
    server = swagger['servers'][0]
    path = server['variables']['basePath']['default']
    new = path.strip('/')
    server['variables']['basePath']['default'] = new
    return swagger
