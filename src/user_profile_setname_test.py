'''
Backend tests for user_profile_setname function
'''

import pytest
from other import clear
import error
from auth import auth_register
from user import user_profile, user_profile_setname

def test_user_setname_valid():
    '''Valid case: three users are correctly registered, names should change'''
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

    # Check names before and after with user_profile

    assert user_profile(us_token0, us_id0)['user']['name_first'] == "jim"
    assert user_profile(us_token0, us_id0)['user']['name_last'] == "roberts"

    assert user_profile(us_token1, us_id1)['user']['name_first'] == "steve"
    assert user_profile(us_token1, us_id1)['user']['name_last'] == "jobs"

    assert user_profile(us_token2, us_id2)['user']['name_first'] == "tim"
    assert user_profile(us_token2, us_id2)['user']['name_last'] == "timothy"

    user_profile_setname(us_token0, "bob", "marley")
    user_profile_setname(us_token1, "robert", "downey jr.")
    user_profile_setname(us_token2, "ireland", "o'name")

    assert user_profile(us_token0, us_id0)['user']['name_first'] == "bob"
    assert user_profile(us_token0, us_id0)['user']['name_last'] == "marley"

    assert user_profile(us_token1, us_id1)['user']['name_first'] == "robert"
    assert user_profile(us_token1, us_id1)['user']['name_last'] == "downey jr."

    assert user_profile(us_token2, us_id2)['user']['name_first'] == "ireland"
    assert user_profile(us_token2, us_id2)['user']['name_last'] == "o'name"


def test_user_setname_invalid_token():
    '''Invalid case: three users are correctly registered but an invalid token is supplied'''
    clear()

    auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    auth_register("steve.jobs2@email.com", "stevejobs", "steve", "jobs")
    auth_register("tim.timothy@email.com", "timtimothy", "tim", "timothy")

    with pytest.raises(error.AccessError):
        user_profile_setname("invalid", "bob", "marley")
    with pytest.raises(error.AccessError):
        user_profile_setname("invalid", "john", "lennon")
    with pytest.raises(error.AccessError):
        user_profile_setname("invalid", "rick", "astley")


def test_user_setname_invalid_name_first():
    '''Invalid case: user correctly registered, invalid name_first supplied'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    # Length based errors

    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "", "marley")
    with pytest.raises(error.InputError):
        user_profile_setname(
            us_token0,
            "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn",
            "marley"
        )

    # Assumption based errors according to assumptions.md

    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "23141204899", "marley")
    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, '"./,/./;,/.,;/,', "marley")


def test_user_setname_invalid_name_last():
    '''Invalid case: user correctly registered, invalid name_last supplied'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    # Length based errors

    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "Bono", "")
    with pytest.raises(error.InputError):
        user_profile_setname(
            us_token0,
            "rick",
            "astleyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        )

    # Assumption based errors according to assumptions.md

    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "Johnno", "12341241")
    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "Henry", ".,;,/./;,/,.;")
    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "Harrison", "1235154414531./.'..;.")


def test_user_setname_invalid_names():
    '''Invalid case: user is correctly registered, invalid name_first and name_last supplied'''
    clear()

    us_dic0 = auth_register("jim.roberts1@email.com", "jimroberts", "jim", "roberts")
    us_token0 = us_dic0['token']

    # Length based errors

    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "", "")
    with pytest.raises(error.InputError):
        user_profile_setname(
            us_token0,
            "rickkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
            "astleyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        )
    with pytest.raises(error.InputError):
        user_profile_setname(
            us_token0,
            "",
            "astleyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        )
    with pytest.raises(error.InputError):
        user_profile_setname(
            us_token0,
            "",
            "astleyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        )

    # Assumption based errors according to assumptions.md

    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "123414545", "12341241")
    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, ",/.,/.;.,//;,", ".,;,/./;,/,.;")
    with pytest.raises(error.InputError):
        user_profile_setname(us_token0, "132/.4,/1.,41/,4", "1235154414531./.'..;.")
