'''
Frontend tests for auth_passwordreset_request function
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import pytest
import requests

TEST_EMAIL = "cs1531flasktest@gmail.com"

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

def test_auth_passwordreset_request_valid_web(url):
    '''Valid case: User correctly registered, valid inputs supplied (email sent is tested manually)'''
    requests.delete(url + 'clear')

    requests.post(url + 'auth/register', json={
        'email': TEST_EMAIL,
        'password': 'jimroberts',
        'name_first': 'jim',
        'name_last': 'roberts'
    })

    resp = requests.post(url + 'auth/passwordreset/request', json={
        'email': TEST_EMAIL
    })

    assert resp.status_code == 200

def test_auth_passwordreset_request_invalid_email_web_1(url):
    '''Invalid case: user is not registered'''
    requests.delete(url + 'clear')

    resp = requests.post(url + 'auth/passwordreset/request', json={
        'email': TEST_EMAIL
    })

    assert resp.status_code == 400
