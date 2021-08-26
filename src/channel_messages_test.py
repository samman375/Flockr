'''
Backend tests for channel_messages
'''

import pytest
import channel
from channels import channels_create
from auth import auth_register
from error import AccessError, InputError
from other import clear
from data import data_messages


def test_channel_no_messages_valid():
    '''Valid case: getting messages from a channel with none returns an empty list'''
    clear()

    # User registered and added to new channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    data_messages[ch_id0] = []

    # Should succeed as channel_id and start are valid, and user is member of channel
    # Returns -1 as end as no messages sent
    assert len(channel.channel_messages(us_token0, ch_id0, 0)['messages']) == 0
    assert channel.channel_messages(us_token0, ch_id0, 0)['start'] == 0
    assert channel.channel_messages(us_token0, ch_id0, 0)['end'] == -1

def test_channel_messages_valid1():
    '''Valid case: all inputs valid, user is a member of the channel, 'end' == -1'''
    clear()

    # User registered and added to new channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    data_messages[ch_id0] = []

    i = 0
    while i < 70:
        data_messages[ch_id0].append(
            {
                'message_id': i,
                'u_id': us_id0,
                'message': 'Hello world',
                'time_created': i,
            },
        )

        i += 1

    mess_data_0 = channel.channel_messages(us_token0, ch_id0, 5)

    assert len(mess_data_0['messages']) == 50
    assert mess_data_0['start'] == 5
    assert mess_data_0['end'] == 55

    mess_data_0 = channel.channel_messages(us_token0, ch_id0, 51)

    assert len(mess_data_0['messages']) == 20
    assert mess_data_0['start'] == 51
    assert mess_data_0['end'] == -1

def test_channel_messages_invalid_ch():
    '''Invalid case: trying to get messages from a channel the user is not in or doesn't exist'''
    clear()

    # User registerd but not channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    # Invalid channel_id, should fail
    with pytest.raises(InputError):
        channel.channel_messages(us_token0, 12, 4)

def test_channel_messages_invalid_start():
    '''Invalid case: invalid 'start' is larger than number of messages in the channel'''
    clear()

    # User and channel both registered
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    data_messages[ch_id0] = [
        {
            'message_id': 0,
            'u_id': us_id0,
            'message': 'Hello world',
            'time_created': 1,
        },
        {
            'message_id': 1,
            'u_id': us_id0,
            'message': 'My name is Jim',
            'time_created': 2,
        },
        {
            'message_id': 2,
            'u_id': us_id0,
            'message': 'I like cheese',
            'time_created': 3,
        },
        {
            'message_id': 3,
            'u_id': us_id0,
            'message': '12345',
            'time_created': 4,
        },
    ]

    with pytest.raises(InputError):
        channel.channel_messages(us_token0, ch_id0, 5)

def test_channel_messages_invalid_access():
    '''Invalid case: user who is not in the channel tries to access the messages'''
    clear()

    # Users and channel created but user requesting access not in channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    # user_id not in channel, should fail
    with pytest.raises(AccessError):
        channel.channel_messages(us_token1, ch_id0, 0)

def test_invalid_token():
    '''Invalid case: raises an access error if the token is invalid'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    data_messages[ch_id0] = []

    with pytest.raises(AccessError):
        channel.channel_messages('invalid', ch_id0, 0)
