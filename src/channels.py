"""
Functions for channels.
"""
from data import data_channel, data_user
from error import AccessError, InputError
from webtoken import token_validate

def channels_list(token):
    '''
    Given a valid token, checks channel data for authorised user and returns
    a list of channels that authorised user is part of, containing id and name
    of each channel.
    '''
    # Check if token is valid
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise AccessError("Invalid token")

    auth_channels = []

    # put channel details into dictionary and add this to list.
    for channel in data_channel:
        if user_id in data_channel[channel]['all_members']:
            auth_channel_new = {
                'channel_id': channel,
                'name': data_channel[channel]['channel_name'],
            }
            auth_channels.append(dict(auth_channel_new))

    return {
        'channels': auth_channels
    }

def channels_listall(token):
    '''
    Given a valid token, returns list of all channels containing dictionaries
    with every channel's id and name.
    '''
    # Check if token is valid
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise AccessError("Invalid token")

    all_channels = []

    # put channel details into dictionary and add this to list
    for channel in data_channel:
        channel_new = {
            'channel_id': channel,
            'name': data_channel[channel]['channel_name'],
        }
        all_channels.append(dict(channel_new))

    return {
        'channels': all_channels
    }

def channels_create(token, name, is_public):
    '''
    Given a valid token, valid name and boolean for public or private, creates
    a channel and stores channel info in channel data. Returns channel id.
    '''
    # Check if name is valid
    if len(name) > 20:
        raise InputError(description="Invalid name")

    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise AccessError("Invalid token")

    channel_id = 0
    for channel in data_channel:
        channel_id = channel + 1

    data_channel[channel_id] = {
        'token': token,
        'channel_name': name,
        'public': is_public,
        'owner_members': [
            user_id,
            ],
        'all_members': [
            user_id,
            ],
    }
    data_user[user_id]['permission_id'] == 1

    return {
        'channel_id': channel_id
    }
