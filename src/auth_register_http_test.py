'''
Frontend tests for auth_register function
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
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

def test_valid_auth_register_web(url):
    '''Valid case: simple test for valid auth_register frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    payload = resp.json()
    assert resp.status_code == 200
    token = payload['token']
    validated_token = jwt.decode(token.encode('utf-8'), 'beans_123', algorithms=['HS256'])
    assert payload['u_id'] == 0
    assert validated_token['user_id'] == 0

def test_auth_register_web_invalid_email_1(url):
    '''Invalid case: invalid email in auth_register frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'b',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    assert resp.status_code == 400

def test_auth_register_web_invalid_email_2(url):
    '''Invalid case: duplicate email used in auth_register frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    assert resp.status_code == 400

def test_auth_register_web_invalid_password(url):
    '''Invalid case: invalid password used in auth_register frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'passw',
        'name_first': 'Bob',
        'name_last': 'Jefferson'
    })
    assert resp.status_code == 400

def test_auth_register_web_invalid_name_first(url):
    '''Invalid case: invalid name_first used in auth_register frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': '',
        'name_last': 'Jefferson'
    })
    assert resp.status_code == 400

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': '134134',
        'name_last': 'Jefferson'
    })
    assert resp.status_code == 400

def test_auth_register_web_invalid_name_last(url):
    '''Invalid case: invalid name_first used in auth_register frontend'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob',
        'name_last': ''
    })
    assert resp.status_code == 400

    resp = requests.post(url + 'auth/register', json={
        'email': 'bob@gmail.com',
        'password': 'hellothere',
        'name_first': 'Bob4',
        'name_last': '134124'
    })
    assert resp.status_code == 400
