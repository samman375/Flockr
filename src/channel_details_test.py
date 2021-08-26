'''
Backend tests for channel_details function
'''

import pytest
import channel
from channels import channels_create
from auth import auth_register
from error import AccessError, InputError
from other import clear

def test_channel_details_valid():
    '''Valid case: simple valid use case of channel_details, all inputs valid'''
    clear()

    # Owner and second user registered and added to new channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    channel.channel_invite(us_token0, ch_id0, us_id1)

    # Should succeed as both users and channel are valid
    assert channel.channel_details(us_token0, ch_id0)['name'] == "channel_name0"

    assert channel.channel_details(us_token0, ch_id0)['owner_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'}
    ]

    assert channel.channel_details(us_token0, ch_id0)['all_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]

def test_channel_details_invalid_ch():
    '''Invalid case: users created but not channel, so channel ID is invalid'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    with pytest.raises(InputError):
        channel.channel_details(us_token0, 2)

def test_channel_details_invalid_access():
    '''Invalid case: user requesting access is not in the channel'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(AccessError):
        # User not member of channel, should fail
        channel.channel_details(us_token1, ch_id0)

def test_invalid_token():
    '''Invalid case: token is invalid'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(AccessError):
        channel.channel_details('invalid', ch_id0)
