'''
Frontend tests for channels_create function
'''

import re
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

def test_valid_channels_create_web(url):
    '''Valid case: valid use of channels_create frontend, all inputs valid'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password123',
        'name_first': 'First',
        'name_last': 'Last'
    })

    payload = resp.json()
    token = payload['token']

    resp = requests.post(url + 'channels/create', json={
        'token': token,
        'name': 'Channel A',
        'is_public': True
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert payload['channel_id'] == 0

def test_invalid_name_channels_create_web(url):
    '''Invalid case: invalid name is used (exceeds the 20 character limit)'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password123',
        'name_first': 'First',
        'name_last': 'Last'
    })

    payload = resp.json()
    token = payload['token']

    resp = requests.post(url + 'channels/create', json={
        'token': token,
        'name': 'nameismorethantwentycharacters',
        'is_public': True
    })

    assert resp.status_code == 400

def test_invalid_token_channels_create_web(url):
    '''Invalid case: invalid token used'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password123',
        'name_first': 'First',
        'name_last': 'Last'
    })

    resp = requests.post(url + 'channels/create', json={
        'token': 'invalid',
        'name': 'Channel A',
        'is_public': True
    })

    assert resp.status_code == 400
