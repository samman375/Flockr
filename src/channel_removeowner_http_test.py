'''
Frontend tests for channel_removeowner function
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import pytest
import requests

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

def test_valid_channel_removeowner_test_web(url):
    '''Valid case: valid use of channel_removeowner frontend, all inputs valid'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']
    u_id1 = payload['u_id']

    resp = requests.post(url + 'auth/register', json={
        'email': 'bobbrown@domain.com',
        'password': 'password2',
        'name_first': 'Bob',
        'name_last': 'Brown'
    })
    payload = resp.json()
    u_id2 = payload['u_id']

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp.json()
    ch_id1 = payload['channel_id']

    resp = requests.post(url + 'channel/invite', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    resp = requests.post(url + 'channel/addowner', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    resp = requests.get(url + 'channel/details', params={
        'token': token1,
        'channel_id': ch_id1
    })
    payload = json.loads(resp.text)

    assert payload['owner_members'] == [
        {
            'u_id': u_id1,
            'name_first': 'John',
            'name_last': 'Smith'
        },
        {
            'u_id': u_id2,
            'name_first': 'Bob',
            'name_last': 'Brown'
        }
    ]

    resp = requests.post(url + 'channel/removeowner', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })
    assert resp.status_code == 200

    resp = requests.get(url + 'channel/details', params={
        'token': token1,
        'channel_id': ch_id1
    })
    payload = json.loads(resp.text)

    assert payload['owner_members'] == [
        {
            'u_id': u_id1,
            'name_first': 'John',
            'name_last': 'Smith'
        }
    ]

def test_invalid_channelid_channel_removeowner_web(url):
    '''Invalid case: the channel with the given channel_id doesn't exist'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']

    resp = requests.post(url + 'auth/register', json={
        'email': 'bobbrown@domain.com',
        'password': 'password2',
        'name_first': 'Bob',
        'name_last': 'Brown'
    })
    payload = resp.json()
    u_id2 = payload['u_id']

    resp = requests.post(url + 'channel/removeowner', json={
        'token': token1,
        'channel_id': 3,
        'u_id': u_id2
    })

    assert resp.status_code == 400

def test_not_owner_removed_channel_removeowner_web(url):
    '''Invalid case: the user being removed as owner is not an owner'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']

    resp = requests.post(url + 'auth/register', json={
        'email': 'bobbrown@domain.com',
        'password': 'password2',
        'name_first': 'Bob',
        'name_last': 'Brown'
    })
    payload = resp.json()
    u_id2 = payload['u_id']

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp.json()
    ch_id1 = payload['channel_id']

    resp = requests.post(url + 'channel/invite', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    resp = requests.post(url + 'channel/removeowner', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    assert resp.status_code == 400

def test_caller_not_owner_channel_removeowner_web(url):
    '''Invalid case: the requesting user is not an owner of the flockr or channel'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']
    u_id1 = payload['u_id']

    resp = requests.post(url + 'auth/register', json={
        'email': 'bobbrown@domain.com',
        'password': 'password2',
        'name_first': 'Bob',
        'name_last': 'Brown'
    })
    payload = resp.json()
    token2 = payload['token']
    u_id2 = payload['u_id']

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp.json()
    ch_id1 = payload['channel_id']

    resp = requests.post(url + 'channel/invite', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    resp = requests.post(url + 'channel/removeowner', json={
        'token': token2,
        'channel_id': ch_id1,
        'u_id': u_id1
    })

    assert resp.status_code == 400
