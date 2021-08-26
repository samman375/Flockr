'''
Global functions for clearing stored data, gathering all user data,
changing user's global permissions and searching for messages
'''

from data import data_user, current_tokens, data_channel, data_messages
from webtoken import token_validate
from channels import channels_list
from error import AccessError, InputError

def clear():
    '''Empties all data structures'''
    data_user.clear()
    current_tokens.clear()
    data_channel.clear()
    data_messages.clear()

def users_all(token):
    '''Returns dictionary containing a list of all the currently registered user's data'''

    valid_token_check(token)

    users = []
    for user in data_user:
        curr_user = {}
        curr_user['u_id'] = user
        curr_user['email'] = data_user[user]['email']
        curr_user['name_first'] = data_user[user]['name_first']
        curr_user['name_last'] = data_user[user]['name_last']
        curr_user['handle_str'] = data_user[user]['handle_str']
        users.append(curr_user)

    return {'users': users}


def admin_userpermission_change(token, u_id, permission_id):
    '''Function for owners to change the permission_id of a specific user'''

    valid_token_check(token)

    valid_ids = [1, 2]
    if permission_id not in valid_ids:
        raise InputError(description='Invalid permission ID')

    for user in data_user:
        if token_validate(token) == user:
            if data_user[user]['permission_id'] != 1:
                raise AccessError(description='You are not authorised to change user permissions')

    valid_u_id = 0
    owner_count = 0
    curr_perm_id = 0
    for user in data_user:
        if data_user[user]['permission_id'] == 1:
            owner_count += 1
        if user == u_id:
            valid_u_id = 1
            curr_perm_id = data_user[user]['permission_id']

    if valid_u_id == 0:
        raise InputError('Invalid user ID')

    if curr_perm_id == permission_id:
        return

    if token_validate(token) == u_id and owner_count == 1:
        raise InputError('There must be at least ONE global owner at all times')

    data_user[u_id]['permission_id'] = permission_id

    return {}

def search(token, query_str):
    '''Returns list of messages containing the query string in all channels the user has joined'''

    valid_token_check(token)

    returned_messages = []
    joined_channels = channels_list(token)['channels']

    for channel in joined_channels:
        ch_id = channel['channel_id']
        if ch_id in data_messages:
            for i in range(len(data_messages[ch_id])):
                if data_messages[ch_id][i]['message'] != "WAITING TO BE SENT":
                    if query_str.lower() in data_messages[ch_id][i]['message'].lower():
                        returned_messages.append(data_messages[ch_id][i])

    return {'messages' : returned_messages}


def valid_token_check(token):
    '''Checks if token is currently valid'''
    if token_validate(token) == 'INVALID':
        raise AccessError(description='This token is not currently authorised')
