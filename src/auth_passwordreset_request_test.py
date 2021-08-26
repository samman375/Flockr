'''
Backend tests for auth_passwordreset_request function
'''

import pytest
from other import clear
import error
from auth import auth_register, auth_passwordreset_request, auth_logout

TEST_EMAIL = "cs1531flasktest@gmail.com"

def test_request_passwordreset_valid():
    '''Valid case: tests valid usage of auth_passwordreset_request
    User registered, logged out, password reset requested
    (email sent is tested manually)'''
    clear()

    us_dic = auth_register(TEST_EMAIL, "jimroberts", "jim", "roberts")
    token = us_dic['token']

    assert auth_logout(token)

    auth_passwordreset_request(TEST_EMAIL)

def test_request_passwordreset_invalid_email():
    '''Invalid case: non-registered email is used'''
    clear()

    with pytest.raises(error.InputError):
        auth_passwordreset_request(TEST_EMAIL)
        auth_passwordreset_request('INVALID')
        auth_passwordreset_request('adskljfakjslfj')
