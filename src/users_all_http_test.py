'''
Frontend tests for users_all function
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


def test_users_empty_invalid_web(url):
    '''Invalid case: no users registered, invalid token'''
    clear()
    resp = requests.get(url + 'users/all', params={
        'token' : 'some invalid token'
    })
    assert resp.status_code == 400


def test_users_all_single_web(url):
    '''Valid case: single user registered, their data is returned correctly'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    user = resp.json()
    token = user['token']
    u_id = user['u_id']
    
    resp = requests.get(url + 'users/all', params={
        'token': token
    })
    assert resp.status_code == 200
    payload = json.loads(resp.text)
    assert payload == {
        'users' : [{
            'u_id' : u_id,
            'email': 'name@domain.com',
            'name_first': 'First',
            'name_last': 'Last',
            'handle_str' : 'firstlast'
        }]
    
    }

def test_users_all_multiple_web(url):
    '''Valid case: multiple users registered, all data is returned correctly'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    user1 = resp.json()
    token1 = user1['token']
    u_id1 = user1['u_id']
    
    resp = requests.post(url + 'auth/register', json={
        'email': 'another@domain.com',
        'password': 'password',
        'name_first': 'Another',
        'name_last': 'Name'
    })
    user2 = resp.json()
    token2 = user2['token']
    u_id2 = user2['u_id']

    resp = requests.post(url + 'auth/register', json={
        'email': 'someoneelse@domain.com',
        'password': 'password',
        'name_first': 'Someone',
        'name_last': 'Else'
    })
    user3 = resp.json()
    u_id3 = user3['u_id']

    correct_data = {
        'users' : [
            {
                'u_id' : u_id1,
                'email': 'name@domain.com',
                'name_first': 'First',
                'name_last': 'Last',
                'handle_str' : 'firstlast'
            }, {
                'u_id' : u_id2,
                'email': 'another@domain.com',
                'name_first': 'Another',
                'name_last': 'Name',
                'handle_str' : 'anothername'
            }, {
                'u_id' : u_id3,
                'email': 'someoneelse@domain.com',
                'name_first': 'Someone',
                'name_last': 'Else',
                'handle_str' : 'someoneelse'
            }
        ]
    }

    resp = requests.get(url + 'users/all', params={
        'token': token1
    })
    assert resp.status_code == 200
    payload = json.loads(resp.text)
    assert payload == correct_data

    resp = requests.get(url + 'users/all', params={
        'token': token2
    })
    assert resp.status_code == 200
    payload = json.loads(resp.text)
    assert payload == correct_data
