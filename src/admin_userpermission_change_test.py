'''
Backend tests for admin_userpermission_change function
'''

import pytest
from data import data_user, current_tokens
from auth import auth_register as register
from error import AccessError, InputError
from other import clear, admin_userpermission_change as permission_change


def generating_data():
    '''GENERATING DATA USED IN EACH TEST-CASE'''
    clear()
    test_data = {}

    flockr_owner = register('flockrowner@domain.com', 'password', 'First', 'Last')
    test_data['token_flockr_owner'] = flockr_owner['token']
    test_data['id_flockr_owner'] = flockr_owner['u_id']

    member1 = register('member1@domain.com', 'password', 'First', 'Last')
    test_data['token_member1'] = member1['token']
    test_data['id_member1'] = member1['u_id']

    member2 = register('member2@domain.com', 'password', 'First', 'Last')
    test_data['token_member2'] = member2['token']
    test_data['id_member2'] = member2['u_id']

    member3 = register('member3@domain.com', 'password', 'First', 'Last')
    test_data['token_member3'] = member3['token']
    test_data['id_member3'] = member3['u_id']

    return test_data


def checking_permission_id(user_id, wanted_id):
    '''GIVEN A U_ID, CHECK THE USER'S PERMISSION_ID MATCHES WANTED_ID'''
    for user in data_user:
        if user == user_id:
            assert data_user[user]['permission_id'] == wanted_id


# VALID TOKEN

def test_permissionchange_valid_token():
    '''Valid case: valid token'''
    clear()
    data = generating_data()
    assert data['token_flockr_owner'] in current_tokens
    permission_change(data['token_flockr_owner'], data['id_member1'], 1)
    checking_permission_id(data['id_member1'], 1)

def test_permissionchange_invalid_token():
    '''Invalid case: token not currently valid'''
    clear()
    data = generating_data()
    with pytest.raises(AccessError):
        permission_change('token', data['id_member1'], 1)
    checking_permission_id(data['id_member1'], 2)


# VALID U_ID

def test_permissionchange_multiple_valid_u_id():
    '''Valid case: owner changes permission_id of three users using valid u_id's'''
    clear()
    data = generating_data()
    permission_change(data['token_flockr_owner'], data['id_member1'], 1)
    checking_permission_id(data['id_member1'], 1)

    clear()
    data = generating_data()
    permission_change(data['token_flockr_owner'], data['id_member2'], 1)
    checking_permission_id(data['id_member2'], 1)

    clear()
    data = generating_data()
    permission_change(data['token_flockr_owner'], data['id_member3'], 1)
    checking_permission_id(data['id_member3'], 1)

def test_permissionchange_invalid_u_id():
    '''Invalid case: invalid u_id'''
    clear()
    data = generating_data()
    with pytest.raises(InputError):
        permission_change(data['token_flockr_owner'], 'some_u_id', 1)


# VALID PERMISSION_ID

def test_permissionchange_valid_permission_id_both():
    '''Valid case: owner changing permission_id of user from 2 to 1 and back to 2'''
    clear()
    data = generating_data()
    permission_change(data['token_flockr_owner'], data['id_member1'], 1)
    checking_permission_id(data['id_member1'], 1)

    permission_change(data['token_flockr_owner'], data['id_member1'], 2)
    checking_permission_id(data['id_member1'], 2)

def test_permissionchange_invalid_permission_id_0():
    '''Valid case: invalid permission_id'''
    clear()
    data = generating_data()
    with pytest.raises(InputError):
        permission_change(data['token_flockr_owner'], data['id_member1'], 0)

def test_permissionchange_invalid_permission_id_3():
    '''Valid case: invalid permission_id'''
    clear()
    data = generating_data()
    with pytest.raises(InputError):
        permission_change(data['token_flockr_owner'], data['id_member1'], 3)

def test_permissionchange_invalid_permission_id_negative_1():
    '''Valid case: invalid permission_id'''
    clear()
    data = generating_data()
    with pytest.raises(InputError):
        permission_change(data['token_flockr_owner'], data['id_member1'], -3)


# SETTING A USER'S PERMISSION_ID TO THEIR CURRENT PERMISSION_ID (NO EFFECT)

def test_permissionchange_valid_permission_id_unchanged():
    '''Valid case: no change to permission ID'''
    clear()
    data = generating_data()
    permission_change(data['token_flockr_owner'], data['id_member1'], 2)
    checking_permission_id(data['id_member1'], 2)


# AUTHORISED USER IS NOT AN OWNER

def test_permissionchange_valid_authorised_user_is_owner():
    '''Valid case: authorised user is an owner'''
    clear()
    data = generating_data()
    checking_permission_id(data['id_flockr_owner'], 1)
    permission_change(data['token_flockr_owner'], data['id_member1'], 1)
    checking_permission_id(data['id_member1'], 1)

def test_permissionchange_invalid_authorised_user_is_not_owner():
    '''Valid case: authorised user is not an owner'''
    clear()
    data = generating_data()
    checking_permission_id(data['id_member1'], 2)
    with pytest.raises(AccessError):
        permission_change(data['token_member1'], data['id_member2'], 1)
    checking_permission_id(data['id_member2'], 2)


# OWNER CHANGING THEIR OWN PERMISSION_ID

def test_permissionchange_valid_another_owner():
    '''Valid case: owner changes their own permission_id, valid since
    there is also currently another owner'''
    clear()
    data = generating_data()
    checking_permission_id(data['id_flockr_owner'], 1)
    permission_change(data['token_flockr_owner'], data['id_member1'], 1)
    checking_permission_id(data['id_member1'], 1)
    permission_change(data['token_flockr_owner'], data['id_flockr_owner'], 2)
    checking_permission_id(data['id_flockr_owner'], 2)

def test_permissionchange_invalid_only_owner_changes_permissions():
    '''Invdalid case: owner changes their own permission_id, invalid since
    they are currently the only flockr owner'''
    clear()
    data = generating_data()
    checking_permission_id(data['id_flockr_owner'], 1)
    with pytest.raises(InputError):
        permission_change(data['token_flockr_owner'], data['id_flockr_owner'], 2)
    checking_permission_id(data['id_flockr_owner'], 1)
