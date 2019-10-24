from base_model import BaseModel

class Order(BaseModel):
    tablename = 'orders'
    partition_key = 'order_id'

# Singleton
ORDERS = Order.get_singleton()

# POST /order
def order_create(event, context):
    return ORDERS.create(event, context)

# PUT /order
def order_update(event, context):
    return ORDERS.update(event, context)

# GET /order/{order_id}
def order_get(event, context):
    return ORDERS.get(event, context)

# GET /order
def order_get_all(event, context):
    return ORDERS.get_all(event, context)

# DELETE /order/{order_id}
def order_delete(event, context):
    return ORDERS.delete(event, context)
