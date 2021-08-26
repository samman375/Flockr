'''
Backend tests for auth_passwordreset_reset function
Assumes working auth_register, auth_login, auth_logout, auth_passwordreset_request
Valid case and invalid cases with valid secret code tested manually due to blackbox nature of tests
Valid secret code cases all succeeded
'''

import pytest
from other import clear
import error
import auth

TEST_EMAIL = "cs1531flasktest@gmail.com"

def test_request_passwordreset_invalid_code_1():
    '''
    Invalid case: tests invalid code supplied with registered user
    User registered, logged out, password reset requested, invalid code provided
    '''
    clear()

    auth.auth_register(TEST_EMAIL, "jimroberts", "jim", "roberts")

    auth.auth_passwordreset_request(TEST_EMAIL)

    with pytest.raises(error.InputError):
        auth.auth_passwordreset_reset("INVALID", "abcdefg")

def test_request_passwordreset_invalid_code_2():
    '''Invalid case: invalid code supplied without registered user'''
    clear()

    with pytest.raises(error.InputError):
        auth.auth_passwordreset_reset("INVALID", "abcdefg")
