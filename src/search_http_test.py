'''
Frontend tests for search
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import pytest
import requests
import json

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
    data = {}
    resp = requests.post(url + 'auth/register', json={
        'email': 'name@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    assert resp.status_code == 200
    owner = resp.json()
    data['owner_token'] = owner['token']
    data['owner_id'] = owner['u_id']

    resp = requests.post(url + 'auth/register', json={
        'email': 'anothername@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    assert resp.status_code == 200
    user = resp.json()
    data['user_token'] = user['token']
    data['user_id'] = user['u_id']

    resp = requests.post(url + 'channels/create', json={
        'token': data['owner_token'],
        'name': 'Channel1',
        'is_public': True
    })
    assert resp.status_code == 200
    channel1 = resp.json()
    data['ch_id_public'] = channel1['channel_id']
    resp = requests.post(url + 'channel/join', json={
        'token': data['user_token'],
        'channel_id': data['ch_id_public']
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'channels/create', json={
        'token': data['user_token'],
        'name': 'Channel2',
        'is_public': False
    })
    assert resp.status_code == 200
    channel2 = resp.json()
    data['ch_id_private'] = channel2['channel_id']

    return data


# VALID TOKEN

def test_search_valid_token_web(url):
    '''Valid case: valid token'''
    data = generating_data(url)
    resp = requests.get(url + 'search', params={
        'token': data['owner_token'],
        'query_str': 'Hello, world!'
    })
    payload = json.loads(resp.text)
    assert payload['messages'] == []
    assert resp.status_code == 200

def test_search_invalid_token_web(url):
    '''Invalid case: token not currently valid'''
    requests.delete(url + 'clear')
    resp = requests.get(url + 'search', params={
        'token': 'some_invalid_token',
        'query_str': 'Hello, world!'
    })
    assert resp.status_code == 400


# THE FOLLOWING TESTS INCLUDE:
# - Multiple channels to search, one public and one private
# - Messages can have unique capitalisation from the query string
# - The query string can be contained within messages

def test_search_complex_valid_owner_web(url):
    '''Valid case: valid complex search with correctly returned data, user is owner'''
    data = generating_data(url)

    resp = requests.post(url + 'message/send', json={
        'token': data['owner_token'],
        'channel_id': data['ch_id_public'],
        'message': 'HELLo!'
    })
    payload = resp.json()
    msg_id1 = payload['message_id']

    requests.post(url + 'message/send', json={
        'token': data['owner_token'],
        'channel_id': data['ch_id_public'],
        'message': 'HEY THERE'
    })

    resp = requests.post(url + 'message/send', json={
        'token': data['user_token'],
        'channel_id': data['ch_id_public'],
        'message': 'So uhh... hello, world!'
    })
    payload = resp.json()
    msg_id2 = payload['message_id']

    requests.post(url + 'message/send', json={
        'token': data['owner_token'],
        'channel_id': data['ch_id_private'],
        'message': 'Hello'
    })

    resp = requests.post(url + 'message/send', json={
        'token': data['user_token'],
        'channel_id': data['ch_id_public'],
        'message': 'HeLlO tHeRe'
    })
    payload = resp.json()
    msg_id3 = payload['message_id']

    resp = requests.get(url + 'search', params={
        'token': data['owner_token'],
        'query_str': 'Hello'
    })
    assert resp.status_code == 200

    returned_data = resp.json()
    messages = returned_data['messages']

    assert messages[0]['message'] == 'HELLo!'
    assert messages[0]['message_id'] == msg_id1
    assert messages[1]['message'] == 'So uhh... hello, world!'
    assert messages[1]['message_id'] == msg_id2
    assert messages[2]['message'] == 'HeLlO tHeRe'
    assert messages[2]['message_id'] == msg_id3


def test_search_complex_valid_member_web(url):
    '''Valid case: valid complex search with correctly returned data, user is not owner'''
    data = generating_data(url)

    resp = requests.post(url + 'message/send', json={
        'token': data['owner_token'],
        'channel_id': data['ch_id_public'],
        'message': 'Welll... uhhh... HELLo!'
    })
    payload = resp.json()
    msg_id1 = payload['message_id']

    requests.post(url + 'message/send', json={
        'token': data['user_token'],
        'channel_id': data['ch_id_private'],
        'message': 'H-E-L-L-O!'
    })

    resp = requests.post(url + 'message/send', json={
        'token': data['user_token'],
        'channel_id': data['ch_id_private'],
        'message': 'Hello'
    })
    payload = resp.json()
    msg_id2 = payload['message_id']

    resp = requests.get(url + 'search', params={
        'token': data['user_token'],
        'query_str': 'Hello'
    })
    assert resp.status_code == 200

    returned_data = json.loads(resp.text)
    messages = returned_data['messages']

    assert messages[0]['message'] == 'Welll... uhhh... HELLo!'
    assert messages[0]['message_id'] == msg_id1
    assert messages[1]['message'] == 'Hello'
    assert messages[1]['message_id'] == msg_id2
