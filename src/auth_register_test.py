'''
Backend tests for auth_register function
'''

from hashlib import sha256
import pytest
import auth
from webtoken import token_validate
from data import data_user
from other import clear
from error import InputError

# VALID EMAIL STRUCTURE

def test_register_valid_email():
    '''Valid case: valid email structure'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')

def test_register_valid_email_numbers():
    '''Valid case: valid email structure with numbers in name'''
    clear()
    auth.auth_register('name123@domain.com', 'password', 'First', 'Last')

def test_register_invalid_domain_1():
    '''Invalid case: email structure missing .com'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain', 'password', 'First', 'Last')

def test_register_invalid_domain_2():
    '''Invalid case: email structure missing domain'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name.com', 'password', 'First', 'Last')

def test_register_missing_domain():
    '''Invalid case: email structure missing domain entirely'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name', 'password', 'First', 'Last')

def test_register_missing_name():
    '''Invalid case: email structure missing name'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('@domain.com', 'password', 'First', 'Last')


# EMAIL IS NOT ALREADY BEING USED

def test_register_already_used_email():
    '''Valid case: email is already being used by another user'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'anotherpassword123', 'One', 'Two')


# CORRECTLY GENERATES NEW TOKEN

def test_register_valid_token():
    '''Valid case: token is correctly generated'''
    clear()
    user = auth.auth_register('name@domain.com', 'password', 'First', 'Last')
    assert token_validate(user['token']) == user['u_id']


# CORRECT U_ID GENERATED

def test_register_first_id():
    '''Valid case: the first u_id is generated correctly'''
    clear()
    u_id = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['u_id']
    assert u_id == 0

def test_register_second_id():
    '''Valid case: the second u_id is generated correctly'''
    clear()
    auth.auth_register('someemail@domain.com', 'password', 'First', 'Last')
    u_id = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['u_id']
    assert u_id == 1

def test_register_third_id():
    '''Valid case: the third u_id is generated correctly'''
    clear()
    auth.auth_register('someemail@domain.com', 'password', 'First', 'Last')
    auth.auth_register('anotheremail@domain.com', 'password', 'First', 'Last')
    u_id = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['u_id']
    assert u_id == 2


# CORRECT HANDLE_STR GENERATED

def test_register_first_str():
    '''Valid case: the first handle_str is generated correctly'''
    clear()
    u_id = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlast'

