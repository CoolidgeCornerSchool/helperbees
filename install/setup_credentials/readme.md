# How to set up credentials

## Overview

We need to grant this app (the python code in functions/sendmail.py)
permission to send email using the gmail account. 

```
 GMAIL_ACCOUNT = "ccs.helperbees@gmail.com"
```

This assumes you're a developer and can get code from the developer console in the browser.

Read [Google Sign-in for Server Side](https://developers.google.com/identity/sign-in/web/server-side-flow)

* Install google auth libraries (which go into src/helperbees/lib/*)  
  ```bash
  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib -t ${HELPERBEES}/lib
  ```

### Download secrets as a JSON file
 * Go to the Google API [credentials page](https://console.developers.google.com/apis/credentials) in the console.
 * Make sure you're logged in as the project owner (GMAIL_ACCOUNT).
 * Set up a new project if needed
 * Set up new Oauth2 credentials ("Oauth Client ID"), application type = "web application"
 * Set the Authorized origin to `http://localhost:4000`
 * Set the Authorized redirect URLs to `http://localhost:4000`
 * Save it
 * Download JSON (you'll get a downloaded file called something like `secrets.json`)
 * Edit the path to this file in `setup_auth.py` as `CLIENTSECRETS_LOCATION`

### Get the Authorization Code from Google
 The Authorization code is used only once, when you set up this app. It's used to create the *refresh token* (below).
 * Enter the client ID into signon.html in this folder
 * Run jekyll locally and open signon.html.
 * Click the "Sign in with Google" button.
 * Authenticate as the Gmail user you'll be sending email from (GMAIL_ACCOUNT)
 * When you approve, Google will provide an Authorization Code, which javascript will print in the console.
 * Cut and paste this code into `setup_auth.py`

### Use the Authorization Code to get a *refresh token*, and save it in a file.

  The *refresh token* is uploaded along with the rest of the python code in `functions.zip` to AWS Lambda,
  when you run `deploy_lambda.py`.
  The *refresh token* is used by `sendmail.py` to authenticate before sending mail. It's called a refresh token because it
  periodically expires, and is used to automatically create a new token.
  
  * Run Python, load `setup_auth.py`
  ```
  >>> import json
  >>> import setup_auth
  >>> auth_code = "s0011002233444455555..."
  >>> credentials = setup_auth.exchange_code(auth_code)
  >>> credentials
  <oauth2client.client.OAuth2Credentials object at 0x107eac400>
  >>> credentials_json = json.loads(credentials.to_json())
  >>> json.dump(credentials_json, open('refresh.json', 'w'))
  ```
  * This file contains your *refresh token*. Save this file into `functions/keys/refresh.json`.
  
### How to restore saved credentials from a saved json file
 ```
   >>> from oauth2client.client import OAuth2Credentials
   >>> credentials_json = json.load(open('refresh.json'))
   >>> clean_json = {k:v for (k,v) in credentials_json.items() if k not in ['_class', '_module', 'invalid']}
   >>> credentials = OAuth2Credentials(**clean_json)
   >>> credentials
   <oauth2client.client.OAuth2Credentials object at 0x103a71438>
 ```

### Auth Gmail API - example of sending email with these credentials
```
  >>> from googleapiclient.discovery import build
  >>> from email.mime.text import MIMEText
  >>> service = build('gmail', 'v1', credentials=credentials)
  >>> message = MIMEText("hello there")
  >>> message['to'] = 'someperson@example.com'
  >>> message['subject'] = 'about this test'
  >>> msg = {"raw" : base64.urlsafe_b64encode(message.as_string().encode('utf8')).decode('utf8')}
  >>> service.users().messages().send(userId='me', body=msg).execute()

