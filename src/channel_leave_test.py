'''Backend tests for channel_leave
'''

import pytest
import channel
from channels import channels_create
from auth import auth_register
from error import AccessError, InputError
from other import clear

def test_channel_leave_valid0():
    '''Valid case: valid use of channel_leave with all inputs valid'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    channel.channel_invite(us_token0, ch_id0, us_id1)

    assert channel.channel_details(us_token0, ch_id0)['all_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]

    channel.channel_leave(us_token1, ch_id0)

    assert channel.channel_details(us_token0, ch_id0)['all_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'}
    ]

def test_channel_leave_valid1():
    '''Valid case: making sure ownership is passed-on when the last owner leaves'''
    clear()

    # Users registered and added to channel
    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    channel.channel_invite(us_token0, ch_id0, us_id1)

    # Owner requests leave
    # Should succeed as user is in channel and channel exists
    # Ownership should be transferred to remaining user
    assert channel.channel_details(us_token0, ch_id0)['owner_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'}
    ]
    assert channel.channel_details(us_token0, ch_id0)['all_members'] == [
        {'u_id': us_id0, 'name_first': 'jim', 'name_last': 'roberts'},
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]

    channel.channel_leave(us_token0, ch_id0)

    assert channel.channel_details(us_token1, ch_id0)['all_members'] == [
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]
    assert channel.channel_details(us_token0, ch_id0)['owner_members'] == [
        {'u_id': us_id1, 'name_first': 'steve', 'name_last': 'jobs'}
    ]

def test_channel_leave_ownership_change():
    '''Valid case: another test of ownership change when the last owner leaves'''
    clear()

    us_dic0 = auth_register("a.b@email.com", "abcd12", "aaaa", "bbbb")
    us_dic1 = auth_register("c.d@email.com", "efgh23", "cccc", "dddd")
    us_dic2 = auth_register("e.f@email.com", "ijkl34", "eeee", "ffff")
    us_dic3 = auth_register("g.h@email.com", "mnop45", "gggg", "hhhh")
    us_dic4 = auth_register("i.j@email.com", "qrst56", "iiii", "jjjj")
    us_dic5 = auth_register("k.l@email.com", "wxyz67", "kkkk", "llll")

    ch_id0 = channels_create(us_dic0['token'], "channel_name0", True)['channel_id']
    channel.channel_invite(us_dic0['token'], ch_id0, us_dic1['u_id'])
    channel.channel_invite(us_dic0['token'], ch_id0, us_dic2['u_id'])
    channel.channel_invite(us_dic0['token'], ch_id0, us_dic3['u_id'])
    channel.channel_invite(us_dic0['token'], ch_id0, us_dic4['u_id'])
    channel.channel_invite(us_dic0['token'], ch_id0, us_dic5['u_id'])

    channel.channel_addowner(us_dic0['token'], ch_id0, us_dic3['u_id'])

    assert channel.channel_details(us_dic0['token'], ch_id0)['owner_members'] == [
        {'u_id': us_dic0['u_id'], 'name_first': 'aaaa', 'name_last': 'bbbb'},
        {'u_id': us_dic3['u_id'], 'name_first': 'gggg', 'name_last': 'hhhh'}
    ]

    channel.channel_leave(us_dic0['token'], ch_id0)

    assert channel.channel_details(us_dic3['token'], ch_id0)['owner_members'] == [
        {'u_id': us_dic3['u_id'], 'name_first': 'gggg', 'name_last': 'hhhh'}
    ]

    channel.channel_leave(us_dic3['token'], ch_id0)

    assert channel.channel_details(us_dic1['token'], ch_id0)['owner_members'] == [
        {'u_id': us_dic1['u_id'], 'name_first': 'cccc', 'name_last': 'dddd'}
    ]

def test_channel_leave_last_user():
    '''Valid case: making sure the channel is deleted when the last user leaves'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    channel.channel_leave(us_token0, ch_id0)

    with pytest.raises(InputError):
        channel.channel_details(us_token0, ch_id0)

def test_channel_leave_invalid_ch():
    '''Invalid case: trying to leave a channel that doesn't exist'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    with pytest.raises(InputError):
        channel.channel_leave(us_token0, 13)

def test_channel_leave_invalid_access():
    '''Invalid case: the requesting user is not in the channel'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']

    with pytest.raises(AccessError):
        channel.channel_leave(us_token1, ch_id0)

def test_invalid_token():
    '''Invalid case: the token is invalid'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    ch_id0 = channels_create(us_token0, "channel_name0", True)['channel_id']
    channel.channel_invite(us_token0, ch_id0, us_id1)

    with pytest.raises(AccessError):
        channel.channel_leave('invalid', ch_id0)
