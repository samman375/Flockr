'''
Functions for registering, logging-in, logging-out users, storing user data/tokens, passwordreset
'''

import re
import random
import smtplib
import ssl
from hashlib import sha256
import jwt
from data import data_user, current_tokens, current_passwordreset_codes
from error import InputError
from webtoken import token_validate, token_create

SECRET = 'aqdiojf123a'

def auth_register(email, password, name_first, name_last):
    '''
    REGISTERING NEW USERS
    Checking for valid email, password, name, and last name before storing
    user data in the data_user nested dictionary, as well as assigning
    permissions, an active token, and u_id.
    '''

    # Validating email
    regex_email = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

    if not re.search(regex_email, email):
        raise InputError(description='Invalid email structure')

    for user in data_user:
        if data_user[user]['email'] == email:
            raise InputError(description='This email has already been used')

    # Validating password
    if len(password) < 6:
        raise InputError(description='Passwords must be at least 6 characters long')

    # Validating name_first
    if not (len(name_first) >= 1 and len(name_first) <= 50):
        raise InputError(description='First names must be between 1 and 50 characters (inclusive)')

    regex_name = r"^[a-zA-Z]+(?:[-.'\s][a-zA-Z]+)*$"

    if not re.search(regex_name, name_first):
        raise InputError(
            description="First names can only contain alphabetical characters and: . - '"
        )

    # Validating name_last
    if not (len(name_last) >= 1 and len(name_last) <= 50):
        raise InputError(description='Last names must be between 1 and 50 characters (inclusive)')

    if not re.search(regex_name, name_last):
        raise InputError(
            description="Last names can only contain alphabetical characters and: . -'"
        )

    # Generating user ID
    u_id = 0
    for user in data_user:
        u_id += 1

    # Generating handle
    handle = auth_generate_handle(u_id, name_first, name_last)

    # Adding new user to data_user list, adding token to active token list
    data_user[u_id] = {}

    data_user[u_id]['handle_str'] = handle
    data_user[u_id]['email'] = email
    data_user[u_id]['password'] = sha256(password.encode()).hexdigest()
    data_user[u_id]['name_first'] = name_first
    data_user[u_id]['name_last'] = name_last

    if u_id == 0:
        data_user[u_id]['permission_id'] = 1
    else:
        data_user[u_id]['permission_id'] = 2

    new_token = token_create(u_id)
    current_tokens.append(new_token)

    return {
        'u_id': u_id,
        'token': new_token,
    }


def auth_generate_handle(u_id, name_first, name_last):
    '''
    GENERATING A UNIQUE USER HANDLE_STR
    '''
    handle = name_first.lower() + name_last.lower()

    while len(handle) > 20:
        handle = handle[:-1]

    for user in data_user:
        if data_user[user]['handle_str'] == handle:
            handle = handle[:-1]
            if u_id > 9:
                handle = handle[:-1]
            handle = handle + str(u_id)

    return handle


def auth_login(email, password):
    '''
    LOGGING-IN REGISTERED USERS
    Checking that the given email and password are valid, assigning a new
    token for the user to remain authenticated during their session.
    '''
    hashed_pw = sha256(password.encode()).hexdigest()
    for user in data_user:
        if data_user[user]['email'] == email and data_user[user]['password'] == hashed_pw:
            new_token = token_create(user)
            if new_token not in current_tokens:
                current_tokens.append(new_token)
                return {
                    'u_id' : user,
                    'token': new_token
                }
            raise InputError(description='This account is already logged-in')

    raise InputError(description='Your email and/or password are incorrect')


def auth_logout(token):
    '''
    LOGGING-OUT AUTHENTICATED USERS
    Checking that the given token is currently valid, and removing the user
    from the list of currently authenticated users to log them out.
    '''
    for user in data_user:
        if token_validate(token) == user and token in current_tokens:
            current_tokens.remove(token)
            return {
                'is_success': True
            }
    return {
        'is_success': False
    }

def auth_passwordreset_request(email):
    '''
    REQUEST PASSWORD RESET
    Checks email is valid, sends secret code to email to be used to reset password
    Code stored in dictionary
    '''
    valid_user = False
    user_id = None
    for user in data_user:
        if data_user[user]['email'] == email:
            valid_user = True
            user_id = user

    if not valid_user:
        raise InputError(description='Invalid email provided')

    # Secret code encoded with jwt with code stored in dictionary
    secret_num = random.randint(1000, 9999)
    encoded_jwt = jwt.encode(
        {'secret_num': secret_num, 'u_id': user_id},
        SECRET,
        algorithm='HS256'
    ).decode('utf-8')
    current_passwordreset_codes[user_id] = secret_num

    # Create secure connection with google SMTP to send email
    # Code adapted from realpython.com
    port = 465
    sender_email = "cs1531flasktest@gmail.com"
    sender_password = "comp1531#4"
    message = f"""\
Subject: Flockr password reset

Code for password reset:
{encoded_jwt}

Copy and paste this code to reset password."""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message)

    return {}

def auth_passwordreset_reset(reset_code, new_password):
    '''
    RESET PASSWORD
    Given secret code, checks valid and changes password stored to given password
    Code removed from dictionary when successfully changed
    Valid password must be provided
    Function tested manually due to blackbox nature
    '''

    try:
        decoded_code = jwt.decode(reset_code.encode('utf-8'), SECRET, algorithms=['HS256'])
    except:
        raise InputError(description='Incorrect reset code provided')

    if "secret_num" not in decoded_code:
        raise InputError(description='Incorrect reset code provided')

    assert decoded_code['secret_num'] == 1

    user_id = decoded_code['u_id']

    valid_requesting_user = True
    if user_id not in current_passwordreset_codes:
        valid_requesting_user = False
    elif current_passwordreset_codes[user_id] != decoded_code['secret_num']:
        valid_requesting_user = False

    if not valid_requesting_user:
        raise InputError(description='Incorrect reset code provided')

    if len(new_password) < 6:
        raise InputError(description='Passwords must be at least 6 characters long')

    old_password = data_user[user_id]['password']

    if new_password == old_password:
        raise InputError(description='Password cannot be the same as old password')

    data_user[user_id]['password'] = sha256(new_password.encode()).hexdigest()

    del current_passwordreset_codes[user_id]

    return {}
