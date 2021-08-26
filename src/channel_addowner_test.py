'''
Backend tests for channel_addowner function
'''

import pytest
import channel
from channels import channels_create
from auth import auth_register
from error import AccessError, InputError
from other import clear


def test_channel_addowner_valid():
    '''Valid case: simple valid usecase with all valid inputs'''
    clear()

    # Users registered and added to new channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    channel.channel_invite(us_token0, ch_id0, us_id1)

    # Requesting user already owner and channel is valid, 2nd user not already owner
    # Should Succeed

    # Test 2nd user is owner with channel_details
    assert channel.channel_details(us_token0, ch_id0)['owner_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'}
    ]

    channel.channel_addowner(us_token0, ch_id0, us_id1)

    assert channel.channel_details(us_token0, ch_id0)['owner_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]


def test_channel_addowner_invalid_ch():
    '''Invalid case: trying to add owners to a channel that doesn't exist'''
    clear()

    # Users registered but not channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    # Invalid channel_id supplied, should fail
    with pytest.raises(InputError):
        channel.channel_addowner(us_token0, 'invalid', us_id0)


def test_channel_addowner_invalid_user():
    '''Invalid case: trying to add an owner who is already an owner'''
    clear()

    # Users registered and added to channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    channel.channel_invite(us_token0, ch_id0, us_id1)

    # Second user also made owner
    channel.channel_addowner(us_token0, ch_id0, us_id1)

    # user_id supplied is already owner, should fail
    with pytest.raises(InputError):
        channel.channel_addowner(us_token0, ch_id0, us_id1)

def test_channel_addowner_invalid_access():
    '''Invalid case: the user calling the addowner function is not an owner'''
    clear()

    # Users registered and added to channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']
    us_token1 = us_dic1['token']

    channel.channel_invite(us_token0, ch_id0, us_id1)

    us_dic2 = auth_register("harry.potter3@email.com", "harrypotter3", "harry", "potter")
    us_id2 = us_dic2['u_id']

    channel.channel_invite(us_token0, ch_id0, us_id2)

    # Requesting user not owner of flockr or channel, should fail
    with pytest.raises(AccessError):
        channel.channel_addowner(us_token1, ch_id0, us_id2)

def test_invalid_token():
    '''Invalid case: token is invalid'''
    clear()

    info_0 = auth_register("jim.roberts1@email.com", "jimroberts0", "jim", "roberts")
    us_token0 = info_0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    info_1 = auth_register("steve.jobs2@email.com", "stevejobs2", "steve", "jobs")
    us_id1 = info_1['u_id']

    channel.channel_invite(us_token0, ch_id0, us_id1)

    with pytest.raises(AccessError):
        channel.channel_addowner('invalid', ch_id0, us_id1)

def test_not_in_channel():
    '''Invalid case: trying to add a user who isn't in the channel as an owner'''
    clear()
    info_0 = auth_register("jim.roberts1@email.com", "jimroberts0", "jim", "roberts")
    us_token0 = info_0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    info_1 = auth_register("steve.jobs2@email.com", "stevejobs2", "steve", "jobs")
    us_id1 = info_1['u_id']

    with pytest.raises(InputError):
        channel.channel_addowner(us_token0, ch_id0, us_id1)
