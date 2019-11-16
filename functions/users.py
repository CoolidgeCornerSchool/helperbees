import secrets
import logging
from base_model import BaseModel
from common import response, with_admin, with_user, safe_json, to_dynamo, to_json

class User(BaseModel):
    tablename = 'users'
    partition_key = 'user_id'
    #masked_fields = ['login_code']

    def validate_for_create(self, item):
        """
        :return: tuple of (response, is_err)
        If response is an error, return it with is_err=True.
        If no error, response is the user_item, which can be
           a) if user already exists, user_item = {'user_id': <user_id>}
           b) if user doesn't exist, returns dict of user fields to create a new user
        """
        user_id = item.get('user_id', None)
        if user_id:
            # Supplied user_id -> look up values and return existing user
            result = self.get_by_id(user_id)
            if result:
                return result, False
            else:
                return response(404, f"User not found: {user_id}"), True
        # call base method
        item, is_err = super().validate_for_create(item)
        if is_err:
            return item
        first_name = item.get('first_name', None)
        last_name = item.get('last_name', None)
        user_id, is_err = self.lookup_by_name(first_name, last_name)
        if is_err:
            return user_id, True  # error while trying to look up user by name
        if user_id:
            return {'user_id' : user_id}, False # found existing user
        # will need to create a new user
        result = {'create_new_user': True}
        required_user_fields = ['first_name', 'last_name', 
                                'parent_name','parent_phone', 'parent_email']                                
        for field in required_user_fields:
            if field not in item:
                return response(400, f'Missing required field: "{field}"'), True
            else:
                result[field] = item[field]
        return result, False

    def lookup_by_name(self, first_name, last_name):
        """
        :return: a tuple of (user_id, is_err)
        If user is found, returns (user_id, False)
        If user is not found, this is not an error [returns (None, False)]
        """
        if not (first_name and last_name):
            return response(400, f'Missing name: "{first_name}" "{last_name}"'), True
        try:
            result = self.dynamo.query(
                ExpressionAttributeValues={ ':fn': { 'S': first_name },
                                            ':ln': { 'S': last_name }},
                KeyConditionExpression='first_name = :fn AND last_name = :ln',
                TableName=self.tablename,
                IndexName='full_name-index'
                )
            items = result['Items']
            if len(items) == 0:
                return (None, False)
            elif len(items) > 1:
                return response(500, f'More than one person named "{first_name}" "{last_name}"'), True
            else:
                item = to_json(items[0])
                return item['user_id'], False
        except Exception:
            raise

    def lookup_by_login(self, login_code):
        """
        :return: user record, or None
        """
        try:
            result = self.dynamo.query(
                ExpressionAttributeValues={ ':l': { 'S': login_code }},
                KeyConditionExpression='login_code = :l',
                TableName=self.tablename,
                IndexName='login_code-index'
                )
            items = result['Items']
            if len(items) == 0:
                return None
            elif len(items) > 1:
                logging.error(f'More than one record found for login_code={login_code}')
                return None
            else:
                return to_json(items[0])
        except Exception:
            raise

    def update_hook(self, item):
        """
        Prevent updates for login_code.
        """
        return {k:v for (k,v) in item.items() if k != 'login_code'}


    def create_attempt_put(self, item):
        """
        When creating a user, also create a login_code
        
        This is invoked by create (overrides default behavior).
        It tries to store a newly-created item.
        Hopefully the new randomly-generated ID is unique, but if it isn't,
        this will throw an error and will be retried with a different random ID.
        """
        if 'create_new_user' in item:
            del item['create_new_user']
        new_id = secrets.token_urlsafe(self.id_size)
        item['user_id'] = new_id
        item['login_code'] = secrets.token_urlsafe(self.id_size)

        # TODO: This doesn't actually prevent collisions on login_code, since we don't look for it.
        condition = f'attribute_not_exists(user_id) AND attribute_not_exists(login_code)'
        self.dynamo.put_item(TableName=self.tablename,
                             Item=to_dynamo(item),
                             ConditionExpression=condition)
        return new_id

# Singleton
USER = User.get_singleton()


# POST /user
def user_create(event, context):
    item, err = safe_json(event['body'])
    if err:
        return item
    new_key = USER.create(item)
    return response(200, {'user_id': new_key})

# PUT /user
@with_user
@with_admin
def user_update(event, context, user=None, admin=None):
    item_id = event['pathParameters']['user_id']
    item, err = safe_json(event['body'])
    if err:
        return item
    if USER.update(item_id, item):
        return response(200, {'result': 'Successfully updated'})

# GET /user/{user_id}
@with_user
@with_admin
def user_get(event, context, user=None, admin=None):
    item_id = event['pathParameters']['user_id']
    if not (admin or (user and user['user_id'] == item_id)):
        return response(401, 'Unauthorized')
    item = USER.get_by_id(item_id)
    if item:
        return response(200, item)
    return response(404, 'Item not found')

# GET /user
@with_admin
def user_get_all(event, context, admin=None):
    if not admin:
        return response(401, 'Unauthorized')
    items = USER.get_all()
    return response(200, {'result': items})

# DELETE /user/{user_id}
@with_admin
def user_delete(event, context, admin=None):
    if not admin:
        return response(401, 'Unauthorized')
    item_id = event['pathParameters']['user_id']
    success = USER.delete(item_id)
    return response(200, {'success': success})

# GET /login/{login_code}
def user_login(event, context):
    login_code = event['pathParameters'].get('login_code', None)
    if not login_code:
        return response(400, 'Missing login_code parameter')
    user = USER.lookup_by_login(login_code)
    if not user:
        return response(404, 'User not found')
    return response(200, user)

# Not yet implemented
# GET /remind/{email}
def remind_code(event, context):
    user = USER.lookup_by_email(email)
