'''
Frontend tests for user_profile_setemail function
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


def test_user_setemail_valid_web(url):
    '''Valid case: email uses valid structure'''
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

    resp = requests.put(url + 'user/profile/setemail', json={
        'token': token1,
        'email': 'domain@name.com'
    })
    assert resp.status_code == 200

    resp = requests.get(url + 'user/profile', params={
        'token': token1,
        'u_id': u_id1
    })

    payload = json.loads(resp.text)

    assert payload['user']['email'] == 'domain@name.com'

def test_user_setemail_invalid_web(url):
    '''Invalid case: email uses invalid structure'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'jim.roberts1@email.com',
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    payload = resp.json()
    token1 = payload['token']

    resp = requests.put(url + 'user/profile/setemail', json={
        'token': token1,
        'email': 'v4/1d.NAME'
    })

    assert resp.status_code == 400

def test_user_setemail_already_used_web(url):
    '''Invalid case: email is already being used by another user'''
    clear()

    resp = requests.post(url + 'auth/register', json={
        'email': 'jim.roberts1@email.com',
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    resp = requests.post(url + 'auth/register', json={
        'email': 'jim.roberts2@email.com',
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    payload = resp.json()
    token1 = payload['token']

    resp = requests.put(url + 'user/profile/setemail', json={
        'token': token1,
        'email': 'jim.roberts1@email.com'
    })

    assert resp.status_code == 400
