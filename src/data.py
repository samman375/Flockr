'''
FLOCKR DATA STRUCTURES
'''

# Nested dictionary for storing user data
data_user = dict()

'''
    user_id : {
        'handle_str'    : 'firstlast',
        'email'         : 'name@domain.com',
        'password'      : 'password123',
        'token'         : 'token',
        'name_first'    : 'first',
        'name_last'     : 'last',
        'permission_id' : 1,
   },
'''

# List of currently valid user tokens
current_tokens = []

'''
    'name@domain.com',
'''

# Nested dictionary for storing channel data
data_channel = dict()

'''
    channel_id : {
        'channel_name' : 'channel1',
        'token' : 56789,
        'public' : True,
        'owner_members' : [
            user id,
        ],
        'all_members' : [
            user id,
            user id,
        ],
    }
'''

# Nested dictionary for storing message data
data_messages = dict()

'''
{
    'count' : (total number of messages sent)
    channel_id : [
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'Hello world',
            'time_created': unix timestamp,
            'reacts': [],
            'is_pinned': False
        }
    ]
}
'''

# Dictionary with all current passwordreset secret numbers and corresponding u_id
current_passwordreset_codes = dict()
'''
{
    '1': secret_num
}
'''

# List of all valid react_id's
data_reacts = [1]
