#this is where the authentication subsystem is defined
#this provides an alternative way for clients that are not web browsers to log in
from app import db
from app.api import bp
from app.api.auth import token_auth, basic_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required #this decorator will instruct flask-httpauth to very authentication
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token': token}


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    #clients can send a DELETE request to the /tokens url to invalidate the token
    token_auth.current_user().revoke_token()
    #uses the revoke_token() method from the User class to revoke it
    db.session.commit()
    return '', 204