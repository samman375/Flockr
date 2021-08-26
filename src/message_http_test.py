'''
Frontend tests for message_* functions
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import pytest
import requests
import json
from error import AccessError, InputError
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
    payload = resp.json()
    channel_id = payload['channel_id']

    return {
        "token" : token,
        "user_id" : user_id,
        "channel_id" : channel_id,
    }


def test_valid_message_web(url):
    '''Valid case: tests for valid uses of send, remove & edit message functions'''
    requests.delete(url + 'clear')

    info = generating_data(url)

    resp0 = requests.post(url + 'message/send', json={
        'token': info["token"],
        'channel_id': info["channel_id"],
        'message': "1"
    })
    assert resp0.status_code == 200
    payload0 = resp0.json()
    assert payload0["message_id"] == 0

    check_resp0 = requests.get(url + 'channel/messages', params={
        'token' : info["token"],
        'channel_id' : info["channel_id"],
        'start' : 1,
    })
    check_payload0 = json.loads(check_resp0.text)
    assert len(check_payload0["messages"]) == 1
    assert check_payload0["messages"][0]["message"] == "1"
    assert check_payload0["messages"][0]["u_id"] == info["user_id"]

    resp1 = requests.post(url + 'message/send', json={
        'token': info["token"],
        'channel_id': info["channel_id"],
        'message': "2"
    })
    assert resp1.status_code == 200
    assert resp1.json()["message_id"] == 1

    check_resp1 = requests.get(url + 'channel/messages', params={
        'token' : info["token"],
        'channel_id' : info["channel_id"],
        'start' : 1,
    })
    check_payload1 = json.loads(check_resp1.text)
    assert len(check_payload1["messages"]) == 2
    assert check_payload1["messages"][1]["message"] == "2"
    assert check_payload1["messages"][1]["u_id"] == info["user_id"]

    requests.delete(url + 'message/remove', json={
        'token': info["token"],
        'message_id': 0
    })

    check_resp2 = requests.get(url + 'channel/messages', params={
        'token' : info["token"],
        'channel_id' : info["channel_id"],
        'start' : 1,
    })
    assert check_resp2.status_code == 200
    check_payload2 = json.loads(check_resp2.text)
    assert len(check_payload2["messages"]) == 1
    assert check_payload2["messages"][0]["message"] == "2"
    assert check_payload2["messages"][0]["u_id"] == info["user_id"]

    raises_test_resp = requests.put(url + 'message/edit', json={
        'token': info["token"],
        'message_id': resp1.json()["message_id"],
        'message': "5"
    })
    assert raises_test_resp.status_code == 200

    check_resp3 = requests.get(url + 'channel/messages', params={
        'token' : info["token"],
        'channel_id' : info["channel_id"],
        'start' : 1,
    })

    assert check_resp3.status_code == 200
    check_payload3 = json.loads(check_resp3.text)

    assert len(check_payload3["messages"]) == 1
    assert check_payload3["messages"][0]["message"] == "5"
    assert check_payload3["messages"][0]["u_id"] == info["user_id"]

    resp = requests.put(url + 'message/edit', json={
        'token': info["token"],
        'message_id': check_payload3['messages'][0]["message_id"],
        'message': ""
    })
    assert resp.status_code == 200
    check_resp4 = requests.get(url + 'channel/messages', params={
        'token' : info["token"],
        'channel_id' : info["channel_id"],
        'start' : 1,
    })
    assert check_resp4.status_code == 400


def test_message_web_invalid_token(url):
    '''Invalid case: using send, remove & edit message functions with invalid tokens'''
    requests.delete(url + 'clear')
    info = generating_data(url)

    resp = requests.post(url + 'message/send', json={
        'token': info["token"],
        'channel_id': info["channel_id"],
        'message': "1"
    })
    payload = resp.json()

    resp = requests.post(url + 'message/send', json={
        'token': "beans",
        'channel_id': info["channel_id"],
        'message': "2"
    })
    assert resp.status_code == 400

    requests.delete(url + 'message/remove', json={
        'token': "beans",
        'message_id': payload["message_id"]
    })
    assert resp.status_code == 400

    resp = requests.put(url + 'message/edit', json={
        'token': "beans",
        'message_id': payload["message_id"],
        'message': "5"
    })
    assert resp.status_code == 400

def test_message_web_invalid_channel_user(url):
    '''Invalid case: using send, remove & edit message functions with incorrect 
    channel or user not in channel'''
    requests.delete(url + 'clear')
    info = generating_data(url)
    token1 = info["token"]
    user_fe = requests.post(url + 'auth/register', json={
        'email': 'name1@domain.com',
        'password': 'password12345',
        'name_first': 'jon',
        'name_last': 'jon'
    })

    payload2 = user_fe.json()
    token2 = payload2['token']

    requests.post(url + 'message/send', json={
        'token': token1,
        'channel_id': info["channel_id"],
        'message': "1"
    })

    requests.post(url + 'channel/join', json={
        'token': token2,
        'channel_id': info["channel_id"]
    })
    m_id = requests.post(url + 'message/send', json={
        'token': token2,
        'channel_id': info["channel_id"],
        'message': "4"
    })
    message2 = m_id.json()["message_id"]
    requests.post(url + 'channel/leave', json={
        'token': token2,
        'channel_id': info["channel_id"]
    })

    resp = requests.post(url + 'message/send', json={
        'token': token1,
        'channel_id': 42,
        'message': "2"
    })
    assert resp.status_code == 400

    resp = requests.post(url + 'message/send', json={
        'token': token2,
        'channel_id': info["channel_id"],
        'message': "2"
    })
    assert resp.status_code == 400

    resp = requests.delete(url + 'message/remove', json={
        'token': token2,
        'message_id': message2
    })
    assert resp.status_code == 400

    resp = requests.put(url + 'message/edit', json={
        'token': info["token"],
        'message_id': message2,
        'message': "5"
    })
    assert resp.status_code == 200

def test_long(url):
    '''Invalid case: sending a message to a channel that exceeds the character limit'''
    requests.delete(url + 'clear')
    info = generating_data(url)
    long_message = '''
    According to all known laws of aviation, there is no way a bee should be able to
    fly. Its wings are too small to get its fat little body off the ground.The bee, of course,
    flies anyway because bees don't care what humans think is impossible. Yellow, black. Yellow,
    black. Yellow, black. Yellow, black. Ooh, black and yellow! Let's shake it up a little.
    Barry! Breakfast is ready! Ooming! Hang on a second. Hello? - Barry? - Adam? - Oan you
    believe this is happening? - I can't. I'll pick you up. Looking sharp. Use the stairs. Your
    father paid good money for those. Sorry. I'm excited. Here's the graduate. We're very proud
    of you, son. A perfect report card, all B's. Very proud. Ma! I got a thing going here. -
    You got lint on your fuzz. - Ow! That's me! - Wave to us! We'll be in row 118,000. - Bye!
    Barry, I told you, stop flying in the house! - Hey, Adam. - Hey, Barry. - Is that fuzz gel?
    - A little. Special day, graduation. Never thought I'd make it. Three days grade school, three
    days high school. Those were awkward. Three days college. I'm glad I took a day and
    hitchhiked around the hive. You did come back different. - Hi, Barry. - Artie, growing a
    mustache? Looks good. - Hear about Frankie? - Yeah. - You going to the funeral? - No, I'm not
    going. Everybody knows, sting someone, you die. Don't waste it on a squirrel. Such a hothead.
    I guess he could have just gotten out of the way. I love this incorporating an amusement park
    into our day. That's why we don't need vacations. Boy, quite a bit of pomp... under the
    circumstances. - Well, Adam, today we are men. - We are! - Bee-men. - Amen! Hallelujah!
    Students, faculty, distinguished bees, please welcome Dean Buzzwell. Welcome, New Hive Oity
    graduating class of... ...9:15. That concludes our ceremonies. And begins your career at Honex
    Industries! Will we pick our job today? I heard it's just orientation.
    '''
    resp = requests.post(url + 'message/send', json={
        'token': info["token"],
        'channel_id': info["channel_id"],
        'message': long_message
    })
    assert resp.status_code == 400

def test_message_remove_edit(url):
    '''Invalid case: testing various errors in message remove and edit:
        - user not sender
        - message doesn't exist
        - channel owner can remove and edit any message
    '''
    requests.delete(url + 'clear')
    info = generating_data(url)
    token1 = info["token"]
    user_fe = requests.post(url + 'auth/register', json={
        'email': 'name1@domain.com',
        'password': 'password12345',
        'name_first': 'jon',
        'name_last': 'jon'
    })

    payload2 = user_fe.json()
    token2 = payload2['token']

    resp1 = requests.post(url + 'message/send', json={
        'token': token1,
        'channel_id': info["channel_id"],
        'message': "1"
    })
    message1 = resp1.json()['message_id']

    requests.post(url + 'channel/join', json={
        'token': token2,
        'channel_id': info["channel_id"]
    })
    resp2 = requests.post(url + 'message/send', json={
        'token': token2,
        'channel_id': info["channel_id"],
        'message': "4"
    })
    message2 = resp2.json()["message_id"]

    # Try to edit and remove someone elses message
    resp = requests.put(url + 'message/edit', json={
        'token': token2,
        'message_id': message1,
        'message': "5"
    })
    assert resp.status_code == 400

    resp = requests.delete(url + 'message/remove', json={
        'token': token2,
        'message_id': message1
    })
    assert resp.status_code == 400

    # Try to remove message with invalid ID
    resp = requests.put(url + 'message/edit', json={
        'token': token1,
        'message_id': 52,
        'message': "5"
    })
    assert resp.status_code == 400

    resp = requests.delete(url + 'message/remove', json={
        'token': token1,
        'message_id': 54
    })
    assert resp.status_code == 400

    # Owner sucessfully edits and then removes someone elses message
    resp = requests.put(url + 'message/edit', json={
        'token': token1,
        'message_id': message2,
        'message': "5"
    })
    
    assert resp.status_code == 200

    resp = requests.delete(url + 'message/remove', json={
        'token': token1,
        'message_id': message2
    })
    assert resp.status_code == 200
