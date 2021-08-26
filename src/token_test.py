'''
Tests for functions in webtoken file
'''

from webtoken import token_create, token_validate
from other import clear
from data import current_tokens
from auth import auth_register


def test_token_valid():
    '''Valid case: valid token used'''
    clear()

    auth_register('bob@gmail.com', 'hellothere', 'Bob', 'Marley')
    encoded = token_create(0)
    current_tokens.append(encoded)
    assert token_validate(encoded) == 0


def test_u_id_invalid():
    '''Invalid case: incorrect signature used'''
    clear()

    encoded = token_create(0)
    assert token_validate(encoded) == 'INVALID'


def test_invalid_token():
    '''Invalid case: invalid token string used'''
    clear()

    # String concatenated due to pylint
    string1 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    string2 = '.eyJ1c2VyX2lkIjo1fQ.7I3D_DJjBcMdyu2eI'
    string3 = '6oejdFR4hDpm43yIlht8cVHi8A'
    string = string1 + string2 + string3

    assert token_validate(string) == 'INVALID'
