'''
Server wrappers for Flockr backend functions
'''

from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError
import auth
import channel
import channels
import message
import user
import other


def default_handler(err):
    '''
    Provided function
    '''
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)


# EXAMPLE ######################################################################

@APP.route("/echo", methods=['GET'])
def echo():
    '''
    Example echo function
    '''
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


# AUTH #########################################################################

@APP.route("/auth/register", methods=['POST'])
def auth_register_web():
    '''
    Wrapped auth_register
    '''
    data_in = request.get_json()
    data_out = auth.auth_register(
        data_in['email'],
        data_in['password'],
        data_in['name_first'],
        data_in['name_last']
    )
    return dumps(data_out)

@APP.route("/auth/login", methods=['POST'])
def auth_login_web():
    '''
    Wrapped auth_login
    '''
    data_in = request.get_json()
    data_out = auth.auth_login(
        data_in['email'],
        data_in['password']
    )
    return dumps(data_out)

@APP.route("/auth/logout", methods=['POST'])
def auth_logout_web():
    '''
    Wrapped auth_logout
    '''
    data_in = request.get_json()
    data_out = auth.auth_logout(
        data_in['token']
    )
    return dumps(data_out)

@APP.route("/auth/passwordreset/request", methods=['POST'])
def auth_passwordreset_request_web():
    '''
    Wrapped auth_passwordreset_request
    '''
    data_in = request.get_json('data')
    data_out = auth.auth_passwordreset_request(
        data_in['email']
    )
    return dumps(data_out)

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def auth_passwordreset_reset_web():
    '''
    Wrapped auth_passwordreset_reset_web
    '''
    data_in = request.get_json('data')
    data_out = auth.auth_passwordreset_reset(
        data_in['reset_code'],
        data_in['new_password']
    )
    return dumps(data_out)


# CHANNEL ######################################################################

@APP.route("/channel/invite", methods=['POST'])
def channel_invite_web():
    '''
    Wrapped channel_invite
    '''
    data_in = request.get_json()
    data_out = channel.channel_invite(
        data_in['token'],
        data_in['channel_id'],
        data_in['u_id']
    )
    return dumps(data_out)

@APP.route("/channel/details", methods=['GET'])
def channel_details_web():
    '''
    Wrapped channel_details
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    data_out = channel.channel_details(token, channel_id)
    return dumps(data_out)

@APP.route("/channel/messages", methods=['GET'])
def channel_messages_web():
    '''
    Wrapped channel_messages
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    data_out = channel.channel_messages(token, channel_id, start)
    return dumps(data_out)

@APP.route("/channel/leave", methods=['POST'])
def channel_leave_web():
    '''
    Wrapped channel_leave
    '''
    data_in = request.get_json()
    data_out = channel.channel_leave(
        data_in['token'],
        data_in['channel_id']
    )
    return dumps(data_out)

@APP.route("/channel/join", methods=['POST'])
def channel_join_web():
    '''
    Wrapped channel_join
    '''
    data_in = request.get_json()
    data_out = channel.channel_join(
        data_in['token'],
        data_in['channel_id']
    )
    return dumps(data_out)

@APP.route("/channel/addowner", methods=['POST'])
def channel_addowner_web():
    '''
    Wrapped channel_addowner
    '''
    data_in = request.get_json()
    data_out = channel.channel_addowner(
        data_in['token'],
        data_in['channel_id'],
        data_in['u_id']
    )
    return dumps(data_out)

@APP.route("/channel/removeowner", methods=['POST'])
def channel_removeowner_web():
    '''
    Wrapped channel_removeowner
    '''
    data_in = request.get_json()
    data_out = channel.channel_removeowner(
        data_in['token'],
        data_in['channel_id'],
        data_in['u_id']
    )
    return dumps(data_out)


# CHANNELS #####################################################################

@APP.route("/channels/list", methods=['GET'])
def channels_list_web():
    '''
    Wrapped channels_list
    '''
    token = request.args.get('token')
    data_out = channels.channels_list(token)
    return dumps(data_out)

@APP.route("/channels/listall", methods=['GET'])
def channels_listall_web():
    '''
    Wrapped channels_listall
    '''
    token = request.args.get('token')
    data_out = channels.channels_listall(token)
    return dumps(data_out)

@APP.route("/channels/create", methods=['POST'])
def channels_create_web():
    '''
    Wrapped channels_create
    '''
    data_in = request.get_json()
    data_out = channels.channels_create(
        data_in['token'],
        data_in['name'],
        data_in['is_public']
    )
    return dumps(data_out)


