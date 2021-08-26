'''
Backend tests for user_profile_sethandle function
'''

import pytest
import error
from auth import auth_register
from user import user_profile, user_profile_sethandle
from other import clear
from webtoken import token_validate


def test_user_sethandle_valid_1():
    '''Valid case: handle is valid length, minimum'''
    clear()

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    user_profile_sethandle(test_token, 'dogs')

    assert user_profile(test_token, token_validate(test_token))['user']['handle_str'] == 'dogs'

def test_user_sethandle_valid_2():
    '''Valid case: handle is valid length, maximum'''
    clear()

    longhandlestring = 'isalonghandlestring'

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    user_profile_sethandle(test_token, longhandlestring)

    assert user_profile(test_token, token_validate(test_token))['user']['handle_str'] == longhandlestring

def test_user_sethandle_invalid_1():
    '''Invalid case: handle is invalid length, below minimum'''
    clear()

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    with pytest.raises(error.InputError):
        user_profile_sethandle(test_token, 'dog')

def test_user_sethandle_invalid_2():
    '''Invalid case: handle is invalid length, above maximum'''
    clear()

    test_user = auth_register('name@domain.com', 'password', 'First', 'Last')
    test_token = test_user['token']

    with pytest.raises(error.InputError):
        user_profile_sethandle(test_token, 'thisstringistoolongtobeahandlestring')

def test_user_sethandle_invalid_token():
    '''Invalid case: token used is not valid'''
    clear()

    auth_register('name@domain.com', 'password', 'First', 'Last')

    with pytest.raises(error.AccessError):
        user_profile_sethandle('invalid', 'handlestring')

def test_user_sethandle_already_used():
    '''Invalid case: handle is already being used by another user'''
    clear()

    auth_register('dontcopy@domain.com', 'password', 'First', 'Last')
    test_user = auth_register('name@domain.com', 'password', 'test', 'user')
    test_token = test_user['token']

    with pytest.raises(error.InputError):
        user_profile_sethandle(test_token, 'firstlast')
