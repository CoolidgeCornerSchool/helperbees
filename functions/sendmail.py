import re
import sys
import json
import os.path
import base64
from common import DISABLE_EMAIL
from email.mime.text import MIMEText

DIR = os.path.dirname('__file__')
sys.path.append(os.path.join(DIR, 'lib'))

from oauth2client.client import OAuth2Credentials
from googleapiclient.discovery import build


TEMPLATES = os.path.join(DIR, 'email_templates')

# get_service() has permission to send email on behalf of one gmail user.
# See install/setup_credentials/readme.md for info on how to create this file.
CREDENTIALS_FILE = os.path.join(DIR, 'keys', 'refresh.json')

def get_service():
    """
    :return: GMAIL service - an instance of googleapiclient.discovery.Resource
    with permission to send email on behalf of the user certified in CREDENTIALS_FILE.
    """
    credentials_json = json.load(open(CREDENTIALS_FILE))
    clean_json = {k:v for (k,v) in credentials_json.items() if k not in ['_class', '_module', 'invalid']}
    credentials = OAuth2Credentials(**clean_json)
    return build('gmail', 'v1', credentials=credentials)

GMAIL = get_service()

def render_template(template, values):
    result = open(os.path.join(TEMPLATES, template)).read()
    for k,v in values.items():
        pattern = re.compile(f'{{{{\s*{k}\s*}}}}')
        result = pattern.sub(str(v), result)
    return result

def send(recipient, subject, body):
    """
    Immediately sends email from gmail account in CREDENTIALS_FILE.
    :param recipient: string, e.g. 'user@host.com' or 'user1@a.com, user2@b.com'
    :param subject: string
    :param body: body of message
    """
    if DISABLE_EMAIL:
        logging.warn(f'Email is disabled (DISABLE_EMAIL==True). No email sent to {recipient}.')
        return
    message = MIMEText(body)
    message['to'] = recipient
    message['subject'] = subject
    body = {"raw" : base64.urlsafe_b64encode(message.as_string().encode('utf8')).decode('utf8')}
    return GMAIL.users().messages().send(userId='me', body=body).execute()

