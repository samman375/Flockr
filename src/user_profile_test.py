'''
Backend tests for user_profile function
'''

import pytest
from other import clear
import error
from auth import auth_register
from user import user_profile

def test_user_profile_valid():
    '''Valid case: three users are correctly registered with all valid inputs'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']
    us_token1 = us_dic1['token']

    us_dic2 = auth_register("tim.timothy@email.com", "timtimothy", "tim", "timothy")
    us_id2 = us_dic2['u_id']
    us_token2 = us_dic2['token']

    assert user_profile(us_token0, us_id0)['user']['u_id'] == us_id0
    assert user_profile(us_token0, us_id0)['user']['email'] == "jim.roberts1@email.com"
    assert user_profile(us_token0, us_id0)['user']['name_first'] == "jim"
    assert user_profile(us_token0, us_id0)['user']['name_last'] == "roberts"
    assert user_profile(us_token0, us_id0)['user']['handle_str'] == "jimroberts"

    assert user_profile(us_token1, us_id1)['user']['u_id'] == us_id1
    assert user_profile(us_token1, us_id1)['user']['email'] == "steve.jobs2@email.com"
    assert user_profile(us_token1, us_id1)['user']['name_first'] == "steve"
    assert user_profile(us_token1, us_id1)['user']['name_last'] == "jobs"
    assert user_profile(us_token1, us_id1)['user']['handle_str'] == "stevejobs"

    assert user_profile(us_token2, us_id2)['user']['u_id'] == us_id2
    assert user_profile(us_token2, us_id2)['user']['email'] == "tim.timothy@email.com"
    assert user_profile(us_token2, us_id2)['user']['name_first'] == "tim"
    assert user_profile(us_token2, us_id2)['user']['name_last'] == "timothy"
    assert user_profile(us_token2, us_id2)['user']['handle_str'] == "timtimothy"


def test_user_profile_invalid_uid():
    '''Invalid case: three users are registered with invalid u_id supplied'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_token1 = us_dic1['token']

    us_dic2 = auth_register("tim.timothy@email.com", "timtimothy", "tim", "timothy")
    us_token2 = us_dic2['token']

    with pytest.raises(error.InputError):
        user_profile(us_token0, '420')
    with pytest.raises(error.InputError):
        user_profile(us_token1, '420')
    with pytest.raises(error.InputError):
        user_profile(us_token2, '420')


def test_user_profile_invalid_token():
    '''Invalid case: three users are registered with invalid tokens supplied'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_id0 = us_dic0['u_id']

    us_dic1 = auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    us_id1 = us_dic1['u_id']

    us_dic2 = auth_register("tim.timothy@email.com", "timtimothy", "tim", "timothy")
    us_id2 = us_dic2['u_id']

    with pytest.raises(error.AccessError):
        user_profile('invalid', us_id0)
    with pytest.raises(error.AccessError):
        user_profile('invalid', us_id1)
    with pytest.raises(error.AccessError):
        user_profile('invalid', us_id2)


def test_user_profile_invalid_token_uid():
    '''Invalid case: three users are registered with invalid tokens and u_id is supplied'''
    clear()

    auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    auth_register("tim.timothy@email.com", "timtimothy", "tim", "timothy")

    with pytest.raises(error.InputError):
        user_profile('invalid', '420')
    with pytest.raises(error.InputError):
        user_profile('invalid', '420')
    with pytest.raises(error.InputError):
        user_profile('invalid', '420')
