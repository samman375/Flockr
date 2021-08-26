'''
Frontend tests for channels_listall function
'''

import re
import json
from subprocess import Popen, PIPE
import signal
from time import sleep
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


def test_valid_channels_listall_web(url):
    '''Valid case: valid use of channels_listall frontend, all inputs valid'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name1@domain.com',
        'password': 'password1',
        'name_first': 'John',
        'name_last': 'Smith'
    })

    payload = resp.json()
    token1 = payload['token']

    resp = requests.post(url + 'auth/register', json={
        'email': 'name2@domain.com',
        'password': 'password2',
        'name_first': 'Bob',
        'name_last': 'Brown'
    })

    payload = resp.json()
    token2 = payload['token']

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    payload = resp.json()
    channel_id1 = payload['channel_id']

    resp = requests.post(url + 'channels/create', json={
        'token': token2,
        'name': 'Channel B',
        'is_public': True
    })
    payload = resp.json()
    channel_id2 = payload['channel_id']

    resp = requests.get(url + 'channels/listall', params={'token': token1})
    assert resp.status_code == 200
    payload = json.loads(resp.text)
    assert payload['channels'] == [
        {
            "channel_id": channel_id1,
            "name"      : "Channel A",
        },
        {
            "channel_id": channel_id2,
            "name"      : "Channel B",
        },
    ]

def test_invalid_token_channels_listall_web(url):
    '''Invalid case: invalid token used in channels_listall frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password123',
        'name_first': 'John',
        'name_last': 'Smith'
    })

    payload = resp.json()
    token = payload['token']

    resp = requests.post(url + 'channels/create', json={
        'token': token,
        'name': 'Channel A',
        'is_public': True
    })

    resp = requests.post(url + 'channels/create', json={
        'token': token,
        'name': 'Channel B',
        'is_public': True
    })

    resp = requests.get(url + 'channels/listall', params={'token': 'invalid'})

    assert resp.status_code == 400
