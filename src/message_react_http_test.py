'''
Frontend tests for message_react and message_unreact functions
'''

import json
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

def generating_data(url):
    '''GENERATING DATA USED IN EACH TEST-CASE'''

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password123',
        'name_first': 'First',
        'name_last': 'Last'
    })

    payload = resp.json()
    token = payload['token']
    user_id = payload['u_id']

    resp = requests.post(url + 'channels/create', json={
        'token': token,
        'name': 'Channel A',
        'is_public': True
    })
    channel_id = resp.json()['channel_id']

    resp0 = requests.post(url + 'message/send', json={
        'token': token,
        'channel_id': channel_id,
        'message': "1"
    })
    message_id = resp0.json()["message_id"]

    return {
        "token" : token,
        "user_id" : user_id,
        "channel_id" : channel_id,
        "message_id" : message_id,
    }


def test_valid(url):
    '''Valid case: valid uses of react and unreact'''
    requests.delete(url + 'clear')

    info = generating_data(url)

    react = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })

    assert react.status_code == 200

    unreact = requests.post(url + 'message/unreact', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })

    assert unreact.status_code == 200

def test_invalid_token(url):
    '''Invalid case: invalid token used'''
    requests.delete(url + 'clear')

    info = generating_data(url)

    react0 = requests.post(url + 'message/react', json={
        'token': "abcd",
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert react0.status_code == 400

    react1 = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert react1.status_code == 200

    unreact0 = requests.post(url + 'message/unreact', json={
        'token': "abcd",
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert unreact0.status_code == 400

def test_invalid_message(url):
    '''Invalid case: invalid message IDs used'''
    requests.delete(url + 'clear')

    info = generating_data(url)

    react0 = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': 123,
        'react_id': 1
    })
    assert react0.status_code == 400

    react1 = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert react1.status_code == 200

    unreact0 = requests.post(url + 'message/unreact', json={
        'token': info["token"],
        'message_id': 234,
        'react_id': 1
    })
    assert unreact0.status_code == 400

def test_invalid_react_id(url):
    '''Valid case: invalid react IDs used'''
    requests.delete(url + 'clear')

    info = generating_data(url)

    react0 = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 4
    })
    assert react0.status_code == 400

    react1 = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert react1.status_code == 200

    unreact0 = requests.post(url + 'message/unreact', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 4
    })
    assert unreact0.status_code == 400

def test_already_reacted(url):
    '''Invalid case: tests for reacting to a message more than once and
    unreacting to a messagethat doesn't have a react'''
    requests.delete(url + 'clear')

    info = generating_data(url)

    react0 = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert react0.status_code == 200

    react1 = requests.post(url + 'message/react', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert react1.status_code == 400

    unreact0 = requests.post(url + 'message/unreact', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert unreact0.status_code == 200

    unreact1 = requests.post(url + 'message/unreact', json={
        'token': info["token"],
        'message_id': info["message_id"],
        'react_id': 1
    })
    assert unreact1.status_code == 400

def test_user_unauthorised(url):
    '''Invalid case: user not in the channel attempts to react and unreact to a message'''
    requests.delete(url + 'clear')

    info = generating_data(url)

    resp_new_user = requests.post(url + 'auth/register', json={
        'email': 'heeby.jeeby@domain.com',
        'password': 'gottheheebyjeebies123',
        'name_first': 'Heeby',
        'name_last': 'Jeeby'
    })
    token1 = resp_new_user.json()['token']

    react = requests.post(url + 'message/react', json={
        'token': token1,
        'message_id': info["message_id"],
        'react_id': 1
    })

    assert react.status_code == 400

    requests.post(url + 'channel/join', json={
        'token': token1,
        'channel_id': info["channel_id"]
    })

    react = requests.post(url + 'message/react', json={
        'token': token1,
        'message_id': info["message_id"],
        'react_id': 1
    })

    assert react.status_code == 200

    requests.post(url + 'channel/leave', json={
        'token': token1,
        'channel_id': info["channel_id"]
    })

    unreact = requests.post(url + 'message/unreact', json={
        'token': token1,
        'message_id': info["message_id"],
        'react_id': 1
    })

    assert unreact.status_code == 400
