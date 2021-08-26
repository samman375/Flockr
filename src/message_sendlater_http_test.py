'''
Tests for the message/sendlater function
'''

import json
import re
import time
import datetime
from datetime import datetime, timedelta, timezone
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

    resp = requests.post(url + 'auth/register', json={
        'email': 'anothername@domain.com',
        'password': 'password',
        'name_first': 'First',
        'name_last': 'Last'
    })
    payload = resp.json()
    token2 = payload['token']
    user_id2 = payload['u_id']

    resp = requests.post(url + 'channels/create', json={
        'token': token1,
        'name': 'Channel A',
        'is_public': True
    })
    channel_id = resp.json()['channel_id']

    return {
        "token1" : token1,
        "user_id1" : user_id1,
        "token2" : token2,
        "user_id2" : user_id2,
        "channel_id" : channel_id,
    }


def test_simple_valid(url):
    '''Valid case: sending a message set for 5 seconds later'''
    data = generating_data(url)

    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 400

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()
    
    resp = requests.post(url + 'message/sendlater', json={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'message': "Hello, world!",
        'time_sent': timestamp
    })

    assert resp.status_code == 200
    assert resp.json()['message_id'] == 0

    while datetime.now() < send_time:
        time.sleep(1)
    
    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 200
    payload = json.loads(resp.text)
    assert len(payload['messages']) == 1


def test_invalid_time(url):
    '''Invalid case: trying to send at a time in the past'''
    data = generating_data(url)

    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 400

    send_time = datetime.now() - timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()
    
    resp = requests.post(url + 'message/sendlater', json={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'message': "Hello, world!",
        'time_sent': timestamp
    })

    assert resp.status_code == 400

    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 400


def test_invalid_channel_id(url):
    '''Invalid case: invalid channel ID'''
    data = generating_data(url)

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()

    resp = requests.post(url + 'message/sendlater', json={
        'token': data["token1"],
        'channel_id': "some_invalid_id",
        'message': "Hello, world!",
        'time_sent': timestamp
    })

    assert resp.status_code == 400

def test_invalid_user_not_in_channel(url):
    '''Invalid case: user is not a member of the channel they're trying to post to'''
    data = generating_data(url)

    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 400

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()
    
    resp = requests.post(url + 'message/sendlater', json={
        'token': data["token2"],
        'channel_id': data["channel_id"],
        'message': "Hello, world!",
        'time_sent': timestamp
    })

    assert resp.status_code == 400

    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 400

def test_invalid_message_length(url):
    '''Invalid case: the message exceeds the 1000 character limit'''
    data = generating_data(url)

    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 400

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()
    
    resp = requests.post(url + 'message/sendlater', json={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'message': """Did you ever hear the tragedy of Darth Plagueis The Wise? I thought not.
        It’s not a story the Jedi would tell you. It’s a Sith legend. Darth Plagueis
        was a Dark Lord of the Sith, so powerful and so wise he could use the Force to
        influence the midichlorians to create life… He had such a knowledge of the dark
        side that he could even keep the ones he cared about from dying. The dark side
        of the Force is a pathway to many abilities some consider to be unnatural. He
        became so powerful… the only thing he was afraid of was losing his power, which
        eventually, of course, he did. Unfortunately, he taught his apprentice everything
        he knew, then his apprentice killed him in his sleep. Ironic. He could save others
        from death, but not himself.
        Did you ever hear the tragedy of Darth Plagueis The Wise? I thought not.
        It’s not a story the Jedi would tell you. It’s a Sith legend. Darth Plagueis
        was a Dark Lord of the Sith, so powerful and so wise he could use the Force to
        influence the midichlorians to create life…""",
        'time_sent': timestamp
    })

    assert resp.status_code == 400

    resp = requests.get(url + 'channel/messages', params={
        'token': data["token1"],
        'channel_id': data["channel_id"],
        'start': 1
    })
    assert resp.status_code == 400
