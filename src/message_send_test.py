'''
Backend tests for message_send function
'''

import pytest
import channel
import channels
import auth
from message import message_send
from error import AccessError, InputError
from other import clear

def test_valid():
    '''Valid case: all inputs valid, everything works'''
    clear()

    info = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token = info['token']
    user = info['u_id']

    channel_id = channels.channels_create(token, "name", True)['channel_id']

    assert message_send(token, channel_id, "hello")['message_id'] == 0

    assert len(channel.channel_messages(token, channel_id, 1)["messages"]) == 1
    assert channel.channel_messages(token, channel_id, 1)["messages"][0]["message"] == "hello"
    assert channel.channel_messages(token, channel_id, 1)["messages"][0]["u_id"] == user

    assert message_send(token, channel_id, "helloooo")['message_id'] == 1

    assert len(channel.channel_messages(token, channel_id, 1)["messages"]) == 2
    assert channel.channel_messages(token, channel_id, 1)["messages"][1]["message"] == "helloooo"

    assert message_send(token, channel_id, "hi")['message_id'] == 2

    assert len(channel.channel_messages(token, channel_id, 1)["messages"]) == 3
    assert channel.channel_messages(token, channel_id, 1)["messages"][2]["message"] == "hi"

def test_invalid_token():
    '''Invalid case: sending to a channel with an invalid token'''
    clear()

    token = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")['token']

    channel_id = channels.channels_create(token, "name", True)['channel_id']

    with pytest.raises(AccessError):
        message_send(4, channel_id, "beans")

def test_invalid_channel():
    '''Invalid case: the user tries to send to a channel that doesn't exist'''
    clear()

    info = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token = info['token']

    with pytest.raises(InputError):
        message_send(token, 4, "hello")

def test_invalid_user():
    '''Invalid case: the user isn't in the channel they're trying to a send message in'''
    clear()

    info1 = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token1 = info1['token']

    info2 = auth.auth_register("jon.bob@email.com", "jonbob", "jon", "bob")
    token2 = info2['token']

    channel_id = channels.channels_create(token1, "name", True)['channel_id']

    message_send(token1, channel_id, "I'm in this channel")

    with pytest.raises(AccessError):
        message_send(token2, channel_id, "I'm not in this channel")

def test_too_long():
    '''Invalid case: the message exceeds the 1000 character limit'''
    clear()

    info = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token = info['token']

    long_message = '''
    According to all known laws of aviation, there is no way a bee should be able to
    fly. Its wings are too small to get its fat little body off the ground.The bee, of course,
    flies anyway because bees don't care what humans think is impossible. Yellow, black. Yellow,
    black. Yellow, black. Yellow, black. Ooh, black and yellow! Let's shake it up a little.
    Barry! Breakfast is ready! Ooming! Hang on a second. Hello? - Barry? - Adam? - Oan you
    believe this is happening? - I can't. I'll pick you up. Looking sharp. Use the stairs. Your
    father paid good money for those. Sorry. I'm excited. Here's the graduate. We're very proud
    of you, son. A perfect report card, all B's. Very proud. Ma! I got a thing going here. -
    You got lint on your fuzz. - Ow! That's me! - Wave to us! We'll be in row 118,000. - Bye!
    Barry, I told you, stop flying in the house! - Hey, Adam. - Hey, Barry. - Is that fuzz gel?
    - A little. Special day, graduation. Never thought I'd make it. Three days grade school, three
    days high school. Those were awkward. Three days college. I'm glad I took a day and
    hitchhiked around the hive. You did come back different. - Hi, Barry. - Artie, growing a
    mustache? Looks good. - Hear about Frankie? - Yeah. - You going to the funeral? - No, I'm not
    going. Everybody knows, sting someone, you die. Don't waste it on a squirrel. Such a hothead.
    I guess he could have just gotten out of the way. I love this incorporating an amusement park
    into our day. That's why we don't need vacations. Boy, quite a bit of pomp... under the
    circumstances. - Well, Adam, today we are men. - We are! - Bee-men. - Amen! Hallelujah!
    Students, faculty, distinguished bees, please welcome Dean Buzzwell. Welcome, New Hive Oity
    graduating class of... ...9:15. That concludes our ceremonies. And begins your career at Honex
    Industries! Will we pick ourjob today? I heard it's just orientation.'''

    channel_id = channels.channels_create(token, "name", True)['channel_id']

    with pytest.raises(InputError):
        message_send(token, channel_id, long_message)

def test_no_message():
    '''Invalid case: the message string is empty'''
    clear()

    info = auth.auth_register("jim.rob@email.com", "jimrob", "jim", "rob")
    token = info['token']

    channel_id = channels.channels_create(token, "name", True)['channel_id']

    with pytest.raises(InputError):
        message_send(token, channel_id, "")
