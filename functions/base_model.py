import boto3
import json
import string
import secrets
import logging
from common import log_setup, response, safe_json
from botocore.exceptions import ClientError

LOG = log_setup()

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


    def validate_for_create(self, item):
        """
        If item is valid, return it with is_error=False
        If there's an error, return the error response (as dict) along with is_error=True
        :param item: item to be validated
        :return: tuple of (object, is_error)
        """
        if self.partition_key in item:
            return response(400, 'Cannot supply item_id in request'), True
        return item, False


    # POST /<thing>
    def create(self, event, context):
        """
        Create a new entry with a new unique id
        :param event: AWS Lambda incoming event
        :param context: AWS Lambda incoming context
        :return item_id:
        """
        item, err = safe_json(event['body'])
        if err:
            return item
        new_key = self.create_with_item(item)
        return response(200, {self.partition_key: new_key})

    def create_with_item(self, item):
        """
        :param item: dict with values for item to be created with a new unique id
        :return: new_key
        """

        item, err = self.validate_for_create(item)
        if err:
            return item
        i = 0
        while True:
            # Retry if our random key collides
            i += 1
            if i>1:
                logging.warning(f' *** repeating CREATE_WITH_ITEM N={i}: create {self.__class__}')
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
        return new_key

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

    # PUT /<thing>
    def update(self, event, context):
        """
        Updates the entry by replacing it
        :param event: AWS Lambda incoming event
        :param context: AWS Lambda incoming context        
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

    # GET /<thing>/{item_id}
    def get(self, event, context):
        """
        :param event: AWS Lambda incoming event
        :param context: AWS Lambda incoming context
        """
        item_id = event['pathParameters'][self.partition_key]
        item = self.get_by_id(item_id)
        if item:
            result = self.mask_fields(item)
            return response(200, result)
        return response(404, 'Item not found')

    def get_by_id(self, item_id):
        """
        :param item_id:
        :return: dict - item if found, or None
        """
        try:
            response = self.dynamo.get_item(TableName=self.tablename,
                                            Key={self.partition_key: {'S': item_id}})
        except ClientError as err:
            error_code = err.response['Error']['Code']
            logging.exception(f'ERROR {error_code}: {err}')
            raise
        item = response.get('Item', None)
        if item:
            return to_json(item)

    # GET /<thing>
    def get_all(self, event, context):
        """
        :param event: AWS Lambda incoming event
        :param context: AWS Lambda incoming context
        :return: a list of all items. At scale, this should be paginated.
        """
        data = self.dynamo.scan(TableName=self.tablename)
        items = [self.mask_fields(to_json(i)) for i in data['Items']]
        return response(200, {'result': items})

    # DELETE /<thing>/{item_id}
    def delete(self, event, context):
        """
        Deletes an item
        :param event: AWS Lambda incoming event
        :param context: AWS Lambda incoming context
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
            
