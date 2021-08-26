'''
Frontend tests for channel_invite function
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

def test_valid_channel_invite_web(url):
    '''Valid case: simple valid use of channel_invite frontend, all inputs valid'''
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
    assert resp.status_code == 200

    resp = requests.get(url + 'channel/details', params={
        'token': token1,
        'channel_id': ch_id1
    })
    payload = json.loads(resp.text)

    assert payload['all_members'] == [
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

def test_invalid_channelid_channel_invite_web(url):
    '''Invalid case: the given channel_id doesn't exist'''
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

    assert resp.status_code == 200

    resp = requests.post(url + 'channel/invite', json={
        'token': token1,
        'channel_id': 3,
        'u_id': u_id2
    })

    assert resp.status_code == 400

def test_invalid_userid_channel_invite_web(url):
    '''Invalid case: the user being invited doesn't exist (invalid u_id)'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp.json()
    ch_id1 = payload['channel_id']

    assert resp.status_code == 200

    resp = requests.post(url + 'channel/invite', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': 3
    })

    assert resp.status_code == 400

def test_user_not_member_channel_invite_web(url):
    '''Invalid case: the authorised user is not in channel with given channel ID'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name1@domain.com',
        'password': 'password1',
        'name_first': 'First',
        'name_last': 'Last'
    })
    payload = resp.json()
    token1 = payload['token']

    resp = requests.post(url + 'auth/register', json={
        'email': 'name2@domain.com',
        'password': 'password12',
        'name_first': 'John',
        'name_last': 'Smith'
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

    assert resp.status_code == 200

    resp = requests.post(url + 'channel/invite', json={
        'token': token2,
        'channel_id': ch_id1,
        'u_id': u_id2
    })

    assert resp.status_code == 400

def test_user_already_member_channel_invite_web(url):
    '''Invalid case case: inviting a user who is already a member of the channel.'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name1@domain.com',
        'password': 'password1',
        'name_first': 'First',
        'name_last': 'Last'
    })
    payload = resp.json()
    token1 = payload['token']

    resp = requests.post(url + 'auth/register', json={
        'email': 'name2@domain.com',
        'password': 'password12',
        'name_first': 'John',
        'name_last': 'Smith'
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
    assert resp.status_code == 200

    resp = requests.post(url + 'channel/invite', json={
        'token': token1,
        'channel_id': ch_id1,
        'u_id': u_id2
    })
    assert resp.status_code == 400
