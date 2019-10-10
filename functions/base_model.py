import boto3
import json
import string
import secrets
import logging
from common import log_setup
from botocore.exceptions import ClientError

LOG = log_setup()

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
    

class BaseModel:
    singleton = None
    id_size = 6                # length of generated ID token

    def __init__(self):
        self.dynamo = boto3.client('dynamodb')


    @classmethod
    def get_singleton(cls):
        """
        :return: an instance of the model class
        This is a singleton - will re-use the existing instance if one exists.
        """
        if not cls.singleton:
            cls.singleton = cls()
        return cls.singleton


    def create_attempt_put(self, item):
        """
        This is invoked by create.
        It tries to store a newly-created item.
        Hopefully the new randomly-generated ID is unique, but if it isn't,
        this will throw an error and will be retried with a different random ID.
        """
        new_id = secrets.token_urlsafe(self.id_size)
        item[self.partition_key] = new_id
        
        self.dynamo.put_item(TableName=self.tablename,
                             Item=to_dynamo(item),
                             ConditionExpression=f'attribute_not_exists({self.partition_key})')
        return new_id

    # POST /user
    def create(self, event, context):
        """
        Create a new entry with a new unique id
        """
        item, err = safe_json(event['body'])
        if err:
            return item
        if self.partition_key in item:
            return response(400, 'Cannot supply item_id in request')

        i = 0
        while True:
            # Retry if our random key collides
            i += 1
            if i>1:
                logging.warning(f' *** repeating N={i}: create {self.__class__}')
            try:
                new_key = self.create_attempt_put(item)
                break # success: exit loop
            except ClientError as err:
                logging.exception(f'Error: {err}')
                error_code = err.response['Error']['Code']
                if error_code == 'ConditionalCheckFailedException':
                    # Collision, try again
                    continue
            except:
                logging.exception('Error')
                raise
        return response(200, {self.partition_key: new_key})

    # PUT /user
    def update(self, event, context):
        """
        Updates the entry by replacing it
        """
        item_id = event['pathParameters'][self.partition_key]
        item, err = safe_json(event['body'])
        if err:
            return item
        # Don't attempt to update the partition key
        item = {k:v for (k,v) in item.items() if k != self.partition_key}
        item = self.update_hook(item)

        try:
            params = to_dynamo_update(item)
            result = self.dynamo.update_item(TableName=self.tablename,
                                             Key={self.partition_key: {'S' : item_id}},
                                             UpdateExpression=params['UpdateExpression'],
                                             ExpressionAttributeValues=params['ExpressionAttributeValues'])
        except Exception as err:
            logging.exception(f'Error: {err}')
            raise
        return response(200, {self.partition_key: item_id})

    def update_hook(self, item):
        return item

    # GET /user/{item_id}
    def get(self, event, context):
        item_id = event['pathParameters'][self.partition_key]
        try:
            data = self.dynamo.get_item(TableName=self.tablename,
                                        Key={self.partition_key: {'S': item_id}})
        except ClientError as err:
            error_code = err.response['Error']['Code']
            logging.exception(f'ERROR {error_code}: {err}')
            raise
        item = data.get('Item', None)
        if item:
            result = self.mask_fields(to_json(item))
            return response(200, result)
        return response(404, 'Item not found')

    # GET /user
    def get_all(self, event, context):
        """
        :return: a list of all items. At scale, this should be paginated.
        """
        data = self.dynamo.scan(TableName=self.tablename)
        items = [self.mask_fields(to_json(i)) for i in data['Items']]
        return response(200, {'result': items})

    # DELETE /user/{item_id}
    def delete(self, event, context):
        """
        Deletes an item
        """
        item_id = event['pathParameters'][self.partition_key]
        result = self.dynamo.delete_item(TableName=self.tablename,
                                    Key={self.partition_key: {'S': item_id}})
        return response(200, {'success': True})

    def mask_fields(self, item):
        if hasattr(self, 'masked_fields'):
            return {k:v for k,v in item.items() if k not in self.masked_fields}
        else:
            return item


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
            