def test_register_second_str():
    '''Valid case: two handle_str's with identical first/lastnames generated correctly'''
    clear()
    u_id = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlast'

    u_id = auth.auth_register('anothername@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas1'

def test_register_third_str():
    '''Valid case: three handle_str's with identical first/lastnames generated correctly'''
    clear()
    u_id = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlast'

    u_id = auth.auth_register('anothername@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas1'

    u_id = auth.auth_register('yetanothername@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas2'

def test_register_tenth_str():
    '''Valid case: ten handle_str's with identical first/lastnames generated correctly'''
    clear()
    u_id = auth.auth_register('name@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlast'

    u_id = auth.auth_register('anothername@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas1'

    u_id = auth.auth_register('yetanothername@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas2'

    u_id = auth.auth_register('hello@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas3'

    u_id = auth.auth_register('hi@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas4'

    u_id = auth.auth_register('yo@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas5'

    u_id = auth.auth_register('sup@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas6'

    u_id = auth.auth_register('gday@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas7'

    u_id = auth.auth_register('yoooo@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas8'

    u_id = auth.auth_register('runningoutofnames@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstlas9'

    u_id = auth.auth_register('firstlast@domain.com', 'password', 'First', 'Last')['u_id']
    assert data_user[u_id]['handle_str'] == 'firstla10'

def test_register_long_name():
    '''Valid case: the first handle_str is generated correctly'''
    clear()
    first = 'Thisisalongname'
    last = 'Andthisisalsoalongname'
    u_id = auth.auth_register('name@domain.com', 'password', first, last)['u_id']
    assert data_user[u_id]['handle_str'] == 'thisisalongnameandth'


# PASSWORD IS VALID LENGTH

def test_register_valid_password_length():
    '''Valid case: the password is of a valid length'''
    clear()
    auth.auth_register('name@domain.com', 'correctpassword#123', 'First', 'Last')

def test_register_valid_edge_password_length():
    '''Valid case: the password 6 characters long (minimum-edge)'''
    clear()
    auth.auth_register('name@domain.com', '123456', 'First', 'Last')

def test_register_invalid_password_length():
    '''Invalid case: the password is less than 6 characters long'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'wrong', 'First', 'Last')


# FIRST NAME IS VALID LENGTH

def test_register_valid_first_length():
    '''Valid case: the first name is of a valid length'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')

def test_register_empty_first_length():
    '''Invalid case: the first name is empty'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'password', '', 'Last')

def test_register_valid_edge_first_length():
    '''Valid case: the first name is 50 characters long (maximum-edge)'''
    clear()
    first = 'Iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii'
    auth.auth_register('name@domain.com', 'password', first, 'Last')

def test_register_invalid_first_length():
    '''Invalid case: the first name is over 50 characters long'''
    clear()
    with pytest.raises(InputError):
        first = 'Iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiie'
        auth.auth_register('name@domain.com', 'password', first, 'Last')


# FIRST NAME IS ONLY VALID CHARACTERS

def test_register_valid_first_alph():
    '''Valid case: the first name is only comprised of alphabetical characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')

def test_register_valid_first_other_character1():
    '''Valid case: the first name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First-name', 'Last')

def test_register_valid_first_other_character2():
    '''Valid case: the first name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', "First'name", 'Last')

def test_register_valid_first_other_character3():
    '''Valid case: the first name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', "First.Name", 'Last')

def test_register_valid_first_other_character_combo():
    '''Valid case: the first name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', "F.Irst-n'ame", 'Last')


def test_register_invalid_first_numbers():
    '''Invalid case: the first name is a number'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'password', '1', 'Last')

def test_register_invalid_first_many_numbers():
    '''Invalid case: the first name includes numbers'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'password', '1F2i3r4s5t6', 'Last')


# LAST NAME IS VALID LENGTH

def test_register_valid_last_length():
    '''Valid case: the last name is of a valid length'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')

def test_register_empty_last_length():
    '''Invalid case: the last name is empty'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'password', 'First', '')

def test_register_valid_edge_last_length():
    '''Valid case: the last name is 50 characters long (maximum-edge)'''
    clear()
    last = 'Iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii'
    auth.auth_register('name@domain.com', 'password', 'First', last)

def test_register_invalid_last_length():
    '''Invalid case: the last name is over 50 characters long'''
    clear()
    last = 'Iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiie'
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'password', 'First', last)


# LAST NAME IS ONLY VALID CHARACTERS

def test_register_valid_last_alph():
    '''Valid case: the last name is only comprised of alphabetical characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last')

def test_register_valid_last_other_character1():
    '''Valid case: the last name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', 'Last-name')

def test_register_valid_last_other_character2():
    '''Valid case: the last name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', "L'ast")

def test_register_valid_last_other_character3():
    '''Valid case: the last name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', "La.St")

def test_register_valid_last_other_character_combo():
    '''Valid case: the last name is only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', 'First', "L'ast-na.me")

def test_register_invalid_last_numbers():
    '''Invalid case: the last name is a number'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'password', 'First', '1')

def test_register_invalid_last_many_numbers():
    '''Invalid case: the last name includes numbers'''
    clear()
    with pytest.raises(InputError):
        auth.auth_register('name@domain.com', 'password', 'First', '1L2a3s4t5')


# FIRST AND LAST NAME IS ONLY VALID CHARACTERS

def test_register_valid_full_name_other_characters():
    '''Valid case: the first and last names are only comprised of valid characters'''
    clear()
    auth.auth_register('name@domain.com', 'password', "F'irst-name", "L'ast-name")


# CORRECTLY ENCODES AND STORES PASSWORD

def test_register_hashed_pw():
    '''Valid case: the password is correctly hashed and stored in data_user'''
    clear()
    u_id = auth.auth_register('name@domain.com', 'password', "First", "Last")['u_id']
    assert data_user[u_id]['password'] != 'password'
    assert data_user[u_id]['password'] == sha256('password'.encode()).hexdigest()
