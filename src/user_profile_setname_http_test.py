'''
Frontend tests for user_profile_setname function
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


def test_user_setname_valid_web(url):
    '''Valid case: user correctly registered, names should change'''
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

    resp = requests.put(url + 'user/profile/setname', json={
        'token': token1,
        'name_first': 'bob',
        'name_last': 'marley'
    })
    assert resp.status_code == 200
    resp = requests.get(url + 'user/profile', params={
        'token': token1,
        'u_id': u_id1
    })

    payload = json.loads(resp.text)

    assert payload['user']['name_first'] == 'bob'
    assert payload['user']['name_last'] == 'marley'

def test_user_setname_invalid_web(url):
    '''Invalid case: names use invalid structure'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'jim.roberts1@email.com',
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    payload = resp.json()
    token1 = payload['token']

    resp = requests.put(url + 'user/profile/setname', json={
        'token': token1,
        'name_first': 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn',
        'name_last': '.,;,/./;,/,.;'
    })

    assert resp.status_code == 400

def test_user_setname_invalid_token_web(url):
    '''Invalid case: token used is invalid'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'jim.roberts1@email.com',
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    resp = requests.put(url + 'user/profile/setname', json={
        'token': 'invalid',
        'name_first': 'ian',
        'name_last': 'jacobs'
    })

    assert resp.status_code == 400
