'''
Backend tests for auth_logout function
'''

import auth
from webtoken import token_validate
from other import clear

# VALID TOKEN

def test_successful_logout():
    '''Valid case: token is valid'''
    clear()
    user = auth.auth_register('name@domain.com', 'password', 'First', 'Last')
    assert token_validate(user['token']) == user['u_id']
    assert auth.auth_logout(user['token']) == {'is_success': True}

def test_unsuccessful_logout():
    '''Invalid case: token is not currently valid'''
    clear()
    assert auth.auth_logout('sometoken') == {'is_success': False}


# REPEATED LOGINS/LOGOUTS

def test_successful_repeated_logins():
    '''Valid case: token is valid (logged-in, logged-out, logged-in again)'''
    clear()
    token = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['token']
    assert auth.auth_logout(token) == {'is_success': True}
    token1 = auth.auth_login('name@domain.com', 'password')['token']
    assert auth.auth_logout(token1) == {'is_success': True}

def test_unsuccessful_repeated_logins():
    '''Invalid case: token is invalid (already logged-out with the token)'''
    clear()
    token = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['token']
    assert auth.auth_logout(token) == {'is_success': True}
    assert auth.auth_logout(token) == {'is_success': False}
