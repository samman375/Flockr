'''
Channel.py, which is used to add and remove users from a channel, and to
gain information about channels and permissions.
Written by Sam and Georgia.
'''

import error
from data import data_user, data_channel, data_messages
from webtoken import token_validate

def channel_invite(token, channel_id, u_id):
    '''
    A function called by one user (token), on another (u_id).
    The invitee is added to the channel, given that the calling member
    is a member of the channel.
    '''
    if channel_id not in data_channel:
        raise error.InputError(description='Invalid channel ID')

    inviting_user_id = token_validate(token)
    if inviting_user_id == 'INVALID':
        raise error.AccessError("Invalid token")

    if inviting_user_id not in data_channel[channel_id]['all_members']:
        raise error.AccessError('Inviting user not in channel')

    if u_id in data_channel[channel_id]['all_members']:
        raise error.AccessError(description='Invited user already in channel')

    if u_id not in data_user:
        raise error.AccessError(description='Invalid user ID')

    if not data_channel[channel_id]['public'] and data_user[u_id]['permission_id'] != 1:
        raise error.AccessError(description='User is not authorised to join this channel')

     # add user to list of members if there are no exceptions
    data_channel[channel_id]['all_members'].append(u_id)
    if data_user[u_id]['permission_id'] == 1:
        data_channel[channel_id]['owner_members'].append(u_id)

    return {
    }

def channel_details(token, channel_id):
    '''
    returns the details of the channel given, including members, owners, ID, and name
    format of the returned dictionary:
    {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
    }
    '''
    if channel_id not in data_channel:
        raise error.InputError(description='Invalid channel ID')

    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError("Invalid token")

    is_owner = False
    if data_user[user_id]['permission_id'] == 1:
        is_owner = True

    if user_id not in data_channel[channel_id]['all_members'] and not is_owner:
        raise error.AccessError('User not in channel or not owner of Flockr')

    # Create dictionary with empty lists for owners and all members
    details = {
        'name' : data_channel[channel_id]['channel_name'],
        'owner_members' : [],
        'all_members' : []
    }

    # Add each owner member to owners list
    for user in data_channel[channel_id]['owner_members']:
        # User here will be the user ID

        details['owner_members'].append(
            {
                'u_id': user,
                'name_first': data_user[user]['name_first'],
                'name_last': data_user[user]['name_last']
            }
        )

    # Add all members to the all members list
    for user in data_channel[channel_id]['all_members']:
        details['all_members'].append(
            {
                'u_id': user,
                'name_first': data_user[user]['name_first'],
                'name_last': data_user[user]['name_last']
            }
        )

    # Return the channel dictionary
    return details

def channel_messages(token, channel_id, start):
    '''
    Returns the messages within a given range in a channel.
    provides the sender, time, message id, and content
    Format of returned dictionary: {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }
    '''
    # check token and user are valid
    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError("Invalid token")

    if channel_id not in data_channel:
        raise error.InputError(description='Invalid channel ID')

    if user_id not in data_channel[channel_id]['all_members']:
        raise error.AccessError(description='User not in channel')

    if channel_id not in data_messages:
        raise error.InputError(description='No messages have been sent in this channel yet')

    if start > len(data_messages[channel_id]):
        raise error.InputError(description='Start value is greater than number of messages')

    # get the messages
    mess_dict = {
        'messages': [],
        'start': start,
    }

    i = 0
    if len(data_messages[channel_id]) != 0:
        while i < 50 and (start + i) <= len(data_messages[channel_id]):
            if data_messages[channel_id][start + i - 1]['message'] != "WAITING TO BE SENT":
                mess_dict['messages'].append(data_messages[channel_id][start + i - 1])
            i += 1

    if (start + i) < len(data_messages[channel_id]):
        mess_dict['end'] = (start + 50)
    else:
        mess_dict['end'] = -1

    return mess_dict

