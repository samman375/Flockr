'''
Frontend tests for auth_login function
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import pytest
import requests
import jwt

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

def test_valid_auth_login_web(url):
    '''Valid case: simple test for valid auth_login frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    payload = resp.json()
    token = payload['token']
    requests.post(url + 'auth/logout', json={
        'token': token
    })
    resp = requests.post(url + 'auth/login', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere'
    })
    assert resp.status_code == 200
    payload = resp.json()
    token = payload['token']
    validated_token = jwt.decode(token.encode('utf-8'), 'beans_123', algorithms=['HS256'])
    assert payload['u_id'] == 0
    assert validated_token['user_id'] == 0

def test_auth_login_web_invalid_email_1(url):
    '''Invalid case: invalid email for auth_login frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    payload = resp.json()
    token = payload['token']
    requests.post(url + 'auth/logout', json={
        'token': token
    })
    resp = requests.post(url + 'auth/login', json={
        'email': 'john@gmail.com',
        'password': 'hellothere'
    })

    assert resp.status_code == 400

def test_auth_login_web_invalid_email_2(url):
    '''Invalid case: email is already logged-in'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    resp = requests.post(url + 'auth/login', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere'
    })

    assert resp.status_code == 400

def test_auth_login_web_invalid_password(url):
    '''
    Test for invalid password for auth_login frontend
    Assumes working auth_register, auth_logout
    '''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    payload = resp.json()
    token = payload['token']
    requests.post(url + 'auth/logout', json={
        'token': token
    })
    resp = requests.post(url + 'auth/login', json={
        'email': 'bob@gmail.com',
        'password': 'incorrect'
    })

    assert resp.status_code == 400
