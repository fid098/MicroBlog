from app.api import bp
#this stores the user API resources in form of view functions
from app.models import User
from app import db
import sqlalchemy as sa
from flask import request, url_for
from flask import abort
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/users/<int:id>', methods=["GET"])
@token_auth.login_required #we protect the API routes with tokens
def get_user(id):
    return db.get_or_404(User, id).to_dict()
    #recieves the id
    #returns the model if it exists or aborts and returns a 404 error to the client
    #to_dict() method to generate a dictionary with the resource representation for the user

@bp.route('/users', methods=["GET"])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)#caps it at 100(min())
    #extract page and per_page from the query string of the request
    #using defaults of 1 and 10 if they are not defined
    return User.to_collection_dict(sa.select(User), page, per_page,
                                   'api.get_users')
    #pass page and per_page into the method along with the a query that returns all users(sa.select(User))
    #api.get_users is the endpoint name that are needed for the links


@bp.route('/users/<int:id>/followers', methods=["GET"])
@token_auth.login_required
def get_followers(id):
    #specific to the user so it takes an id argument in the url
    user = db.get_or_404(User, id)
    #get the user from the db
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(user.followers.select(), page, per_page, 'api.get_followers', id=id)

@bp.route('/users/<int:id>/following', methods=['GET'])
@token_auth.login_required
def get_following(id):
    user = db.get_or_404(User, id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(user.following.select(), page, per_page,
                                   'api.get_following', id=id)

@bp.route('/users', methods=['POST'])
#the decorator is not added to this view function since the user that will request the token needs to be created first
def create_user():
    data = request.get_json() or {} #.get_json() extracts the json body from the request and returns it as a python structure
    #the request accepts a user representaion in json format from the client in the request body
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if db.session.scalar(sa.select(User).where(User.username == data['username'])):
        return bad_request('please use a different username')
    if db.session.scalar(sa.select(User).where(User.email == data['email'])):
        return bad_request('please use a different email address')
    #once the user is validated
    user = User() #i create a user object and add it to the database
    user.from_dict(data, new_user=True) #password field is now accepted
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201, {'Location': url_for('api.get_user', id=user.id)}
    #i return the representation of the new user, the status code(201), and the location header which is set to url of the new resource

@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id != id:
        abort(403) #this prevents a user from trying to modify another users account
    user = db.get_or_404(User, id)
    #recieve a user id as part of the url, returns a 404 if not found
    data = request.get_json()
    if 'username' in data and data['username'] != user.username and db.session.scalar(sa.select(User).where(User.username == data['username'])):
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and db.session.scalar(sa.select(User).where(User.email == data['email'])):
        return bad_request('please user a different email address')
    #once the data is validated
    user.from_dict(data, new_user=False) #import all the data provided by the client 
    db.session.commit() #commit the change made to the database
    return user.to_dict() #return an updated user representation to the user