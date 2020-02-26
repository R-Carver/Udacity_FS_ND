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
    
    #print(header_parts[1])
    return header_parts[1]


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        #raise AuthError({
        #    'code': 'invalid_claims',
        #    'description': 'Permissions not included in JWT'
        #}, 400)
        abort(400)

    if permission not in payload['permissions']:
        #raise AuthError({
        #    'code': 'unauthorized',
        #    'description': 'Permission not found'
        #}, 403)
        abort(403)
    
    print('Persmissions worked')
    return True


def verify_decode_jwt(token):
    #GET THE PUBLI KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    #GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)
    print("check kid")
    print('kid' not in unverified_header)
    #CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        #raise AuthError({
        #    'code': 'invalid_header',
        #    'description': 'Authorization malformed'
        #}, 401)
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
    
    print("rsa key created")
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

            print('token verified')
            return payload
        
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired'
            }, 401)
            #abort(401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims'
            }, 401)
            #abort(401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to pass token'
            }, 400)
            #abort(400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            print("token from req auth " + token)
            payload = verify_decode_jwt(token)
            print("payload from req auth ")
            print(payload)
            if payload is None:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

#https://coffee-shop-project.eu.auth0.com/authorize?audience=localhost:5000&response_type=token&client_id=l06RhQgmk3vwAVSwuPypxjO3fIrSNdER&redirect_uri=https://localhost:5000/drinks

#manager token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1FTTJSVGM0UkRJNFJqazNRVUZHUmtZM056QkRRVUU0UmpJelJUTXlNelZCUWpNek5VWkRRUSJ9.eyJpc3MiOiJodHRwczovL2NvZmZlZS1zaG9wLXByb2plY3QuZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlNTY5NzZkZmEyOWUxMGQ1Mzk0N2ExOSIsImF1ZCI6ImxvY2FsaG9zdDo1MDAwIiwiaWF0IjoxNTgyNzQyMjAyLCJleHAiOjE1ODI4Mjg2MDIsImF6cCI6ImwwNlJoUWdtazN2d0FWU3d1UHlweGpPM2ZJclNOZEVSIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.VvzrtYDRFPtdUWvOGA6ITTnmesR7GS1xn5dqB7VKp781aKV-NQQ4f0gVMI4d9jAza2cBc1JyUrUb45LCoVS1H8o9kUSf18gMsn95NU6B0DD3rSxxGbBYwt4K9swlxqiaEnn6z4FKvOOq6hoC82daiXGmmLswzku5c3lDe4tyV-Hvndj1T_KRRVQsXpljbhk3udMPcdvgi98Rbs5LzWR6xISDUyey8Whhk2fVid1OBtA47xeSWfJMR5Pecy7pOyeXemGwFhfLDppgiazM7iJQG9kLhR36xDWzsMtt0pbBDEwaH8sEz_aNbvX-UHj4V13Y5L9JVJVhcTjD_lioG9wzdw
#barista token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1FTTJSVGM0UkRJNFJqazNRVUZHUmtZM056QkRRVUU0UmpJelJUTXlNelZCUWpNek5VWkRRUSJ9.eyJpc3MiOiJodHRwczovL2NvZmZlZS1zaG9wLXByb2plY3QuZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVlNTY5NzE2ZmEyOWUxMGQ1Mzk0NzkxOCIsImF1ZCI6ImxvY2FsaG9zdDo1MDAwIiwiaWF0IjoxNTgyNzQyNDcxLCJleHAiOjE1ODI4Mjg4NzEsImF6cCI6ImwwNlJoUWdtazN2d0FWU3d1UHlweGpPM2ZJclNOZEVSIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzLWRldGFpbCJdfQ.EickFLARbguNEfQjOcL10DsPANFeKz8_Un2YhMe3cwwCQFMylx2JcvvC0sNKH5YhddXACmHz0kIc6YFMUikjDSWdHTDX6KY5CpQ6pYH6CWtDRdA19fUfRfcKnABeNIjmpJEd1oLz7_BMhaE4VXMmshm9DjI8w-KhxAB3uS49IfxMkUY_5fU2wc8M09vHu6UdArS3lpisnEKFknwZgAllNXIJFVlSXXOUFMeKHNmVlv0r-HTvWyIKL14GLrY245Jnlt-oldCSeamRfa3T_5cO06jTv57yiE_eryvKbRJblT9o_J78GoGrTfrgAcJ01FjliY_11NZUk_sczMnv8_AilQ