'''
Frontend tests for channel_messages function
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


def test_valid_channel_messages_web(url):
    '''Valid case: valid use of channel_messages, all inputs valid'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']

    resp1 = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp1.json()
    ch_id1 = payload['channel_id']

    resp2 = requests.post(url + 'message/send', json={
        'token': token1,
        'channel_id': ch_id1,
        'message': 'Hello'
    })
    assert resp2.status_code == 200

    resp3 = requests.get(url + 'channel/messages', params={
        'token': token1,
        'channel_id': ch_id1,
        'start': 1
    })
    assert resp3.status_code == 200
    payload = json.loads(resp3.text)

    assert len(payload['messages']) == 1
    assert payload['start'] == 1
    assert payload['end'] == -1

def test_invalid_channelid_channel_messages_web(url):
    '''Invalid case: the given channel_id does not exist'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']

    resp2 = requests.get(url + 'channel/messages', params={
        'token': token1,
        'channel_id': 3,
        'start': 1
    })

    assert resp2.status_code == 400

def test_invalid_start_channel_messages_web(url):
    '''Invalid case: 'start' is greater than the total number of messages in channel'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'johnsmith@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })
    payload = resp.json()
    token1 = payload['token']

    resp1 = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp1.json()
    ch_id1 = payload['channel_id']

    resp2 = requests.post(url + 'message/send', json={
        'token': token1,
        'channel_id': ch_id1,
        'message': 'Hello'
    })
    assert resp2.status_code == 200

    resp3 = requests.get(url + 'channel/messages', params={
        'token': token1,
        'channel_id': ch_id1,
        'start': 2
    })

    assert resp3.status_code == 400

def test_user_not_owner_channel_messages_web(url):
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

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp.json()
    ch_id1 = payload['channel_id']

    resp = requests.get(url + 'channel/messages', params={
        'token': token2,
        'channel_id': ch_id1,
        'start': 1
    })

    assert resp.status_code == 400
