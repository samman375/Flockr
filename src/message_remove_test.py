'''
Backend tests for message_remove function
'''

import pytest
import channel
import channels
import auth
from message import message_send, message_remove
from error import AccessError, InputError
from other import clear

def generating_data():
    '''GENERATING DATA USED IN EACH TEST-CASE'''

    info1 = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token1 = info1['token']
    user1 = info1['u_id']

    info2 = auth.auth_register("jon.bob@email.com", "jonbob", "jon", "bob")
    token2 = info2['token']
    user2 = info2['u_id']

    return {
        'token1' : token1,
        'user1'  : user1,
        'token2' : token2,
        'user2'  : user2,
    }

def test_valid_own_remove():
    '''Valid case: all inputs valid, everything works'''
    clear()
    info = generating_data()

    token1 = info['token1']
    token2 = info['token2']
    user2 = info['user2']

    channel_id = channels.channels_create(token1, "name", True)['channel_id']
    channel.channel_invite(token1, channel_id, user2)

    m_id0 = message_send(token1, channel_id, "0")['message_id']
    m_id1 = message_send(token2, channel_id, "1")['message_id']
    message_send(token1, channel_id, "2")

    assert len(channel.channel_messages(token1, channel_id, 1)["messages"]) == 3

    message_remove(token1, m_id0)

    assert len(channel.channel_messages(token1, channel_id, 1)["messages"]) == 2
    assert channel.channel_messages(token1, channel_id, 1)["messages"][0]["message"] == "1"

    message_remove(token2, m_id1)

    assert len(channel.channel_messages(token1, channel_id, 1)["messages"]) == 1
    assert channel.channel_messages(token1, channel_id, 1)["messages"][0]["message"] == "2"


def test_valid_owner_remove():
    '''Valid case: the channel owner removes someone elses message'''
    clear()
    info = generating_data()

    token1 = info['token1']
    token2 = info['token2']
    user2 = info['user2']

    channel_id = channels.channels_create(token1, "name", True)['channel_id']
    channel.channel_invite(token1, channel_id, user2)

    m_id0 = message_send(token2, channel_id, "0")['message_id']
    m_id1 = message_send(token2, channel_id, "1")['message_id']
    message_send(token2, channel_id, "2")

    assert len(channel.channel_messages(token1, channel_id, 1)["messages"]) == 3

    message_remove(token1, m_id1)

    assert len(channel.channel_messages(token1, channel_id, 1)["messages"]) == 2
    assert channel.channel_messages(token1, channel_id, 1)["messages"][0]["message"] == "0"

    message_remove(token1, m_id0)

    assert len(channel.channel_messages(token1, channel_id, 1)["messages"]) == 1
    assert channel.channel_messages(token1, channel_id, 1)["messages"][0]["message"] == "2"

def test_invalid_token():
    '''Invalid case: trying to remove a message with an invalid token'''
    clear()
    info = generating_data()

    token1 = info['token1']
    token2 = info['token2']
    user2 = info['user2']

    channel_id = channels.channels_create(token1, "name", True)['channel_id']
    channel.channel_invite(token1, channel_id, user2)

    m_id = message_send(token2, channel_id, "0")['message_id']

    with pytest.raises(AccessError):
        message_remove("aaaaaaaaaaaaa", m_id)

def test_invalid_message():
    '''Try to remove a message which doesn't exist'''
    clear()

    info1 = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token1 = info1['token']

    with pytest.raises(InputError):
        message_remove(token1, 4)

def test_not_in_channel():
    '''Invalid case: trying to remove a message in another channel'''
    clear()

    info1 = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token1 = info1['token']

    info2 = auth.auth_register("jon.bob@email.com", "jonbob", "jon", "bob")
    token2 = info2['token']
    user2 = info2['u_id']

    channel_id = channels.channels_create(token1, "name", True)['channel_id']
    channel.channel_invite(token1, channel_id, user2)

    m_id0 = message_send(token2, channel_id, "0")['message_id']

    channel.channel_leave(token2, channel_id)

    with pytest.raises(AccessError):
        message_remove(token2, m_id0)

def test_wrong_user():
    '''Invalid case: trying to remove a message sent by another user'''
    clear()
    info = generating_data()

    token1 = info['token1']
    token2 = info['token2']
    user2 = info['user2']

    channel_id = channels.channels_create(token1, "name", True)['channel_id']
    channel.channel_invite(token1, channel_id, user2)

    m_id0 = message_send(token1, channel_id, "0")['message_id']

    with pytest.raises(AccessError):
        message_remove(token2, m_id0)
