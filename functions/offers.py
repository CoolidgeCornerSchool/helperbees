import json
import secrets
from base_model import BaseModel
from common import response, safe_json, with_user, with_admin
from sendmail import send, render_template
from users import USER

RECIPIENTS = {
    'STEVE': 'steve@strassmann.com',
    'PHIL' : 'phildurbin@gmail.com',
    'DEVS' : 'steve@strassmann.com, phildurbin@gmail.com, futuresuzi@gmail.com',
    'NOBODY' : None}

CONFIRMATION_TO = 'STEVE'

class Offer(BaseModel):
    tablename = 'offers'
    partition_key = 'offer_id'

    def validate_offer(self, item):
        """
        :return: tuple of (response, is_err)
        If is_err is True, response is an error
        """
        # optional field: 'offer_type_other'
        result = { 'offer_type_other' : item.get('offer_type_other', "<empty>") }
        fields = ['offer_type', 'offer_description', 'offer_unit', 'offer_per_hour']
        for field in fields:
            value = item.get(field, None)
            if value:
                result[field] = value
            else:
                msg = f'Missing some required fields in offer: missing "{field}"'
                return response(400, msg), True
        return result, False


    # POST /offer_and_user
    def create_with_user(self, item):
        """
        Like POST /offer, but also has user info in the event body
        :param item: form data with key/values for the offer and for the user
        :return: Returns tuple of (item, is_err):
           if result is an error, returns (err_response, True)
           if result is normal, returns   (result, False)
        """

        offer_item, err = self.validate_offer(item)
        if err:
            return offer_item, True

        user_item, is_err = USER.validate_for_create(item)
        if is_err:
            # if error, return it
            return user_item, True

        # user_item is either a reference to an existing user or a spec for a new user
        # only return a login_code if a new user has been created
        if user_item.get('create_new_user', False):
            del user_item['create_new_user']
            user_id = USER.create(user_item)
            user = USER.get_by_id(user_id)
            login_code = user['login_code']
            user_item['login_code'] = login_code
        else:
            user_id = user_item.get('user_id', None)
            login_code = None
            if not user_id:
                return response(400, "Missing user_id"), True

        offer_item['user_id'] = user_id
        offer_id = self.create(offer_item)
        result = {'user_id': user_id, 'offer_id': offer_id}
        # only return a login_code if a new user has been created
        if login_code:
            result['login_code'] = login_code
        self.send_confirmation_email(offer_item, user_item)
        return response(200, result), False

    def send_confirmation_email(self, offer_item, user_item):
        recipient = RECIPIENTS.get(CONFIRMATION_TO, None)
        if not recipient:
            logging.warn(f'Not sending mail to anyone : CONFIRMATION_TO={CONFIRMATION_TO}')
            return
        new_user = 'login_code' in user_item
        values = offer_item.copy()
        if 'first_name' not in user_item:
            user_item = USER.get_by_id(user_item['user_id'])
        values.update(user_item)
        if new_user:
            template = 'confirm_offer_newuser.txt'
        else:
            template = 'confirm_offer_user.txt'
        body = render_template(template, values)
        return send(recipient, 'Welcome to HelperBees', body)

# Singleton
OFFERS = Offer.get_singleton()

# POST /offer_and_user
def offer_create_with_user(event, context):
    item, err = safe_json(event['body'])
    if err:
        return item
    result = OFFERS.create_with_user(item)
    return response(200, result)

# PUT /offer
@with_user
@with_admin
def offer_update(event, context, user=None, admin=None):
    item_id = event['pathParameters']['offer_id']
    item = OFFERS.get_by_id(item_id)
    if not (admin or (user and user['user_id'] == item['user_id'])):
        # authorized if you're an admin, or if you're the owner of the offer
        return response(401, 'Unauthorized')
    if not item:
        return response(404, 'Item not found')
    put_data, err = safe_json(event['body'])
    if err:
        return put_data
    if OFFERS.update(item_id, put_data):
        return response(200, 'Successfully updated')

# GET /offer/{offer_id}
def offer_get(event, context):
    item_id = event['pathParameters']['offer_id']
    item = OFFERS.get_by_id(item_id)
    if item:
        return response(200, item)
    return response(404, 'Item not found')

# GET /offer
def offer_get_all(event, context):
    items = OFFERS.get_all()
    return response(200, {'result': items})

# DELETE /offer/{offer_id}
@with_user
@with_admin
def offer_delete(event, context, admin=None, user=None):
    item_id = event['pathParameters']['offer_id']
    item = OFFERS.get_by_id(item_id)
    if not item:
        return response(404, 'Item not found')
    if not (admin or (user and user['user_id'] == item['user_id'])):
        # authorized if you're an admin, or if you're the owner of the offer
        return response(401, 'Unauthorized')
    success = OFFERS.delete(item_id)
    return response(200, {'success': success})
