# How to set up the back end


The back end runs on Amazon AWS.

Warning: When working in the AWS console, always be sure that you've selected a region consistently.
For example, we picked `us-east-1` (N. Virginia).

## DynamoDB

The database is DynamoDB. There's no reason to be using NoSQL, in fact,
it might have been a bit easier to use Amazon RDS (Aurora Postgres Serverless)
since there are relations between the objects (like orders and users).

The reason to choose DynamoDB is that the free tier (up to 25GB of data)
is free forever, while RDS is only free for the first 12 months.

### Setup

Go to the DynamoDB console and create these tables:

 * `users` (partition key: `user_id`)
 * `teams` (partition key: `team_id`)
 * `orders` (partition key: `order_id`)
 * `offers` (partition key: `offer_id`)
 * `admins` (partition key: `name`)

For `users`, add a secondary index on `login_code`.

Dial down the read+write capacity to stay within the free tier (total of 25 capacity units).

 * Look at the 'capacity' tab for each table.
 * Look at the 'dashboard' tab for DynamoDb.
 * Default is 5. 1 or 2 is fine.

## Lambda

Lambdas are the functions that handle REST API requests.

### Setup

Go to IAM and create a policy granting DynamoDB permissions: GetItem, PutItem, DeleteItem
Ours has a name like `LambdaExecutedDynamoDBPolicy`.

Go to S3 and find the zip file uploaded by `deploy_lambda.py`. Ours is in https://helperbees.s3.amazonaws.com/prd/artifacts/functions.zip.

Go to the Lambda console and create each of the lambdas. For each one:
 * Start with "Author from Scratch"
 * code entry type: Upload a file from Amazon S3
 * Amazon S3 link: your S3 zip path
 * runtime: Python 3.7
 * handler: users.user_get (the path to each function will be different)
 * Don't forget to hit `Save`

Update the Execution role:
 * By default a new execution role is created. For example, `user_get-role-ptk0njrt`
 * Add `LambdaExecutedDynamoDBPolicy` to the execution role for this lambda.



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
   * Enable "Use Lambda Proxy integration"
   * Under Method Response:
     * under response for `http status=200`
     * under `Response Body for 200`
     * add a response model of type `application/json`

   *For methods that take JSON in the body (i.e. POST, PUT)
   * under Method Request, edit Request Body
   * specify MIME type: application/json
   * specify model
