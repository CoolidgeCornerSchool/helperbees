import os
import sys

DIR = os.path.dirname('__file__')
sys.path.append(os.path.join(DIR, 'lib'))

from oauth2client import client, crypt

# Decode and validate JSON Web Tokens
# JSON Web Tokens are an open, industry standard RFC 7519 method
# for representing claims securely between two parties.
# For more info, and a decoder in an interactive web app,
# see http://jwt.io

def oauth_idinfo(token, client_id, apps_domain_name=False):
    '''Returns fully decoded user properties.
       Token is a JWT token issued by Google
       client_id is the Google app client id used to sign the token
       '''
    idinfo = client.verify_id_token(token, client_id)
    if idinfo['aud'] not in [client_id]:
        print("error: Unrecognized client: %s" % idinfo['aud'])
        raise crypt.AppIdentityError("Unrecognized client: %s" % idinfo['aud'])
    if 'email' not in idinfo or len(idinfo['email'])==0:
        print("email missing from token")
        raise crypt.AppIdentityError("email missing from token")
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        print("Wrong issuer: %s" % idinfo['iss'])
        raise crypt.AppIdentityError("Wrong issuer: %s" % idinfo['iss'])
    # if apps_domain_name is provided, validate it.
    if apps_domain_name and idinfo['hd'] != apps_domain_name:
        print("Wrong hosted domain: %s" % idinfo['hd'])
        raise crypt.AppIdentityError("Wrong hosted domain: %s" % idinfo['hd'])
    return idinfo


def validate(token, client_id, apps_domain_name=False):
    """
    Raises a relevant error if not validated.
    Otherwise returns the email of the validated user.
    :return: google_user_email
    """
    idinfo = oauth_idinfo(token, client_id, apps_domain_name=apps_domain_name)
    return idinfo['email']
