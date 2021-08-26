'''
Contains functions user* for viewing and editing profile
Written by Sam and Lochlan
'''

import re
import error
from data import data_user
from webtoken import token_validate

def user_profile(token, u_id):
    '''
    For a valid user returns information about user_id, email,
    first_name, last_name, handle

    Format of returned dictionary:
    {
        'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        }
    '''

    if u_id not in data_user:
        raise error.InputError('Invalid u_id')

    if token_validate(token) == 'INVALID':
        raise error.AccessError('Invalid token')

    user = {
        'u_id': u_id,
        'email': data_user[u_id]['email'],
        'name_first': data_user[u_id]['name_first'],
        'name_last': data_user[u_id]['name_last'],
        'handle_str': data_user[u_id]['handle_str']
    }

    return {'user': user}

def user_profile_setname(token, name_first, name_last):
    '''
    Updates authorised user's first and last name
    '''

    if token_validate(token) == 'INVALID':
        raise error.AccessError('Invalid token')

    user_id = token_validate(token)

    if not valid_name(name_first) or not valid_name(name_last):
        raise error.InputError('Invalid name')

    data_user[user_id]['name_first'] = name_first
    data_user[user_id]['name_last'] = name_last

    return {
    }

def user_profile_setemail(token, email):
    '''
    Updates authorised user's email address
    '''

    # Validate token

    if token_validate(token) == 'INVALID':
        raise error.AccessError('Invalid token')

    user_id = token_validate(token)

    # Validate email structure

    regex_email = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

    if not re.search(regex_email, email):
        raise error.InputError('Invalid email structure')

    for user in data_user:
        if data_user[user]['email'] == email:
            raise error.InputError('This email has already been used')

    # Change email as desired

    data_user[user_id]['email'] = email

    return {}

def user_profile_sethandle(token, handle_str):
    '''
    Updates authorised user's handle
    '''

    # Validate token

    if token_validate(token) == 'INVALID':
        raise error.AccessError('Invalid token')

    user_id = token_validate(token)

    # Validate handle string length

    if len(handle_str) < 4 or len(handle_str) > 19:
        raise error.InputError('Incorrect length')

    for user in data_user:
        if data_user[user]['handle_str'] == handle_str:
            raise error.InputError('This handle has already been used')

    # Change handle as desired

    data_user[user_id]['handle_str'] = handle_str

    return {}

def valid_name(name):
    '''
    Given a name checks to see if name is valid based on length and assumptions.md
    Returns Boolean
    '''

    if len(name) < 1 or len(name) > 50:
        return False

    match = re.search("^[A-z',. -]+$", name)
    if match is None:
        return False

    return True
