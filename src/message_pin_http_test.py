'''
Frontend tests for message_pin and message_unpin functions
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
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    payload = resp.json()
    token1 = payload['token']
    user_id1 = payload['u_id']

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    channel_id = resp.json()['channel_id']

    resp = requests.post(url + 'message/send', json={
        'token': token1,
        'channel_id': channel_id,
        'message': "Hello, world!"
    })
    message_id = resp.json()["message_id"]

    assert resp.status_code == 200

    resp = requests.post(url + 'auth/register', json={
        'email': 'anothername@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    payload = resp.json()
    token2 = payload['token']
    user_id2 = payload['u_id']

    assert resp.status_code == 200

    return {
        "token1" : token1,
        "user_id1" : user_id1,
        "token2" : token2,
        "user_id2" : user_id2,
        "channel_id" : channel_id,
        "message_id" : message_id,
    }


def test_simple_valid(url):
    '''Valid case: valid pinning and unpinning a message'''
    data = generating_data(url)

    resp = requests.post(url + 'message/pin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200

    resp = requests.post(url + 'message/unpin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200


def test_invalid_token(url):
    '''Invalid case: token is invalid'''
    data = generating_data(url)

    resp = requests.post(url + 'message/pin', json={
        'token': 'someinvalidtoken',
        'message_id': data["message_id"],
    })

    assert resp.status_code == 400

    resp = requests.post(url + 'message/unpin', json={
        'token': 'anotherinvalidtoken',
        'message_id': data["message_id"],
    })

    assert resp.status_code == 400


def test_invalid_message_id(url):
    '''Invalid case: message ID is invalid'''
    data = generating_data(url)

    resp = requests.post(url + 'message/pin', json={
        'token': data["token1"],
        'message_id': 3,
    })

    assert resp.status_code == 400

    resp = requests.post(url + 'message/unpin', json={
        'token': data["token1"],
        'message_id': 3,
    })

    assert resp.status_code == 400

def test_invalid_user_not_in_channel(url):
    '''Invalid case: the authorised user is not in the channel'''
    data = generating_data(url)

    resp = requests.post(url + 'message/pin', json={
        'token': data["token2"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 400

    resp = requests.post(url + 'message/unpin', json={
        'token': data["token2"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 400


def test_invalid_user_not_an_owner(url):
    '''Invalid case: the authorised user is not an owner'''
    data = generating_data(url)

    resp = requests.post(url + 'channel/join', json={
        'token': data["token2"],
        'channel_id': data["channel_id"],
    })

    assert resp.status_code == 200

    resp = requests.post(url + 'message/pin', json={
        'token': data["token2"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 400

    resp = requests.post(url + 'message/unpin', json={
        'token': data["token2"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 400

def test_valid_repeats(url):
    '''Valid case: repeated pinning and unpinning'''
    data = generating_data(url)

    resp = requests.post(url + 'message/pin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200

    resp = requests.post(url + 'message/unpin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200

    resp = requests.post(url + 'message/pin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200

    resp = requests.post(url + 'message/unpin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200


def test_invalid_repeats(url):
    '''Invalid case: attempting to pin a message when it's already pinned'''
    data = generating_data(url)

    resp = requests.post(url + 'message/pin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200

    resp = requests.post(url + 'message/pin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 400

    resp = requests.post(url + 'message/unpin', json={
        'token': data["token1"],
        'message_id': data["message_id"],
    })

    assert resp.status_code == 200
