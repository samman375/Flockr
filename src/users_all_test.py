'''
Backend tests for users_all function
'''

import pytest
from data import current_tokens
from auth import auth_register as register
from error import AccessError
from other import clear, users_all


# VALID TOKEN

def test_valid_token():
    '''Valid case: valid token'''
    clear()
    token = register('name@domain.com', 'password', 'First', 'Last')['token']
    assert token in current_tokens
    users_all(token)

def test_invalid_token():
    '''Invalid case: token not currently valid'''
    clear()
    assert 'sometoken' not in current_tokens
    with pytest.raises(AccessError):
        users_all('sometoken')


# CORRECT DATA RETURNED

def test_valid_data():
    '''Valid case: valid data returned by function.'''
    clear()
    token = register('name@domain.com', 'password', 'Some', 'Name')['token']
    register('anothername@domain.com', 'password', 'Another', 'Person')
    returned_data = users_all(token)
    assert returned_data == {
        'users': [
            {
                'u_id': 0,
                'email': 'name@domain.com',
                'name_first': 'Some',
                'name_last': 'Name',
                'handle_str': 'somename'
            },
            {
                'u_id': 1,
                'email': 'anothername@domain.com',
                'name_first': 'Another',
                'name_last': 'Person',
                'handle_str': 'anotherperson'
            },
        ]
    }
