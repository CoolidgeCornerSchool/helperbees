import os
import sys
import logging
from urllib.parse import parse_qsl
from base_model import BaseModel
from common import response, safe_json, with_admin
from offers import OFFERS

DIR = os.path.dirname('__file__')
sys.path.append(os.path.join(DIR, 'lib'))
import requests

class Order(BaseModel):
    tablename = 'orders'
    partition_key = 'order_id'

# Singleton
ORDERS = Order.get_singleton()

# for confirmation API requests
PAYPAL_SANDBOX_URL = 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_LIVE_URL = 'https://ipnpb.paypal.com/cgi-bin/webscr'

def get_paypal_confirmation(data, url=PAYPAL_LIVE_URL):
    """
    Sends data back to paypal to validate that it's legitimately from paypal.
    See https://developer.paypal.com/docs/classic/ipn/integration-guide/IPNImplementation/
    :return: string either "VERIFIED" or "INVALID"
    """
    user_agent = 'HelperBees paypal agent'
    data['cmd'] = '_notify-validate'
    headers = {'User-Agent': user_agent}
    response = requests.post(url, data=data, headers=headers)
    return response.text

# POST /order
def order_create(event, context):
    """
    Event is a POST from Paypal's IPN (instant payment notification) callback
    containing all the details of a completed Paypal offer.
    """
    item = {i[0]:i[1] for i in parse_qsl(event['body'])}
    confirmation = get_paypal_confirmation(item)
    item['confirmation'] = confirmation
    if 'custom' in item:
        # 'custom' field contains offer_id. If present, insert it as a nested object
        offer_id = item['custom']
        offer = OFFERS.get_by_id(offer_id)
        if offer:
            item['offer'] = offer
    new_key = ORDERS.create(item)
    return response(200, {'order_id': new_key})

# GET /order/{order_id}
def order_get(event, context):
    item_id = event['pathParameters']['order_id']
    item = ORDERS.get_by_id(item_id)
    if item:
        return response(200, item)
    return response(404, 'Item not found')

# GET /order
@with_admin
def order_get_all(event, context, admin=None):
    items = ORDERS.get_all()
    return response(200, {'result': items})

# DELETE /order/{order_id}
@with_admin
def order_delete(event, context, admin=None):
    if not admin:
        return response(401, 'Unauthorized')
    item_id = event['pathParameters']['order_id']
    success = ORDERS.delete(item_id)
    return response(200, {'success': success})

