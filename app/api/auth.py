import sqlalchemy as sa
from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth #this class implements the token authentication and Basic authentication flow from User.check_token()
from app import db
from app.models import User
from app.api.errors import error_response

token_auth = HTTPTokenAuth()
basic_auth = HTTPBasicAuth()

#we configure the two functions with the decorators

@basic_auth.verify_password
def verify_password(username, password):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user and user.check_password(password): #relies on the check_password() method form the User class
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status) #generated in the api/errors.py
    #the status arguemnt is the HTTP status code(401-standard unauthorized error)


#auth for the tokens 
@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)