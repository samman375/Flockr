'''
Frontend tests for auth_logout function
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


def test_valid_auth_logout_web(url):
    '''Valid case: simple test for valid auth_logout frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    payload = resp.json()
    token = payload['token']
    resp = requests.post(url + 'auth/logout', json={
        'token': token
    })
    payload = resp.json()
    assert resp.status_code == 200
    assert payload['is_success']

def test_auth_logout_web_invalid_token(url):
    '''Invalid case: invalid token used'''
    requests.delete(url + 'clear')

    requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    resp = requests.post(url + 'auth/logout', json={
        'token': 'invalid'
    })
    payload = resp.json()

    assert not payload['is_success']
