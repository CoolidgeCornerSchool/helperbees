"""
This exports a JSON document describing all of the REST endpoints
published by AWS API Gateway.
Basically, these are all of the create/read/write/delete endpoints.

This code defines a REST endpoint, GET /swagger
which serves up the output of the AWS API Gateway get_export() command.

You can view the raw JSON by visiting
  https://{API_BASE_URL}/swagger or
  https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/swagger

You can view these with a cute GUI by visiting
  http://helperbees.org/api
This redirects to petstore.swagger.io, which hosts the cute GUI.
"""

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
