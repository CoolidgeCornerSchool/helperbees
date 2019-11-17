import os
import sys
import logging
from urllib.parse import parse_qsl
from base_model import BaseModel
from common import response, safe_json, with_admin, with_user
from sendmail import send, render_template
from offers import OFFERS
from users import USER

DIR = os.path.dirname('__file__')
sys.path.append(os.path.join(DIR, 'lib'))
import requests

# Send bug reports to devs
DEVS = 'steve@strassmann.com, phildurbin@gmail.com, futuresuzi@gmail.com'
# Send cc of normal confirmation messages to admins
ADMIN = 'steve@strassmann.com, phildurbin@gmail.com, futuresuzi@gmail.com'

class Order(BaseModel):
    tablename = 'orders'
    partition_key = 'order_id'

    def create(self, order_item):
        """
        :return: new_key
        """
        try:
            result = super().create(order_item)
            self.send_confirmation_email(order_item)
            return result
        except Exception as err:
            logging.exception('error')
            return 'error'

    def send_confirmation_email(self, order_item):
        logging.info(f'request helper: send_confirmation_email order={order_item}')
        keys = ['order_id', 'payer_email', 'first_name', 'last_name', 'offer', 'memo', 'payment_gross']
        values = {k: order_item.get(k, None) for k in keys}
        if not values['offer']:
            logging.error(f'Error in order: missing offer {order_item}')
            send('error in order', f'Error in order: missing offer {order_item}', DEVS)
            return
        offer = values['offer']
        values.update(offer)
        per_hour = int(offer['offer_per_hour'])
        if per_hour != 1:
            values['plural'] = 's'
        else:
            values['plural'] = ''
        payment_gross = float(values['payment_gross'])
        values['formatted_payment'] = f"${payment_gross:.2f}"
        if not (values['first_name'] and values['last_name']):
            logging.error(f'Error in order: missing customer name {order_item}')
            send('error in order', f'Error in order: missing customer name {order_item}', DEVS)
            return
        values['customer_name'] = values['first_name'] + ' ' + values['last_name']
        values['customer_email'] = values['payer_email']
        # Customer might have included an optional message
        if values['memo']:
            values['customer_message'] = f"\n{values['customer_name']} wrote: \"{values['memo']}\""
        else:
            values['customer_message'] = ''
        if not values['user_id']:
            logging.error(f'Error in order: missing user_id {order_item}')
            send('error in order', f'Error in order: missing user_id {order_item}', DEVS)
            return
        user_item = USER.get_by_id(values['user_id'])
        values['kid_name'] = user_item['first_name']
        for key in ['parent_name', 'parent_email', 'parent_phone']:
            values[key] = user_item[key]
        recipients = values['payer_email'] + ',' + values['parent_email']
        template = 'job_requested.txt'
        body = render_template(template, values)
        result = send('New Helperbees job requested', body, recipients, cc=ADMIN)
        logging.info(f'orders send_confirmation_email sent to={recipients}')
        return result

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
    if 'item_number' in item:
        # 'item_number' field contains offer_id. If present, insert it as a nested object
        offer_id = item['item_number']
        offer = OFFERS.get_by_id(offer_id)
        if offer:
            item['offer'] = offer
    new_key = ORDERS.create(item)
    return response(200, {'order_id': new_key})


# GET /order/{order_id}
# TODO: this probably should be restricted, require either user or admin credentials
def order_get(event, context):
    item_id = event['pathParameters']['order_id']
    item = ORDERS.get_by_id(item_id)
    if item:
        return response(200, item)
    return response(404, 'Item not found')

# GET /order
# TODO: filter by credentials (either user or admin). Only show relevant orders.
# If user is logged in, only show their orders
# If admin is logged in, show all orders
# Return nothing for anonymous requests
@with_user
@with_admin
def order_get_all(event, context, admin=None, user=None):
    if not admin and not user:
        return response(401, "Unauthorized")
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

