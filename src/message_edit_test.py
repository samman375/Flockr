'''
Backend tests for message_edit function
'''

import pytest
from message import message_edit, message_send
from error import AccessError
from other import clear
import auth
import channels
import channel

def test_valid():
    '''Valid case: all inputs are valid'''
    clear()

    info = auth.auth_register("name@domain.com", "password123", "First", "Last")
    token = info['token']
    channel_id = channels.channels_create(token, 'channel_name', True)['channel_id']

    message_id = message_send(token, channel_id, 'hello')['message_id']
    assert len(channel.channel_messages(token, channel_id, 1)['messages']) == 1
    assert channel.channel_messages(token, channel_id, 1)['messages'][0]['message'] == 'hello'

    message_edit(token, message_id, 'hi')

    assert len(channel.channel_messages(token, channel_id, 1)['messages']) == 1
    assert channel.channel_messages(token, channel_id, 1)['messages'][0]['message'] == 'hi'

def test_delete_empty():
    '''Valid case: given empty string edited message, test that the message is deleted'''
    clear()

    info = auth.auth_register("name@domain.com", "password123", "First", "Last")
    token = info['token']
    channel_id = channels.channels_create(token, 'channel_name', True)['channel_id']

    message_id1 = message_send(token, channel_id, 'hello')['message_id']
    message_send(token, channel_id, 'how are you?')
    assert len(channel.channel_messages(token, channel_id, 1)['messages']) == 2
    assert channel.channel_messages(token, channel_id, 1)['messages'][0]['message'] == 'hello'

    message_edit(token, message_id1, '')

    assert len(channel.channel_messages(token, channel_id, 1)['messages']) == 1

def test_invalid_token():
    '''Invalid case: trying to edit a message with an invalid token'''
    clear()
    info1 = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token1 = info1['token']

    info2 = auth.auth_register("jon.bob@email.com", "jonbob", "jon", "bob")
    token2 = info2['token']
    user2 = info2['u_id']

    channel_id = channels.channels_create(token1, "name", True)['channel_id']
    channel.channel_invite(token1, channel_id, user2)

    m_id = message_send(token2, channel_id, "0")['message_id']

    with pytest.raises(AccessError):
        message_edit("aaaaaaaaaaaaa", "beans", m_id)

def test_editor_is_not_sender_or_owner():
    '''Invalid case: test that AccessError is raised if user editing message is
    not who sent it or an owner of the channel or flockr'''
    clear()

    info1 = auth.auth_register("john.smith@email.com", "johnny123", "John", "Smith")
    token1 = info1['token']

    info2 = auth.auth_register("kate.brown@email.com", "kateb1", "Kate", "Brown")
    token2 = info2['token']
    u_id2 = info2['u_id']

    info3 = auth.auth_register("bob@email.com", "bobby4", "Bob", "King")
    token3 = info3['token']
    u_id3 = info3['u_id']

    channel_id = channels.channels_create(token1, 'channel_name', True)['channel_id']

    channel.channel_invite(token1, channel_id, u_id2)
    channel.channel_invite(token1, channel_id, u_id3)

    message_id = message_send(token2, channel_id, 'hello')['message_id']

    with pytest.raises(AccessError):
        message_edit(token3, message_id, 'hi')

def test_owner_edit_any_message():
    '''Invalid case: test that the owner can edit any message'''
    clear()

    info1 = auth.auth_register("john.smith@email.com", "johnny123", "John", "Smith")
    token1 = info1['token']

    info2 = auth.auth_register("kate.brown@email.com", "kateb1", "Kate", "Brown")
    token2 = info2['token']
    u_id2 = info2['u_id']

    channel_id = channels.channels_create(token1, 'channel_name', True)['channel_id']
    channel.channel_invite(token1, channel_id, u_id2)

    message_id = message_send(token2, channel_id, 'hello')['message_id']
    assert len(channel.channel_messages(token1, channel_id, 1)['messages']) == 1
    assert channel.channel_messages(token1, channel_id, 1)['messages'][0]['message'] == 'hello'

    message_edit(token1, message_id, 'hi')
    assert len(channel.channel_messages(token1, channel_id, 1)['messages']) == 1
    assert channel.channel_messages(token1, channel_id, 1)['messages'][0]['message'] == 'hi'
