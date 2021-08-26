'''
Backend tests for user_profile_setemail function
'''

import pytest
import error

from auth import auth_register
from user import user_profile, user_profile_setemail
from other import clear
from webtoken import token_validate


def test_user_setemail_valid_1():
    '''Valid case: valid email structure'''
    clear()

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    user_profile_setemail(test_token, 'domain@name.com')

    assert user_profile(test_token, token_validate(test_token))['user']['email'] == 'domain@name.com'

def test_user_setemail_valid_2():
    '''Valid case: valid email structure including numbers and punctuation'''
    clear()

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    user_profile_setemail(test_token, 'name.123@domain.com')

    assert user_profile(test_token, token_validate(test_token))['user']['email'] == 'name.123@domain.com'

def test_user_setemail_invalid_1():
    '''Invalid case: invalid email structure (missing domain)'''
    clear()

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    with pytest.raises(error.InputError):
        user_profile_setemail(test_token, 'v4/1d.NAME')

def test_user_setemail_invalid_2():
    '''Invalid case: invalid email structure (missing .com)'''
    clear()

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    with pytest.raises(error.InputError):
        user_profile_setemail(test_token, 'name@domain') 

def test_user_setemail_invalid_token():
    '''Invalid case: invalid token used'''
    clear()

    auth_register('name@domain.com', 'password', 'First', 'Last')

    with pytest.raises(error.AccessError):    
        user_profile_setemail('invalid', 'v4/1d.NAME@domain.com')

def test_user_setemail_already_used():
    '''Invalid case: email is already being used by another user'''
    clear()

    auth_register('dontcopy@domain.com', 'password', 'First', 'Last')
    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    with pytest.raises(error.InputError):
        user_profile_setemail(test_token, 'dontcopy@domain.com')
