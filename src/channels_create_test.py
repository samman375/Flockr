'''
Backend tests for channels_create() function
'''

import pytest
from channels import channels_create
from error import InputError, AccessError
import auth
from other import clear


def test_name_valid():
    '''Valid case: creates a channel with all valid parameters'''
    clear()

    info1 = auth.auth_register("john.smith@gmail.com", "Johnsmith1", "John", "Smith")
    token1 = info1['token']

    # public channel with valid name, should pass
    assert channels_create(token1, 'channel0', True)['channel_id'] == 0

    # private channel with valid name, should pass
    assert channels_create(token1, 'channel1', False)['channel_id'] == 1

def test_name_invalid_public():
    '''Invalid case: raises input error given an invalid name for a public channel'''
    clear()

    info2 = auth.auth_register("emmawil@domain.com", "emmawils2", "Emma", "Wilson")

    token2 = info2['token']

    with pytest.raises(InputError):
        # public channel with invalid name, should fail
        channels_create(token2, "nameismorethantwentycharacters", True)

def test_name_invalid_private():
    '''Invalid case: raises input error given an invalid name for a private channel'''
    clear()

    info3 = auth.auth_register("first.last@domain.com", "password123", "First", "Last")
    token3 = info3['token']

    with pytest.raises(InputError):
        # private channel with invalid name, should fail
        channels_create(token3, "nameismorethantwentycharacters", False)

def test_invalid_token_public():
    '''Invalid case: raises access error given an invalid token for a public channel'''
    clear()

    # public channel with invalid token, should fail
    with pytest.raises(AccessError):
        channels_create("wrong", "Name", True)

def test_invalid_token_private():
    '''Invalid case: raises access error given an invalid name for a private channel'''
    clear()

    # public channel with invalid token, should fail
    with pytest.raises(AccessError):
        channels_create("wrong", "Name", False)
