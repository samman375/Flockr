'''
Backend tests for channel_invite
'''

import pytest
from channel import channel_invite, channel_details
from auth import auth_register
from channels import channels_create
import error
from other import clear

def test_valid_owner():
    '''Valid case: create a channel, user and token using channels, Owner of flockr invited'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token1, "channel_name0", True)['channel_id']

    assert channel_details(us_token1, ch_id0)['all_members'] == [
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs',}
    ]

    channel_invite(us_token1, ch_id0, us_id0)

    assert channel_details(us_token1, ch_id0)['all_members'] == [
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'},
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
    ]

def test_channel_id_1():
    '''Invalid case: inviting user to a channel that doesn't exist'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    with pytest.raises(error.InputError):
        channel_invite(us_token0, "invalid", us_id1)

def test_user_not_in():
    '''Invalid case: a user not in the channel tries to invite into it'''
    clear()
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']

    us_dic2 = auth_register("steven.jobbs3@email.com", "stevenjobbs", "steven", "jobbs")
    us_id2 = us_dic2['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    with pytest.raises(error.AccessError):
        channel_invite(us_token1, ch_id0, us_id2)

def test_private():
    '''Invalid case: trying to add user to a private channel'''
    clear()
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']
    ch_id0 = channels_create(us_token0, "channel_name0", False)['channel_id']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']
    with pytest.raises(error.AccessError):
        channel_invite(us_token0, ch_id0, us_id1)

def test_user_id_1():
    '''Invalid case: inviting to channel with an invalid user ID'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(error.AccessError):
        channel_invite(us_token0, ch_id0, 12345)

def test_access_permission_1():
    '''Invalid case: inviting using an invalid token'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(error.AccessError):
        channel_invite('us_token1', ch_id0, us_id1)

def test_user_in_channel_1():
    '''Invalid case: inviting a user who is already in the channel'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    channel_invite(us_token0, ch_id0, us_id1)

    with pytest.raises(error.AccessError):
        channel_invite(us_token0, ch_id0, us_id1)

def test_invalid_token():
    '''Invalid case: the token is invalid'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(error.AccessError):
        channel_invite('invalid', ch_id0, us_id1)
