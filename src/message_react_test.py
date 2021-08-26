'''
Backend tests for message_react and message_unreact functions'''

import pytest
from data import data_messages
from message import message_send, message_react, message_unreact
from auth import auth_register as register
from channels import channels_create
from channel import channel_messages
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
    '''Valid case: valid reacting and unreacting to a message'''
    data = generating_data()

    message_react(data['token_owner'], data['msg_id'], 1)

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['reacts'] == [1]

    message_unreact(data['token_owner'], data['msg_id'], 1)

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['reacts'] == []


def test_invalid_tokens():
    '''Invalid case: invalid tokens used'''
    data = generating_data()
    
    with pytest.raises(AccessError):
        message_react("some_token", data['msg_id'], 1)

    with pytest.raises(AccessError):
        message_unreact("some_token", data['msg_id'], 1)


def test_invalid_message_id():
    '''Invalid case: invalid message ID used'''
    data = generating_data()
    
    with pytest.raises(InputError):
        message_react(data['token_owner'], "some_message_id", 1)

    with pytest.raises(InputError):
        message_unreact(data['token_owner'], "some_message_id", 1)


def test_invalid_react_id():
    '''Invalid case: invalid react ID used'''
    data = generating_data()
    
    with pytest.raises(InputError):
        message_react(data['token_owner'], data['msg_id'], -43)

    with pytest.raises(InputError):
        message_unreact(data['token_owner'], data['msg_id'], -42)


def test_invalid_user_not_in_channel():
    '''Invalid case: the authorised user is not in the channel'''
    data = generating_data()
    
    with pytest.raises(InputError):
        message_react(data['token_member'], data['msg_id'], 1)

    with pytest.raises(InputError):
        message_unreact(data['token_member'], data['msg_id'], 1)


def test_invalid_react_and_unreact_repeats():
    '''Invalid case: reacting to a message when it's already reacted to, etc.'''
    data = generating_data()

    message_react(data['token_owner'], data['msg_id'], 1)

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['reacts'] == [1]

    with pytest.raises(InputError):
        message_react(data['token_owner'], data['msg_id'], 1)

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['reacts'] == [1]

    message_unreact(data['token_owner'], data['msg_id'], 1)

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['reacts'] == []

    with pytest.raises(InputError):
        message_unreact(data['token_owner'], data['msg_id'], 1)

    for message in data_messages[data['ch_id']]:
        if message['message_id'] == data['msg_id']:
            assert message['reacts'] == []
