import logging
import secrets

LOG_LEVEL = logging.DEBUG

CORS_HEADERS = {
    'Content-Type': 'application/json', 
    'Access-Control-Allow-Origin': '*' 
    }

def log_setup():
    """
    Sets the log level.
    No easy way other than to override AWS Lambda default handlers.
    """
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='YYYYY %(asctime)s %(message)s', level=LOG_LEVEL)


def flatten_dynamo_item(item):
    """
    :param item: verbose item (in dynamodb structure)
    :return: simple dict
    """
    return { k:list(v.values())[0] for k,v in item.items()}

def to_dynamo_item(item):
    """
    Dynamodb requires dict markup declaring the type of every entity
    This marks up the results object.
    """
    return { k:{"S":str(v)} for k,v in item.items()}
           


def new_id(client, table_name, key_name):
    """
    :return: a new unused id for table_name.key_name in client
    """
    while True:
        new = secrets.token_urlsafe(6)
        found = client.get_item(TableName=table_name,
                                Key={key_name: {'S': new}},
                                ProjectionExpression=key_name)
        if 'Item' not in found:
            return new

