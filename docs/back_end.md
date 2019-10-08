# How to set up the back end


The back end runs on Amazon AWS.


## DynamoDB

The database is DynamoDB. There's no reason to be using NoSQL, in fact,
it might have been a bit easier to use Amazon RDS (Aurora Postgres Serverless)
since there are relations between the objects (like orders and users).

The reason to choose DynamoDB is that the free tier (up to 25GB of data)
is free forever, while RDS is only free for the first 12 months.

### Setup

Go to the DynamoDB console and create these tables:

 * 'users' (partition key: 'user_id')
 * 'teams' (partition key: 'team_id')
 * 'orders' (partition key: 'order_id')
 * 'order_types' (partition key: 'name')
 * 'offers' (partition key: 'offer_id')
 * 'admins' (partition key: 'name')

## Lambda

Lambdas are the functions that handle REST API requests.

### Setup

Go to the Lambda console and create each of the lambdas.

## API Gateway

We need an API gateway to accept external HTTP requests and
pass them off to Lambdas to be handled.

### Setup

Go to the API Gateway console and create an API (called BeesAPI).

In BeesAPI, create a response model

In BeesAPI, create each of the resources at top level:
  * /user
  * /admin
  * /team
  * /order
  * /offer

Under each resource, create a child resource for the db partition key using brackets for the name:

  * /user/{user_id}
  * /team/{team_id}
  * /order/{order_id}
  * /offer/{offer_id}

For each resource, select it and (in the `Actions` menu) choose `Enable CORS`.

For each resource, create methods `GET`, `PUT`, `POST` connected to the corresponding Lambdas
(`user_get`, `user_update`, etc.).
   * Enable Lambda Proxy integration
   * Under Method Response, under response for `http status=200`, under `Response Body for 200`
   add a response model of type `application/json`

