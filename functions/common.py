import os
import boto3
import json
import logging
from google_oauth import validate
from functools import wraps

LOG_LEVEL = logging.INFO

DISABLE_EMAIL = False # If true, don't send any emails

DIR = os.path.dirname('__file__')
ADMINS = json.load(open(os.path.join(DIR, 'keys', 'admins.json')))
DYNAMO = boto3.client('dynamodb')

# AWS API Gateway id
API_ID = 'pxa9qyui26'
LOGIN_CLIENT_ID = '635073293377-g9q675lgb6ek99l0fd92lhjvkk62kptl.apps.googleusercontent.com'

CORS_HEADERS = { 'Content-Type': 'application/json',
                 'Access-Control-Allow-Origin': '*',
                 'Access-Control-Allow-Credentials' : True,
                 'Access-Control-Allow-Headers':'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,UserLogin',            
                 }

def response(code, data):
    """
    :param code: http response code
    :param data: string or dict to be returned to browser
    :return: dict - lambda/API request response
    """
    if isinstance(data, str):
        body = data
    elif isinstance(data, dict):
        body = json.dumps(data)
    else:
        raise ValueError(f'Unsupported data type ({data.__class__}) for {data}')
    return { "statusCode": code,
             'headers': CORS_HEADERS,
             "body": body}
    
def with_admin(func):
    """
    Decorator: passes admin's email to func if authenticated, or passes None if not.
    Uses JWT token passed in the request's Authorization header.
    JWT token is decoded as a Google oauth identity.
    email must be whitelisted in /keys/admins.yml
    """
    @wraps(func)
    def wrapper(event, context, **kwargs):
        admin = None
        headers = event.get('headers')
        if headers:
            auth = headers.get('Authorization', None)
        else:
            auth = None
        if auth:
            tokens = auth.split()
            if len(tokens)==2 and tokens[0]=="Bearer":
                try:
                    admin_email = validate(tokens[1], LOGIN_CLIENT_ID)
                    if admin_email in ADMINS:
                        admin = admin_email
                except Exception as err:
                    # validation failed
                    logging.error(err)
        return func(event, context, admin=admin, **kwargs)
    return wrapper
            
def with_user(func):
    """
    Decorator: passes user info to func if authenticated, or passes None if not.
    Uses login_code passed in the request's UserLogin header.
    """
    @wraps(func)
    def wrapper(event, context, **kwargs):
        user = None
        headers = event.get('headers')
        if headers:
            login_code = headers.get('userlogin', None)
            if not login_code:
                # Try different case - not sure why both are being passed in
                login_code = headers.get('Userlogin', None)
        else:
            login_code = None
        if login_code:
            user = get_user_by_login_code(login_code)
        return func(event, context, user=user, **kwargs)
    return wrapper

def get_user_by_login_code(login_code):
    result = DYNAMO.query(
        ExpressionAttributeValues={ ':l': { 'S': login_code }},
        KeyConditionExpression='login_code = :l',
        TableName='users',
        IndexName='login_code-index'
        )
    items = result['Items']
    if len(items) == 0:
        return None
    return to_json(items[0])
    
"""
def get_auth(event):
    headers = event.get('headers')
    admin_login = headers.get('Authorization', None)
    login_code = headers.get('userlogin', None)
    if not login_code:
        login_code = headers.get('Userlogin', None)
    admin = None
    if admin_login:
        tokens = admin_login.split()
        if len(tokens)==2 and tokens[0]=="Bearer":
            try:
                admin = validate(tokens[1], LOGIN_CLIENT_ID)[1]
            except Exception as err:
                # validation failed
"""


def to_json(item):
    """
    :param item: verbose item (in dynamodb structure)
    :return: simple dict
    """
    return { k:list(v.values())[0] for k,v in item.items()}

def to_dynamo(item):
    """
    Dynamodb requires dict markup declaring the type of every entity
    This marks up the results object.
    """
    return { k:{"S":str(v)} for k,v in item.items()}



def to_dynamo_update(item):
    """
    :param item: dict of key/value pairs of attributes to update in DynamoDb
    :return: dict of two expressions used by dynamo.update_item()
    Usage:
     >>> to_dynamo_update({'size' : 'large'})
     ->
     {'UpdateExpression': 'set size = :a',
      'ExpressionAttributeValues': {':a': {'S': 'large'}}}
     
    """
    assert isinstance(item, dict)
    assert len(item)<26, f"Item too big, must be <26 keys"
    vars = {}
    values = {}
    for (i, k) in enumerate(item):
        var = ':{}'.format(string.ascii_lowercase[i])
        values[var] = {'S' : item[k]}
        vars[k] = var
    expr = 'set ' + ', '.join(f'{k} = {v}' for (k,v) in vars.items())
    return {'UpdateExpression' : expr,
            'ExpressionAttributeValues' : values}
            


def safe_json(json_string):
    """
    If JSON string is parsed into a dict, return it with is_error=False
    If there's a parse error, return the error response (as dict) along with is_error=True
    :param string: JSON string to be parsed
    :return: tuple of (object, is_error).
    """
    try:
        return json.loads(json_string), False
    except json.decoder.JSONDecodeError as err:
        return response(400, f"Error parsing JSON: {err}"), True


def log_setup():
    """
    Sets the log level.
    No easy way other than to override AWS Lambda default handlers.
    """
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=LOG_LEVEL)
    return root
