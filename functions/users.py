import boto3
from botocore.exceptions import ClientError
import json
import logging
from common import log_setup, flatten_dynamo_item, to_dynamo_item, new_id

log_setup()

DYNAMO = boto3.client('dynamodb')


# POST /user
def post(event, context):
    """
    Create a new entry with a new unique id
    """
    body = json.loads(event['body'])
    if 'user_id' in body:
        return { "statusCode": 400, "body": 'Cannot supply user_id in request'}
    new_key = new_id(DYNAMO, 'users', 'user_id')
    body['user_id'] = new_key
    try:
        result = DYNAMO.put_item(TableName='users',
                                 Item=to_dynamo_item(body),
                                 ConditionExpression='attribute_not_exists(user_id)'
                                 )
    except ClientError as err:
        error_code = err.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            return { "statusCode": 500, "body": f'User "{new_key}" already exists'}
        raise
    return {
        "statusCode": 200,
        'body': json.dumps({'user_id': new_key})
        }

# PUT /user
def update(event, context):
    """
    Updates the entry by replacing it
    """
    user_id = event['pathParameters']['user_id']
    body = json.loads(event['body'])
    key = body.get('user_id', None)
    if key not in body:
        body['user_id'] = key
    if key and key != user_id:
        return { "statusCode": 400, "body": 'Mismatched user_id: "{user_id}" != "{key}"'}
    try:
        result = DYNAMO.put_item(TableName='users',
                                 Item=to_dynamo_item(body),
                                 ConditionExpression='attribute_exists(user_id)')
    except ClientError as err:
        error_code = err.response['Error']['Code']
        if error_code == 'ConditionalCheckFailedException':
            return { "statusCode": 404, "body": f'Cannot update user "{user_id}", no such user.'}
        raise

    return {
        "statusCode": 200,
        'body': json.dumps({'user_id': key})
        }

# GET /user/{user_id}
def get_one(event, context):
    user_id = event['pathParameters']['user_id']
    data = DYNAMO.get_item(TableName='users', Key={'user_id': {'S': user_id}})
    item = data.get('Item', None)
    if item:
        result = flatten_dynamo_item(item)
        return {
            "statusCode": 200,
            'body': json.dumps(result)
            }
    return { "statusCode": 404, 'body': 'User not found'}
    

# GET /user
def get_all(event, context):
    data = DYNAMO.scan(TableName='users')
    items = [flatten_dynamo_item(i) for i in data['Items']]
    return {
        "statusCode": 200,
        'body': json.dumps(items)
        }

# DELETE /user/{user_id}
def delete(event, context):
    """
    Deletes a user
    """
    user_id = event['pathParameters']['user_id']
    result = DYNAMO.delete_item(TableName='users', Key={'user_id': {'S': user_id}})
    return {
        "statusCode": 200,
        'body': json.dumps({'user_id': user_id})
        }
