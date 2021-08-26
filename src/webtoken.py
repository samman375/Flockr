'''
Functions for creating and validating tokens
by Lochlan and Sam
'''
import jwt
from data import data_user, current_tokens

SECRET = 'beans_123'

def token_create(u_id):
    '''
    CREATING TOKENS
    returns encoded jwt string
    '''

    encoded_jwt = jwt.encode({'user_id': u_id}, SECRET, algorithm='HS256').decode('utf-8')
    return encoded_jwt

def token_validate(token):
    '''
    VALIDATING TOKENS
    Returns u_id if valid
    Returns 'INVALID' if invalid or not online
    '''

    if token not in current_tokens:
        return 'INVALID'

    try:
        decoded_token = jwt.decode(token.encode('utf-8'), SECRET, algorithms=['HS256'])
    except:
        return 'INVALID'

    decoded_u_id = decoded_token['user_id']

    if decoded_u_id in data_user:
        return decoded_u_id

    return 'INVALID'
