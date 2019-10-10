import secrets
from base_model import BaseModel, to_dynamo

class User(BaseModel):
    tablename = 'users'
    partition_key = 'user_id'
    masked_fields = ['login_code']

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
    return USER.create(event, context)

# PUT /user
def user_update(event, context):
    return USER.update(event, context)

# GET /user/{user_id}
def user_get(event, context):
    return USER.get(event, context)

# GET /user
def user_get_all(event, context):
    return USER.get_all(event, context)

# DELETE /user/{user_id}
def user_delete(event, context):
    return USER.delete(event, context)
