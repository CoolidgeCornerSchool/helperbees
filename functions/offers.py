import json
import secrets
from base_model import BaseModel
from common import response, safe_json
from users import USER
import logging

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
        fields = ['offer_type', 'offer_description', 'offer_units', 'offer_per_hour']
        for field in fields:
            value = item.get(field, None)
            if value:
                result[field] = value
            else:
                msg = f'Missing some required fields in offer: missing "{field}"'
                logging.warn(msg)
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
        logging.info(f'POOF = {user_item}')

        if is_err:
            # if error, return it
            return user_item
        # user_item is either a reference to an existing user or a spec for a new user
        logging.info(f'create user_item = {user_item}')
        if user_item.get('create_new_user', False):
            del user_item['create_new_user']
            user_id = USER.create_with_item(user_item)
        else:
            user_id = user_item.get('user_id', None)
            if not user_id:
                return response(400, "Missing user_id")

        offer_item['user_id'] = user_id

        new_event = {'body': json.dumps(offer_item)}
        resp = self.create(new_event, context)

        if resp['statusCode'] != 200:
            raise Exception(f"{resp['statusCode']}: {resp['body']}")
        offer_id = json.loads(resp['body'])['offer_id']
        return response(200, {'user_id': user_id, 'offer_id': offer_id})

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
