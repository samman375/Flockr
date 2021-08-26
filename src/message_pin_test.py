'''
Backend tests for message_pin and message_unpin functions
'''

import pytest
from data import data_messages
from message import message_send, message_pin, message_unpin
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

    test_data['msg_id'] = message_send(test_data['token_owner'], test_data['ch_id'], "Hello, world!")['message_id']

    assert len(channel_messages(test_data['token_owner'], test_data['ch_id'], 1)['messages']) == 1

    return test_data


def test_valid_repeated_react_and_unreact():
    '''Valid case: valid pinning and pinning of a message'''
    data = generating_data()

    message_pin(data['token_owner'], data['msg_id'])

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['is_pinned'] == True

    message_unpin(data['token_owner'], data['msg_id'])

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['is_pinned'] == False


def test_invalid_tokens():
    '''Invalid case: invalid tokens used'''
    data = generating_data()
    
    with pytest.raises(AccessError):
        message_pin("some_token", data['msg_id'])

    with pytest.raises(AccessError):
        message_unpin("some_token", data['msg_id'])


def test_invalid_message_id():
    '''Invalid case: invalid message ID used'''
    data = generating_data()
    
    with pytest.raises(InputError):
        message_pin(data['token_owner'], "some_message_id")

    with pytest.raises(InputError):
        message_unpin(data['token_owner'], "some_message_id")


def test_invalid_user_not_in_channel():
    '''Invalid case: the user is not in the channel'''
    data = generating_data()
    
    with pytest.raises(AccessError):
        message_pin(data['token_member'], data['msg_id'])

    with pytest.raises(AccessError):
        message_unpin(data['token_member'], data['msg_id'])


def test_invalid_user_is_not_owner():
    '''Invalid case: the user is in the channel, but is not an owner'''
    data = generating_data()
    
    channel_join(data['token_member'], data['ch_id'])
    
    with pytest.raises(AccessError):
        message_pin(data['token_member'], data['msg_id'])

    with pytest.raises(AccessError):
        message_unpin(data['token_member'], data['msg_id'])


def test_invalid_pin_and_unpin_repeats():
    '''Invalid case: pinning a message when it's already pinned, etc.'''
    data = generating_data()

    message_pin(data['token_owner'], data['msg_id'])

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['is_pinned'] == True

    with pytest.raises(InputError):
        message_pin(data['token_owner'], data['msg_id'])

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['is_pinned'] == True

    message_unpin(data['token_owner'], data['msg_id'])

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['is_pinned'] == False

    with pytest.raises(InputError):
        message_unpin(data['token_owner'], data['msg_id'])

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['is_pinned'] == False
