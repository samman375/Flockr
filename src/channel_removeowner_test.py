'''
Backend tests for channel_removeowner
'''

import pytest
import channel
import error
from auth import auth_register
from channels import channels_create
from other import clear

def test_channel_removeowner_valid():
    '''Valid case: all inputs valid'''
    clear()

    # Users registered, added to new channel, Jim and Steve both owners
    info_0 = auth_register("jim.roberts1@email.com", "jimroberts0", "jim", "roberts")
    us_id0 = info_0['u_id']
    us_token0 = info_0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    info_1 = auth_register("steve.jobs2@email.com", "stevejobs2", "steve", "jobs")
    us_id1 = info_1['u_id']
    us_token1 = info_1['token']

    channel.channel_invite(us_token0, ch_id0, us_id1)
    channel.channel_addowner(us_token0, ch_id0, us_id1)

    assert channel.channel_details(us_token1, ch_id0)['owner_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]

    channel.channel_removeowner(us_token0, ch_id0, us_id1)

    assert channel.channel_details(us_token0, ch_id0)['owner_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'}
    ]

def test_channel_removeowner_invalid_channel():
    '''Invalid case: invalid channel ID'''
    clear()

    # Users registered, added to new channel, Jim and Steve both owners
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    # Should return an error given incorrect channel ID
    with pytest.raises(error.InputError):
        channel.channel_removeowner(us_token0, 4, us_id1)

def test_channel_removeowner_user_not_owner():
    '''Invalid case: attempting to remove a user who is not an owner'''
    clear()

    # Users registered, added to new channel, Jim is owner, Steve is not
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    channel.channel_invite(us_token0, ch_id0, us_id1)

    # Should return an error as Steve is not an owner
    with pytest.raises(error.InputError):
        channel.channel_removeowner(us_token0, ch_id0, us_id1)

def test_channel_removeowner_caller_not_owner():
    '''Invalid case: the user calling to remove owner doesn't have the permission to'''
    clear()

    # Users registered, added to new channel, Jim is owner, Steve is not
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    channel.channel_invite(us_token0, ch_id0, us_id1)

    # Should return an error as Steve is not an owner
    with pytest.raises(error.AccessError):
        channel.channel_removeowner(us_token1, ch_id0, us_id0)

def test_invalid_token():
    '''Invalid case: token is invalid'''
    clear()

    info_0 = auth_register("jim.roberts1@email.com", "jimroberts0", "jim", "roberts")
    us_token0 = info_0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    info_1 = auth_register("steve.jobs2@email.com", "stevejobs2", "steve", "jobs")
    us_id1 = info_1['u_id']

    channel.channel_invite(us_token0, ch_id0, us_id1)
    channel.channel_addowner(us_token0, ch_id0, us_id1)

    with pytest.raises(error.AccessError):
        channel.channel_removeowner('invalid', ch_id0, us_id1)

def test_user_not_in():
    '''Invalid case: trying to remove an owner who isn't in the channel'''
    clear()

    info_0 = auth_register("jim.roberts1@email.com", "jimroberts0", "jim", "roberts")
    us_token0 = info_0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    info_1 = auth_register("steve.jobs2@email.com", "stevejobs2", "steve", "jobs")
    us_id1 = info_1['u_id']
    us_token1 = info_1['token']

    channels_create(us_token1, "channel_name1", True)

    with pytest.raises(error.InputError):
        channel.channel_removeowner(us_token0, ch_id0, us_id1)

def test_remove_last():
    '''Invalid case: trying to remove the last owner of the channel'''
    clear()

    info_0 = auth_register("jim.roberts1@email.com", "jimroberts0", "jim", "roberts")
    us_token0 = info_0['token']
    us_id0 = info_0['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(error.InputError):
        channel.channel_removeowner(us_token0, ch_id0, us_id0)