# MESSAGE ######################################################################

@APP.route("/message/edit", methods=["PUT"])
def message_edit_web():
    '''
    Wrapped message_edit
    '''
    data_in = request.get_json()
    data_out = message.message_edit(
        data_in["token"],
        data_in["message_id"],
        data_in["message"]
    )
    return dumps(data_out)

@APP.route("/message/send", methods=["POST"])
def message_send_web():
    '''
    Wrapped message_send
    '''
    data_in = request.get_json()
    data_out = message.message_send(
        data_in["token"],
        data_in["channel_id"],
        data_in["message"]
    )
    return dumps(data_out)

@APP.route("/message/remove", methods=["DELETE"])
def message_remove_web():
    '''
    Wrapped message_remove
    '''
    data_in = request.get_json()
    data_out = message.message_remove(
        data_in["token"],
        data_in["message_id"]
    )
    return dumps(data_out)

@APP.route("/message/react", methods=["POST"])
def message_react_web():
    '''
    Wrapped message_react
    '''
    data_in = request.get_json()
    data_out = message.message_react(
        data_in['token'],
        data_in['message_id'],
        data_in['react_id']
    )
    return dumps(data_out)

@APP.route("/message/unreact", methods=["POST"])
def message_unreact_web():
    '''
    Wrapped message_unreact
    '''
    data_in = request.get_json()
    data_out = message.message_unreact(
        data_in['token'],
        data_in['message_id'],
        data_in['react_id']
    )
    return dumps(data_out)

@APP.route("/message/pin", methods=["POST"])
def message_pin_web():
    '''
    Wrapped message_pin
    '''
    data_in = request.get_json()
    data_out = message.message_pin(
        data_in['token'],
        data_in['message_id'],
    )
    return dumps(data_out)

@APP.route("/message/unpin", methods=["POST"])
def message_unpin_web():
    '''
    Wrapped message_unpin
    '''
    data_in = request.get_json()
    data_out = message.message_unpin(
        data_in['token'],
        data_in['message_id'],
    )
    return dumps(data_out)

@APP.route("/message/sendlater", methods=["POST"])
def message_sendlater_web():
    '''
    Wrapped message_sendlater
    '''
    data_in = request.get_json()
    data_out = message.message_sendlater(
        data_in['token'],
        data_in['channel_id'],
        data_in['message'],
        data_in['time_sent']
    )
    return dumps(data_out)


# USER #########################################################################

@APP.route("/user/profile", methods=["GET"])
def user_profile_web():
    '''
    Wrapped user_profile
    '''
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    data_out = user.user_profile(token, u_id)
    return dumps(data_out)

@APP.route("/user/profile/setname", methods=["PUT"])
def user_profile_setname_web():
    '''
    Wrapped user_profile_setname
    '''
    data_in = request.get_json()
    data_out = user.user_profile_setname(
        data_in['token'],
        data_in['name_first'],
        data_in['name_last']
    )
    return dumps(data_out)

@APP.route("/user/profile/setemail", methods=["PUT"])
def user_profile_setemail_web():
    '''
    Wrapped user_profile_setemail
    '''
    data_in = request.get_json()
    data_out = user.user_profile_setemail(
        data_in['token'],
        data_in['email']
    )
    return dumps(data_out)

@APP.route("/user/profile/sethandle", methods=["PUT"])
def user_profile_sethandle_web():
    '''
    Wrapped user_profile_sethandle
    '''
    data_in = request.get_json()
    data_out = user.user_profile_sethandle(
        data_in['token'],
        data_in['handle_str']
    )
    return dumps(data_out)

# OTHER ########################################################################

@APP.route("/users/all", methods=["GET"])
def users_all_web():
    '''
    Wrapped users_all
    '''
    token = request.args.get('token')
    data_out = other.users_all(token)
    return dumps(data_out)

@APP.route("/admin/userpermission/change", methods=["POST"])
def admin_userpermission_change_web():
    '''
    Wrapped admin_userpermission_change
    '''
    data_in = request.get_json()
    data_out = other.admin_userpermission_change(
        data_in['token'],
        data_in['u_id'],
        data_in['permission_id']
    )
    return dumps(data_out)

@APP.route("/search", methods=["GET"])
def search_web():
    '''
    Wrapped search
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    data_out = other.search(token, query_str)
    return dumps(data_out)

@APP.route("/clear", methods=["DELETE"])
def clear_web():
    '''
    Wrapped clear
    '''
    other.clear()
    return {}


# PORT #########################################################################

if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
