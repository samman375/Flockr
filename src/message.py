'''
Messages functions to send, remove, edit, react, and pin messages sent to a channel
'''

import threading
from datetime import datetime, timezone
import error
from data import data_user, data_channel, data_messages, data_reacts
from webtoken import token_validate

def check_channel(channel_id):
    '''
    Ensures the channel exists. If not, raises input error. Otherwise, returns true.
    '''
    if channel_id not in data_channel:
        raise error.InputError(description="Invalid channel ID")

    return True

def check_user_is_owner(user_id, channel_id):
    '''
    Ensures that the provided user is in the channel. If not, raises access error.
    Otherwise, returns True if they're an owner, or False if they're a member.
    '''
    if user_id not in data_channel[channel_id]['all_members']:
        raise error.AccessError(description="User not in channel")

    return bool(user_id in data_channel[channel_id]['owner_members'])

def check_message(message_id):
    '''
    Ensures that the message corresponding to the given ID exists.
    Raises an input error if the message doesn't exist.
    Returns a dictionary containing the it's channel ID and user ID.
    '''

    channel_id = -1
    user_id = -1
    for channel in data_messages:
        if channel != 'count':
            for message in data_messages[channel]:
                if message_id == message['message_id']:
                    if message['message'] == "WAITING TO BE SENT":
                        raise error.InputError(description="This message has not been sent yet")
                    channel_id = channel
                    user_id = message['u_id']

    if channel_id == -1:
        raise error.InputError(description="Invalid message ID")

    return {
        'user_id' : user_id,
        'channel_id' : channel_id,
    }

def message_send(token, channel_id, message):
    '''
    Send a message to a channel by adding it to the messages data structure.
    Raises input error when: message more than 1000 char.
    Raises access error when: user is not in the channel, invalid token.
    '''
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError("Invalid token")
    check_channel(channel_id)
    check_user_is_owner(user_id, channel_id)

    if len(message) > 1000:
        raise error.InputError(description="Message too long")

    if len(message) == 0:
        raise error.InputError(description="Message has no contents")

    if 'count' not in data_messages:
        data_messages['count'] = 0

    message_id = data_messages['count']
    data_messages['count'] += 1

    if channel_id not in data_messages:
        data_messages[channel_id] = []

    now = datetime.now()
    timestamp = now.replace(tzinfo=timezone.utc).timestamp()

    data_messages[channel_id].append(
        {
            'message_id': message_id,
            'u_id': user_id,
            'message': message,
            'time_created': timestamp,
            'reacts': [],
            'is_pinned': False,
        }
    )
    return {
        'message_id': message_id,
    }

def message_remove(token, message_id):
    '''
    Removes the message with corresponding id
    Input error: message ID doesn't exist
    Access error: when calling user did not send message or is not owner, invalid token
    '''
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError("Invalid token")

    info = check_message(message_id)
    is_owner = check_user_is_owner(user_id, info['channel_id'])

    if user_id != info['user_id'] and not is_owner:
        raise error.AccessError(description='User does not have permission to delete this message')

    for message in data_messages[info['channel_id']]:
        if message['message_id'] == message_id:
            data_messages['count'] -= 1
            data_messages[info['channel_id']].remove(message)
            break

    return {
    }