def channel_leave(token, channel_id):
    '''
    the user is removed from a channel they are in.
    '''

    user_id = token_validate(token)
    if user_id == 'INVALID':
        raise error.AccessError("Invalid token")

    if channel_id not in data_channel:
        raise error.InputError(description='Invalid channel ID')

    if user_id not in data_channel[channel_id]['all_members']:
        raise error.AccessError(description='User not in channel')

    owners = data_channel[channel_id]['owner_members']
    members = data_channel[channel_id]['all_members']
    if user_id in owners and len(owners) == 1 and len(members) > 1:
        if members[0] not in owners:
            new_owner = members[0]
        else:
            new_owner = members[1]
        channel_addowner(token, channel_id, new_owner)

    data_channel[channel_id]['all_members'].remove(user_id)
    if user_id in data_channel[channel_id]['owner_members']:
        data_channel[channel_id]['owner_members'].remove(user_id)

    if len(data_channel[channel_id]['all_members']) == 0:
        del data_channel[channel_id]

    return {
    }

def channel_join(token, channel_id):
    '''
    The user joins the channel given
    '''
    joining_user_id = token_validate(token)
    if joining_user_id == 'INVALID':
        raise error.AccessError("Invalid token")

    if channel_id not in data_channel:
        raise error.InputError(description='Invalid channel ID')

    if not data_channel[channel_id]['public']:
        if not data_user[joining_user_id]['permission_id'] == 1:
            raise error.AccessError(description='User is not authorised to join this channel')

    if joining_user_id in data_channel[channel_id]['all_members']:
        raise error.InputError(description='User already in channel')

    # add user to list of members if no exceptions raised
    data_channel[channel_id]['all_members'].append(joining_user_id)
    if data_user[joining_user_id]['permission_id'] == 1:
        data_channel[channel_id]['owner_members'].append(joining_user_id)

    return {
    }

def channel_addowner(token, channel_id, u_id):
    '''
    user id is added to the owner list, if the user is not already an owner
    and is in the channel.
    '''
    valid_token = False
    valid_u_id = False

    if channel_id not in data_channel:
        raise error.InputError(description='Invalid channel ID')

    user = token_validate(token)
    if user == 'INVALID':
        raise error.AccessError("Invalid token")

    if data_user[user]['permission_id'] == 1:
        valid_token = True
    if user in data_channel[channel_id]['owner_members']:
        valid_token = True

    if u_id in data_user:
        joining_user_id = u_id
        valid_u_id = True

    if not valid_token:
        raise error.AccessError(description='Invalid access')

    if not valid_u_id or joining_user_id not in data_channel[channel_id]['all_members']:
        raise error.InputError(description='User not in channel')

    if u_id in data_channel[channel_id]['owner_members']:
        raise error.InputError(description='User already owner')

    # add user to list of owners if no exceptions raised
    data_channel[channel_id]['owner_members'].append(u_id)
    data_user[u_id]['permission_id'] = 2

    return {
    }

def channel_removeowner(token, channel_id, u_id):
    '''
    an owner is removed from the owner list. If the owner is the last one in
    the channel, they cannot be removed.
    '''
    valid_token = False
    valid_u_id = False

    if channel_id not in data_channel:
        raise error.InputError(description='Invalid channel ID')

    user = token_validate(token)
    if user == 'INVALID':
        raise error.AccessError("Invalid token")

    if user in data_channel[channel_id]['owner_members']:
        valid_token = True

    if u_id in data_user:
        leaving_user = u_id
        valid_u_id = True

    if not valid_token:
        raise error.AccessError(description='Invalid access')

    # if channel_id not in data_channel:
    #     raise error.InputError('Invalid channel ID')

    if not valid_u_id or leaving_user not in data_channel[channel_id]['all_members']:
        raise error.InputError(description='User not in channel')

    if u_id not in data_channel[channel_id]['owner_members']:
        raise error.InputError(description='User not an owner')

    if len(data_channel[channel_id]['owner_members']) == 1:
        raise error.InputError(description='Must be at least 1 owner in channel')

    # add user to list of owners if no exceptions raised
    data_channel[channel_id]['owner_members'].remove(leaving_user)

    return {
    }
