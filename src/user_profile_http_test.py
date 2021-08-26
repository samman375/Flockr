'''
Frontend tests for user_profile function
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import pytest
import requests
from other import clear


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

def test_valid_user_profile_web(url):
    '''Valid case: all inputs valid, profile is correctly returned'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'jim.roberts1@email.com',
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    payload = resp.json()
    token1 = payload['token']
    u_id1 = payload['u_id']

    resp = requests.get(url + 'user/profile', params={
        'token': token1,
        'u_id': u_id1
    })
    assert resp.status_code == 200
    payload = json.loads(resp.text)

    assert payload['user'] == {
        'u_id': u_id1,
        'email': 'jim.roberts1@email.com',
        'name_first': 'jim',
        'name_last': 'roberts',
        'handle_str': "jimroberts"
    }

def test_invalid_user_profile_web(url):
    '''Invalid case: invalid token used'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'jim.roberts1@email.com',
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    payload = resp.json()
    u_id1 = payload['u_id']

    resp = requests.get(url + 'user/profile', params={
        'token': 'invalid',
        'u_id': u_id1
    })

    assert resp.status_code == 400