def message_edit(token, message_id, message):
    '''
    Edits the message, that corresponds to the given message id, to the new
    message passed in. If the message is edited to an empty string, deletes that
    message.
    Raises AccessError if the user editing the message is not the user that sent
    the message or the user is not an owner of the channel or flockr.
    '''
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError("Invalid token")

    info = check_message(message_id)
    is_owner = check_user_is_owner(user_id, info['channel_id'])

    if user_id != info['user_id'] and not is_owner:
        raise error.AccessError('User does not have permission to edit this message')

    for msg in data_messages[info['channel_id']]:
        if msg['message_id'] == message_id:
            if message == '':
                message_remove(token, message_id)
            else:
                now = datetime.now()
                timestamp = now.replace(tzinfo=timezone.utc).timestamp()
                msg['message'] = message
                msg['time_created'] = timestamp

    return {
    }

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Prepares a message to be sent at a given future time
    Via the threading library, the function assigns a thread to call the
    message_send function at a given future time
    Raises an error for invalid token, invalid channel, and
    any errors raised by functions called
    '''

    now = datetime.now()
    current_timestamp = now.replace(tzinfo=timezone.utc).timestamp()

    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError(description="Invalid token")

    check_channel(channel_id)

    check_user_is_owner(user_id, channel_id)

    if len(message) > 1000:
        raise error.InputError(description="This message exceeds the 1000 character limit")

    if len(message) == 0:
        raise error.InputError(description="Message has no contents")

    if time_sent < current_timestamp:
        raise error.InputError(description="Time sent cannot be in the past")

    if 'count' not in data_messages:
        data_messages['count'] = 0

    message_id = data_messages['count']
    data_messages['count'] += 1

    if channel_id not in data_messages:
        data_messages[channel_id] = []
    
    data_messages[channel_id].append(
        {
            'message_id': message_id,
            'message': "WAITING TO BE SENT"
        }
    )
    
    waiting_time = time_sent - current_timestamp
    t = threading.Timer(waiting_time, message_sendlater_sending, args=(message_id, token, channel_id, message))
    t.start()

    return {'message_id': message_id}

def message_sendlater_sending(message_id, token, channel_id, message):
    '''
    Send a message to a channel by adding it to the messages data structure.
    Raises input error when: message more than 1000 char.
    Raises access error when: user is not in the channel, invalid token.
    '''
    user_id = token_validate(token)

    now = datetime.now()
    timestamp = now.replace(tzinfo=timezone.utc).timestamp()

    for curr_msg in data_messages[channel_id]:
        if curr_msg['message_id'] == message_id:
            curr_msg['u_id'] = user_id
            curr_msg['message'] = message
            curr_msg['time_created'] = timestamp
            curr_msg['reacts'] = []
            curr_msg['is_pinned'] = False

def message_react(token, message_id, react_id):
    '''
    Adds the given react to the list of reacts.
    Raises an error for invalid token, invalid message id, or invalid react id
    '''
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError(description="Invalid token")

    info = check_message(message_id)
    channel_id = info['channel_id']

    if user_id not in data_channel[channel_id]['all_members']:
        raise error.InputError(description="You must be a part of the channel to react to this message")

    if react_id not in data_reacts:
        raise error.InputError(description="Invalid react ID")

    for msg in data_messages[info['channel_id']]:
        if msg['message_id'] == message_id:
            if react_id in msg['reacts']:
                raise error.InputError(description="Already reacted")
            else:
                msg['reacts'].append(react_id)

    return {}

def message_unreact(token, message_id, react_id):
    '''
    Adds the given react to the list of reacts.
    Raises an error for invalid token, invalid message id, or invalid react id
    '''
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError(description="Invalid token")

    info = check_message(message_id)
    channel_id = info['channel_id']

    if user_id not in data_channel[channel_id]['all_members']:
        raise error.InputError(description="You must be a part of the channel to edit reacts for this message")

    if react_id not in data_reacts:
        raise error.InputError(description="Invalid react")

    for msg in data_messages[info['channel_id']]:
        if msg['message_id'] == message_id:
            if react_id not in msg['reacts']:
                raise error.InputError(description="Cannot remove react")
            else:
                msg['reacts'].remove(react_id)

    return {}

def message_pin(token, message_id):
    '''
    Pins a message for special treatment by the frontend given that the user is
    a member of the channel, they're an owner, and that the message hasn't been
    pinned already
    '''

    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError(description="Invalid token")

    info = check_message(message_id)
    channel_id = info['channel_id']

    if user_id not in data_channel[channel_id]['all_members']:
        raise error.AccessError(description="You must be a part of the channel to pin this message")

    if data_user[user_id]['permission_id'] != 1:
        raise error.AccessError(description="You must be an owner to pin a message")

    for message in data_messages[channel_id]:
        if message['message_id'] == message_id:
            if message['is_pinned'] == True:
                raise error.InputError(description="This message has already been pinned")
            else:
                message['is_pinned'] = True

    return {}

def message_unpin(token, message_id):
    '''
    Unpins a message, given that the user is a member of the channel, 
    they're an owner, and that the message is currently pinned
    '''
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError(description="Invalid token")

    info = check_message(message_id)
    channel_id = info['channel_id']

    if user_id not in data_channel[channel_id]['all_members']:
        raise error.AccessError(description="You must be a part of the channel to unpin this message")

    if data_user[user_id]['permission_id'] != 1:
        raise error.AccessError(description="You must be an owner to unpin a message")

    for message in data_messages[channel_id]:
        if message['message_id'] == message_id:
            if message['is_pinned'] == False:
                raise error.InputError(description="This message isn't pinned")
            else:
                message['is_pinned'] = False
    return {}