'''
Frontend tests for channel_addowner function
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

def test_valid_channel_addowner_test_web(url):
    '''Valid case: simple valid use of channel_addowner frontend'''
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
    resp = requests.post(url + 'channel/addowner', json={
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
        },
        {
            'u_id': u_id2,
            'name_first': 'Bob',
            'name_last': 'Brown'
        }
    ]

def test_invalid_channelid_channel_addowner_web(url):
    '''Invalid case: invalid channel ID, checks that channel with given channel_id doesn't exist'''
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

    resp = requests.post(url + 'channel/addowner', json={
        'token': token1,
        'channel_id': 3,
        'u_id': u_id2
    })

    assert resp.status_code == 400

def test_already_owner_channel_addowner_web(url):
    '''Invalid case: user is already an owner of the channel'''
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

    resp = requests.post(url + 'channel/addowner', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    resp = requests.post(url + 'channel/addowner', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    assert resp.status_code == 400

def test_caller_not_owner_channel_addowner_web(url):
    '''Invalid case: requesting user is not an owner of the flockr or channel'''
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
    token2 = payload['token']
    u_id2 = payload['u_id']

    resp = requests.post(url + 'auth/register', json={
        'email': 'emmawilliams@domain.com',
        'password': 'password3',
        'name_first': 'Emma',
        'name_last': 'Williams'
    })
    payload = resp.json()
    u_id3 = payload['u_id']

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

    resp = requests.post(url + 'channel/invite', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id3
    })

    resp = requests.post(url + 'channel/addowner', json={
        'token': token2,
        'channel_id': ch_id1,
        'u_id': u_id3
    })

    assert resp.status_code == 400
