'''
Backend tests for search function
'''

import pytest
from data import current_tokens, data_messages, data_channel
from channels import channels_create
from channel import channel_join
from message import message_send
from auth import auth_register as register
from error import AccessError
from other import clear, search


def generating_data():
    '''GENERATING DATA USED IN EACH TEST-CASE'''
    clear()
    test_data = {}

    flockr_owner = register('flockrowner@domain.com', 'password', 'First', 'Last')
    test_data['token_flockr_owner'] = flockr_owner['token']
    test_data['id_flockr_owner'] = flockr_owner['u_id']

    member1 = register('member1@domain.com', 'password', 'First', 'Last')
    test_data['token_member1'] = member1['token']
    test_data['id_member1'] = member1['u_id']

    member2 = register('member2@domain.com', 'password', 'First', 'Last')
    test_data['token_member2'] = member2['token']
    test_data['id_member2'] = member2['u_id']

    test_data['ch_id_public1'] = channels_create(test_data['token_flockr_owner'], 'Channel1', True)['channel_id']
    channel_join(test_data['token_member1'], test_data['ch_id_public1'])

    test_data['ch_id_public2'] = channels_create(test_data['token_member1'], 'Channel2', True)['channel_id']
    channel_join(test_data['token_flockr_owner'], test_data['ch_id_public2'])
    
    test_data['ch_id_private'] = channels_create(test_data['token_member2'], 'Channel3', False)['channel_id']

    return test_data


def get_comparing_data(msg_id_list):
    '''COLLATING ALL CORRECT MESSAGE DATA TO COMPARE WITH SEARCH RESULTS'''
    comparing_data = {}
    comparing_data['messages'] = []
    for channel in range(len(data_channel)):
        for i in range(len(data_messages[channel])):
            if data_messages[channel][i]['message_id'] in msg_id_list:
                comparing_data['messages'].append(data_messages[channel][i])
    
    return comparing_data


# VALID TOKEN

def test_search_valid_token():
    '''Valid case: valid token'''
    clear()
    token = register('name@domain.com', 'password', 'First', 'Last')['token']
    assert token in current_tokens
    ch_id = channels_create(token, 'MyChannel', True)['channel_id']
    message_send(token, ch_id, 'Hello, World!')
    search(token, 'Hello, World!')

def test_search_invalid_token():
    '''Invalid case: token not currently valid'''
    clear()
    assert 'sometoken' not in current_tokens
    with pytest.raises(AccessError):
        search('sometoken', 'Query')


# SIMPLE SEARCHING –– single channel to search

def test_valid_search_simple():
    '''Valid case: valid search with correctly returned data'''
    clear()
    token = register('name@domain.com', 'password', 'First', 'Last')['token']
    ch_id = channels_create(token, 'MyChannel', True)['channel_id']
    msg_id = message_send(token, ch_id, 'Hello, World!')['message_id']

    returned_data = search(token, 'Hello, World!')
    assert returned_data == {
        'messages': [
            data_messages[ch_id][msg_id]
        ]
    }

def test_valid_search_simple_contains():
    '''Valid case: valid search when message contains query string'''
    clear()
    token = register('name@domain.com', 'password', 'First', 'Last')['token']
    ch_id = channels_create(token, 'MyChannel', True)['channel_id']
    msg_id1 = message_send(token, ch_id, 'Hello, World!')['message_id']
    msg_id2 = message_send(token, ch_id, 'Hello, World! How r ya?')['message_id']

    returned_data = search(token, 'Hello, World!')
    assert returned_data == {
        'messages': [
            data_messages[ch_id][msg_id1],
            data_messages[ch_id][msg_id2]
        ]
    }

def test_valid_search_simple_letter_cases():
    '''Valid case: valid search when message contains different capitalisation from query'''
    clear()
    token = register('name@domain.com', 'password', 'First', 'Last')['token']
    ch_id = channels_create(token, 'MyChannel', True)['channel_id']
    msg_id = message_send(token, ch_id, 'hElLo, WoRlD!')['message_id']

    returned_data = search(token, 'Hello, World!')
    assert returned_data == {
        'messages': [
            data_messages[ch_id][msg_id]
        ]
    }


# MORE COMPLEX SEARCHING –– multiple channels to search with varied permissions, etc.

def test_valid_search_complex_multiple_channels_owner():
    '''Valid case: valid complex search with correctly returned data, user is owner'''
    data = generating_data()

    msg_id1 = message_send(data['token_flockr_owner'], data['ch_id_public1'], 'Hello!')['message_id']
    message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hello')
    msg_id2 = message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hello! e')['message_id']
    msg_id3 = message_send(data['token_member1'], data['ch_id_public1'], 'heLLO!')['message_id']
    msg_id4 = message_send(data['token_member1'], data['ch_id_public2'], 'uhhh... hellO!')['message_id']
    message_send(data['token_member2'], data['ch_id_private'], 'Hello, World!')

    comparing_data = get_comparing_data([msg_id1, msg_id2, msg_id3, msg_id4])

    returned_data = search(data['token_flockr_owner'], 'Hello!')
    assert returned_data == comparing_data


def test_valid_search_complex_multiple_channels_member1():
    '''Valid case: valid complex search with correctly returned data, user is member (1)'''
    data = generating_data()

    msg_id1 = message_send(data['token_flockr_owner'], data['ch_id_public1'], 'Hello!')['message_id']
    message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hello')
    msg_id2 = message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hello! e')['message_id']
    msg_id3 = message_send(data['token_member1'], data['ch_id_public1'], 'heLLO!')['message_id']
    msg_id4 = message_send(data['token_member1'], data['ch_id_public2'], 'uhhh... hellO!')['message_id']
    message_send(data['token_member2'], data['ch_id_private'], 'Hello, World!')

    comparing_data = get_comparing_data([msg_id1, msg_id2, msg_id3, msg_id4])

    returned_data = search(data['token_member1'], 'Hello!')
    assert returned_data == comparing_data


def test_valid_search_complex_multiple_channels_member2():
    '''Valid case: valid complex search with correctly returned data, user is member (2)'''
    data = generating_data()

    message_send(data['token_flockr_owner'], data['ch_id_public1'], 'Hello!')['message_id']
    message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hello')
    message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hello! e')['message_id']
    message_send(data['token_member1'], data['ch_id_public1'], 'heLLO!')['message_id']
    message_send(data['token_member1'], data['ch_id_public2'], 'uhhh... hellO!')['message_id']
    msg_id = message_send(data['token_member2'], data['ch_id_private'], 'Hello, World!')

    comparing_data = get_comparing_data([msg_id])

    returned_data = search(data['token_member2'], 'Hello!')
    assert returned_data == comparing_data


def test_valid_search_complex_multiple_channels_no_matches():
    '''Valid case: valid complex search with correctly returned data, no matches'''
    data = generating_data()

    message_send(data['token_flockr_owner'], data['ch_id_public1'], 'HelloO')['message_id']
    message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hell')
    message_send(data['token_flockr_owner'], data['ch_id_public2'], 'Hello, World!')['message_id']
    message_send(data['token_member1'], data['ch_id_public1'], 'Bye')['message_id']
    message_send(data['token_member1'], data['ch_id_public2'], 'Uhhh...')['message_id']
    message_send(data['token_member2'], data['ch_id_private'], 'Period.')

    comparing_data = get_comparing_data([])

    returned_data = search(data['token_flockr_owner'], 'Hello!')
    assert returned_data == comparing_data
