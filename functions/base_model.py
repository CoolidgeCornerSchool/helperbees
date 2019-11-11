import boto3
import json
import string
import secrets
import logging
from common import log_setup, response, to_json, to_dynamo, to_dynamo_update
from botocore.exceptions import ClientError

LOG = log_setup()

class BaseModel:
    singleton = None
    id_size = 8   # length of generated ID token

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
    def create(self, item):
        """
        :param item: dict with values for item to be created with a new unique id
        :return: new_key
        """
        logging.info(f'CREATE item={item}')
        item, err = self.validate_for_create(item)
        if err:
            return item
        i = 0
        while True:
            # Retry if our random key collides
            i += 1
            if i>1:
                logging.warning(f' *** repeating CREATE_WITH_ITEM N={i}: create {self.__class__} item={item}')
            if i>5:
                logging.error(f'Giving up after {i} tries. item = {item}')
                return "fail"
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
    def update(self, item_id, item):
        """
        Updates the entry by replacing it
        :param item_id:
        :param item: partial spec of values to be updated
        :return: True if succeeds
        """

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
        return True

    def update_hook(self, item):
        return item

    # GET /<thing>/{item_id}
    def get_by_id(self, item_id):
        """
        :param item_id:
        :return: dict - item if found, or None
        """
        try:
            resp = self.dynamo.get_item(TableName=self.tablename,
                                            Key={self.partition_key: {'S': item_id}})
        except ClientError as err:
            error_code = err.response['Error']['Code']
            logging.exception(f'ERROR {error_code}: {err}')
            raise
        item = resp.get('Item', None)
        if item:
            return to_json(item)

    # GET /<thing>
    def get_all(self):
        """
        :return: a list of all items. At scale, this should be paginated.
        """
        data = self.dynamo.scan(TableName=self.tablename)
        items = [to_json(item) for item in data['Items']]
        return items

    # DELETE /<thing>/{item_id}
    def delete(self, item_id):
        """
        Deletes an item
        :param item_id: item to delete
        """
        result = self.dynamo.delete_item(TableName=self.tablename,
                                    Key={self.partition_key: {'S': item_id}})
        return True

    def mask_fields(self, item):
        if hasattr(self, 'masked_fields'):
            return {k:v for k,v in item.items() if k not in self.masked_fields}
        else:
            return item

