import boto3
from botocore.exceptions import ClientError
import json
import logging
import secrets
from common import log_setup

log_setup()

DYNAMO = boto3.client('dynamodb')

ID_SIZE = 6                        # length of ID token

CORS_HEADERS = { 'Content-Type': 'application/json',
                 'Access-Control-Allow-Origin': '*' }


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


class BaseModel:
    singleton = None

    @classmethod
    def get_singleton(cls):
        """
        :return: an instance of the model class
        This is a singleton - will re-use the existing instance if one exists.
        """
        if not cls.singleton:
            cls.singleton = cls()
        return cls.singleton

    # POST /user
    def create(self, event, context):
        """
        Create a new entry with a new unique id
        """
        body, err = safe_json(event['body'])
        if err:
            return body
        if self.partition_key in body:
            return response(400, 'Cannot supply item_id in request')
        new_key = self.new_id()
        body[self.partition_key] = new_key
        try:
            result = DYNAMO.put_item(TableName=self.tablename,
                                     Item=to_dynamo(body),
                                     ConditionExpression=f'attribute_not_exists({self.partition_key})'
                                     )
        except ClientError as err:
            error_code = err.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                return response(500, f'Item "{new_key}" already exists')
            raise
        return response(200, {self.partition_key: new_key})
    

    # PUT /user
    def update(self, event, context):
        """
        Updates the entry by replacing it
        """
        item_id = event['pathParameters'][self.partition_key]
        body, err = safe_json(event['body'])
        if err:
            return body
        if self.partition_key not in body:
            body[self.partition_key] = item_id
        id_from_body = body.get(self.partition_key, None)
        if not id_from_body or id_from_body != item_id:
            return response(400, f'Mismatched item_id: "{item_id}" != "{id_from_body}"')
        try:
            result = DYNAMO.put_item(TableName=self.tablename,
                                     Item=to_dynamo(body),
                                     ConditionExpression=f'attribute_exists({self.partition_key})')
        except ClientError as err:
            error_code = err.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                return response(404, f'Cannot update item {self.partition_key}="{item_id}", no such item with body={to_dynamo(body)}.')
            raise
        return response(200, {self.partition_key: item_id})


    # GET /user/{item_id}
    def get(self, event, context):
        item_id = event['pathParameters'][self.partition_key]
        data = DYNAMO.get_item(TableName=self.tablename, Key={self.partition_key: {'S': item_id}})
        item = data.get('Item', None)
        if item:
            result = to_json(item)
            return response(200, result)
        return response(404, 'Item not found')

    # GET /user
    def get_all(self, event, context):
        """
        :return: a list of all items. At scale, this should be paginated.
        """
        data = DYNAMO.scan(TableName=self.tablename)
        items = [to_json(i) for i in data['Items']]
        return response(200, {'result': items})

    # DELETE /user/{item_id}
    def delete(self, event, context):
        """
        Deletes an item
        """
        item_id = event['pathParameters'][self.partition_key]
        result = DYNAMO.delete_item(TableName=self.tablename,
                                    Key={self.partition_key: {'S': item_id}})
        return response(200, {'success': True})


    def new_id(self):
        """
        :return: an unused id for newly created objects
        Note: this is good enough for us, but for large projects just use UUID and
        don't check the database.
        """
        while True:
            new = secrets.token_urlsafe(ID_SIZE)
            found = DYNAMO.get_item(TableName=self.tablename,
                                    Key={self.partition_key: {'S': new}},
                                    ProjectionExpression=self.partition_key)
            if 'Item' not in found:
                return new
