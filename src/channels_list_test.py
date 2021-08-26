'''
Backend tests for channels_list function
'''

import pytest
import channels
import channel
import auth
from error import AccessError
from other import clear


def test_everything_valid():
    '''Valid case: creates 3 channels, returns channels that authorised user is part of'''
    clear()

    info1 = auth.auth_register("name1@domain.com", "password1", "First", "Last")
    token1 = info1['token']
    u_id1 = info1['u_id']
    info2 = auth.auth_register("name2@domain.com", "password2", "Bob", "Brown")
    token2 = info2['token']
    info3 = auth.auth_register("name3@domain.com", "password3", "John", "Smith")
    token3 = info3['token']
    channel_id1 = channels.channels_create(token1, "Channel A", True)['channel_id']
    channel_id2 = channels.channels_create(token1, "Channel B", True)['channel_id']
    channels.channels_create(token2, "Channel C", True)
    channel_id3 = channels.channels_create(token3, "Channel D", True)['channel_id']
    channel.channel_invite(token3, channel_id3, u_id1)

    assert channels.channels_list(token1)['channels'] == [
        {
            "channel_id": channel_id1,
            "name"      : "Channel A",
        },
        {
            "channel_id": channel_id2,
            "name"      : "Channel B",
        },
        {
            "channel_id": channel_id3,
            "name"      : "Channel D",
        },
    ]

def test_invalid_token():
    '''Invalid case: token is invalid, raises AccessError'''
    clear()

    with pytest.raises(AccessError):
        channels.channels_list("name@domain.com")
