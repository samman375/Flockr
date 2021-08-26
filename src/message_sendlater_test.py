'''
Backend tests for message_sendlater function
'''

import time
import datetime
import pytest
import threading
from datetime import datetime, timedelta, timezone
from data import data_messages
from message import message_sendlater
from auth import auth_register as register
from channels import channels_create
from channel import channel_messages, channel_join
from error import InputError, AccessError
from other import clear


def generating_data():
    '''GENERATING DATA USED IN EACH TEST-CASE'''
    clear()
    test_data = {}

    flockr_owner = register('owner@domain.com', 'password', 'First', 'Last')
    test_data['token_owner'] = flockr_owner['token']
    test_data['id_owner'] = flockr_owner['u_id']

    member = register('member@domain.com', 'password', 'First', 'Last')
    test_data['token_member'] = member['token']
    test_data['id_member'] = member['u_id']

    test_data['ch_id'] = channels_create(test_data['token_owner'], 'Channel1', True)['channel_id']

    return test_data


def test_valid_single_msg():
    '''Valid case: sending a message set for 5 seconds in the future'''
    data = generating_data()

    with pytest.raises(InputError):
        channel_messages(data['token_owner'], data['ch_id'], 1)

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()

    message_str = "Hello, world!"
    t = threading.Thread(target=message_sendlater, args=(data['token_owner'], data['ch_id'], message_str, timestamp))
    t.start()

    msg_data = channel_messages(data['token_owner'], data['ch_id'], 1)
    assert len(msg_data['messages']) == 0

    time.sleep(2)
    while datetime.now() < send_time:
        time.sleep(1)

    msg_data = channel_messages(data['token_owner'], data['ch_id'], 1)
    assert len(msg_data['messages']) == 1
    for message in msg_data['messages']:
        if message['message_id'] == 0:
            assert message['time_created'] >= timestamp
            assert message['message'] == message_str

def test_invalid_channel_id():
    '''Invalid case: invalid channel ID used'''
    data = generating_data()

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(InputError):
        message_sendlater(data['token_owner'], 'some_invalid_ID', "Hello, world!", timestamp)['message_id']

    with pytest.raises(InputError):
        channel_messages(data['token_owner'], data['ch_id'], 1)


def test_invalid_time():
    '''Invalid case: the specificed send time is in the past'''
    data = generating_data()

    send_time = datetime.now() - timedelta(seconds=60)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(InputError):
        message_sendlater(data['token_owner'], data['ch_id'], "Hello, world!", timestamp)['message_id']

    with pytest.raises(InputError):
        channel_messages(data['token_owner'], data['ch_id'], 1)


def test_invalid_message_length():
    '''Invalid case: the message exceeds the 1000 character limit'''
    data = generating_data()

    long_message = """Did you ever hear the tragedy of Darth Plagueis The Wise? I thought not.
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
        influence the midichlorians to create life…"""

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(InputError):
        message_sendlater(data['token_owner'], data['ch_id'], long_message, timestamp)['message_id']

    with pytest.raises(InputError):
        channel_messages(data['token_owner'], data['ch_id'], 1)


def test_invalid_user_is_not_member_of_channel():
    '''Invalid case: user is not a member of the channel'''
    data = generating_data()

    send_time = datetime.now() + timedelta(seconds=5)
    timestamp = send_time.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(AccessError):
        message_sendlater(data['token_member'], data['ch_id'], "Hello, world!", timestamp)['message_id']

    with pytest.raises(InputError):
        channel_messages(data['token_owner'], data['ch_id'], 1)
