import json
import secrets
from base_model import BaseModel
from common import response, safe_json
from sendmail import send, render_template
from users import USER

RECIPIENTS = {
    'STEVE': 'steve@strassmann.com',
    'PHIL' : 'phildurbin@gmail.com',
    'STEVE_AND_PHIL' : 'steve@strassmann.com, phildurbin@gmail.com',
    'NOBODY' : None}

CONFIRMATION_TO = 'STEVE_AND_PHIL'

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
    def create_with_user(self, event, context):
        """
        Like POST /offer, but also has user info in the event body
        :param event: AWS Lambda incoming event
        :param context: AWS Lambda incoming context
        """
        item, err = safe_json(event['body'])
        if err:
            return item

        offer_item, err = self.validate_offer(item)
        if err:
            return offer_item

        user_item, is_err = USER.validate_for_create(item)
        if is_err:
            # if error, return it
            return user_item

        # user_item is either a reference to an existing user or a spec for a new user
        # only return a login_code if a new user has been created
        if user_item.get('create_new_user', False):
            del user_item['create_new_user']
            user_id = USER.create_with_item(user_item)
            user = USER.get_by_id(user_id)
            login_code = user['login_code']
            user_item['login_code'] = login_code
        else:
            user_id = user_item.get('user_id', None)
            login_code = None
            if not user_id:
                return response(400, "Missing user_id")

        offer_item['user_id'] = user_id
        offer_id = self.create_with_item(offer_item)
        result = {'user_id': user_id, 'offer_id': offer_id}
        # only return a login_code if a new user has been created
        if login_code:
            result['login_code'] = login_code
        self.send_confirmation_email(offer_item, user_item)
        return response(200, result)

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
    return OFFERS.create_with_user(event, context)

# PUT /offer
def offer_update(event, context):
    return OFFERS.update(event, context)

# GET /offer/{offer_id}
def offer_get(event, context):
    return OFFERS.get(event, context)

# GET /offer
def offer_get_all(event, context):
    return OFFERS.get_all(event, context)

# DELETE /offer/{offer_id}
def offer_delete(event, context):
    return OFFERS.delete(event, context)

