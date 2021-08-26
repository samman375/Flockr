'''
Frontend tests for admin_userpermission_change function
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import pytest
import requests
from other import clear
import jwt
from data import data_user, current_tokens, data_channel, data_messages


# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    '''
    Starts server
    '''
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")


def generating_data(url):
    '''GENERATING DATA USED IN EACH TEST-CASE'''
    data = {}
    resp = requests.post(url + 'auth/register', json = {
        'email': 'name@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    owner = resp.json()
    data['owner_token'] = owner['token']
    data['owner_id'] = owner['u_id']

    resp = requests.post(url + 'auth/register', json = {
        'email': 'anothername@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    user = resp.json()
    data['user1_token'] = user['token']
    data['user1_id'] = user['u_id']

    resp = requests.post(url + 'auth/register', json = {
        'email': 'yetanothername@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    user = resp.json()
    data['user2_token'] = user['token']
    data['user2_id'] = user['u_id']

    return data


# VALID TOKEN

def test_permissionchange_valid_token_web(url):
    '''Valid case: valid token'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 1
    })
    assert resp.status_code == 200

def test_permissionchange_invalid_token_web(url):
    '''Invalid case: token not currently valid'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': 'some_invalid_token',
        'u_id': data['user1_id'],
        'permission_id': 1
    })
    assert resp.status_code == 400


# VALID U_ID

def test_permissionchange_multiple_valid_u_id_web(url):
    '''Valid case: owner changes permission_id of three users using valid u_id's'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 1
    })
    assert resp.status_code == 200

    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user2_id'],
        'permission_id': 1
    })
    assert resp.status_code == 200

def test_permission_change_invalid_u_id_web(url):
    '''Invalid case: invalid u_id'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': 'some_id',
        'permission_id': 1
    })
    assert resp.status_code == 400


# VALID PERMISSION_ID

def test_permissionchangevalid_permission_id_both_web(url):
    '''Valid case: owner changing permission_id of user from 2 to 1 and back to 2'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 1
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 2
    })
    assert resp.status_code == 200

def test_permissionchange_invalid_permission_id_web(url):
    '''Valid case: invalid permission_id'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 0
    })
    assert resp.status_code == 400


# SETTING A USER'S PERMISSION_ID TO THEIR CURRENT PERMISSION_ID (NO EFFECT)

def test_permissionchange_valid_permission_id_unchanged_web(url):
    '''Valid case: no change to permission ID'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 2
    })
    assert resp.status_code == 200


# AUTHORISED USER IS NOT AN OWNER

def test_permissionchange_valid_authorised_user_is_owner_web(url):
    '''Valid case: authorised user is an owner'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 1
    })
    assert resp.status_code == 200

def test_permissionchange_invalid_authorised_user_is_not_owner_web(url):
    '''Valid case: authorised user is not an owner'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['user1_token'],
        'u_id': data['user2_id'],
        'permission_id': 1
    })
    assert resp.status_code == 400


# OWNER CHANGING THEIR OWN PERMISSION_ID

def test_permissionchange_valid_another_owner_web(url):
    '''Valid case: owner changes their own permission_id, valid since
    there is also currently another owner'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['user1_id'],
        'permission_id': 1
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['owner_id'],
        'permission_id': 2
    })
    assert resp.status_code == 200

def test_permissionchange_invalid_only_owner_changes_permissions_web(url):
    '''Invdalid case: owner changes their own permission_id, invalid since
    they are currently the only flockr owner'''
    requests.delete(url + 'clear')
    data = generating_data(url)
    resp = requests.post(url + 'admin/userpermission/change', json = {
        'token': data['owner_token'],
        'u_id': data['owner_id'],
        'permission_id': 2
    })
    assert resp.status_code == 400
