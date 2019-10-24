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
