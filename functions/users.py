from base_model import BaseModel

class User(BaseModel):
    tablename = 'users'
    partition_key = 'user_id'

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
