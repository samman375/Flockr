'''
Backend tests for auth_login function
'''

import pytest
import auth
from webtoken import token_validate, token_create
from data import current_tokens
from other import clear
from error import InputError

# DOES EMAIL ENTERED BELONG TO A USER

def test_login_email_exists():
    '''Valid case: valid email/password + logs-out before logging back in'''
    clear()
    token = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['token']
    auth.auth_logout(token)
    auth.auth_login('name@domain.com', 'password')

def test_login_email_doesnt_exist():
    '''Invalid case: invalid email'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')
    with pytest.raises(InputError):
        auth.auth_login('differentname@domain.com', 'password')


# IS PASSWORD CORRECT

def test_login_password_correct():
    '''Valid case: password is correct'''
    clear()
    token = auth.auth_register('name@domain.com', 'correctpassword#123', 'First', 'Last')['token']
    auth.auth_logout(token)
    auth.auth_login('name@domain.com', 'correctpassword#123')

def test_login_password_incorrect():
    '''Valid case: password doesn't match email'''
    clear()
    auth.auth_register('name@domain.com', 'correctpassword#123', 'First', 'Last')
    with pytest.raises(InputError):
        auth.auth_login('name@domain.com', 'wrongpassword_456')


# IS USER ALREADY LOGGED-IN

def test_login_already_logged_in():
    '''Invalid case: already logged-in (can't be authenticated more than once at a time)'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')
    with pytest.raises(InputError):
        auth.auth_login('name@domain.com', 'password')


# CORRECTLY GENERATES NEW TOKEN

def test_login_valid_token():
    '''Valid case: token is generated correctly'''
    clear()
    user = auth.auth_register('name@domain.com', 'password', 'First', 'Last')
    assert token_validate(user['token']) == user['u_id']

def test_login_invalid_token():
    '''Invalid case: token is added to current_token but doesn't correspond to registered user'''
    clear()
    token = token_create(1)
    current_tokens.append(token)
    assert token_validate(token) == 'INVALID'
