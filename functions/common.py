import json
import logging

LOG_LEVEL = logging.INFO
API_ID = 'pxa9qyui26'

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
