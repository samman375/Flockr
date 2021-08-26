'''
Backend tests for channels_listall function
'''

import pytest
import channels
import auth
from error import AccessError
from other import clear


def test_valid_token():
    '''Valid case: valid use of channels_listall, all inputs valid'''
    clear()
    info = auth.auth_register('name1@domain.com', 'password1', 'First', 'Last')
    token1 = info['token']
    info = auth.auth_register('name2@domain.com', 'password2', 'Bob', 'Smith')
    token2 = info['token']
    channel_id1 = channels.channels_create(token1, "Channel A", True)['channel_id']
    channel_id2 = channels.channels_create(token2, "Channel B", True)['channel_id']
    assert channels.channels_listall(token1)['channels'] == [
        {
            "channel_id": channel_id1,
            "name"      : "Channel A",
        },
        {
            "channel_id": channel_id2,
            "name"      : "Channel B",
        },
    ]

def test_invalid_token():
    '''Invalid case: raises access error since the token is invalid'''
    clear()
    with pytest.raises(AccessError):
        channels.channels_listall("name@domain.com")
