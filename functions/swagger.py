import boto3
from base_model import response
from common import API_ID, response

client = boto3.client('apigateway')

# GET /swagger
def get_swagger(event, context):
    export = client.get_export(restApiId=API_ID,
                               stageName='dev',
                               exportType='oas30',
                               accepts='application/json')
    print(export.keys())
    body = export['body'].read().decode('utf8')
    return response(200, body)
