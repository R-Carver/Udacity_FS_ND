import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'coffee-shop-project.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'localhost:5000'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    if 'Authorization' not in request.headers:
        abort(401)

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split(' ')

    if len(header_parts) != 2:
        abort(401)
    elif header_parts[0].lower() != 'bearer':
        abort(401)
    
    return header_parts[1]

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)

    if permission not in payload['permissions']:
        abort(403)
    
    print('Persmissions worked')
    return True

def verify_decode_jwt(token):
    #GET THE PUBLI KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    #GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)
    
    #CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        abort(401)

    print("kid present")
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n' : key['n'],
                'e' : key['e']
            }
    
    #Finally verify
    if rsa_key:
        try:
            #use the key to validate the jwt
            payload = jwt.decode(
                token, 
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to pass token'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            if payload is None:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator