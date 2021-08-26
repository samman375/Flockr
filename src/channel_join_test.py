'''
Backend tests for channel_leave
'''

import pytest
import channel
from channels import channels_create
from auth import auth_register
from error import InputError, AccessError
from other import clear


def test_channel_join_valid():
    '''Valid case: valid use with all inputs valid'''
    clear()

    # Users registered and channel created by first user
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']
    us_id0 = us_dic0['u_id']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    # Channel exists and public, should succeed
    channel.channel_join(us_token1, ch_id0)

    # Test user added with channel_details
    assert channel.channel_details(us_token0, ch_id0)['owner_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'}
    ]

    assert channel.channel_details(us_token0, ch_id0)['all_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]

def test_channel_invalid_ch():
    '''Invalid case: inviting a user to a channel that doesn't exist'''
    clear()

    # Users registered and channel created by first user
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    # Incorrect channel_id given, should fail
    with pytest.raises(InputError):
        channel.channel_join(us_token0, 123)

def test_channel_invalid_access():
    '''Invalid case: the user is invited to a private channel'''
    clear()

    # Users registered and private channel created by first user
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", False)['channel_id']

    # Private channel given, should fail
    with pytest.raises(AccessError):
        channel.channel_join(us_token1, ch_id0)

def test_invalid_token():
    '''Invalid case: the token is invalid'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(AccessError):
        channel.channel_join('invalid', ch_id0)

def test_user_already_added():
    '''Invalid case: trying to add a user to a channel they're already in'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    channel.channel_join(us_token1, ch_id0)

    with pytest.raises(InputError):
        channel.channel_join(us_token1, ch_id0)

def test_add_permitted_user():
    '''Valid case: adding a user who has owner permissions, making sure they're added as an owner'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']
    us_id0 = us_dic0['u_id']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']
    us_id1 = us_dic1['u_id']

    channels_create(us_token0, "channel_name0", True)
    ch_id1 = channels_create(us_token1, "channel_name1", True)['channel_id']

    channel.channel_join(us_token0, ch_id1)
    assert channel.channel_details(us_token0, ch_id1)['owner_members'] == [
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'},
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
    ]
