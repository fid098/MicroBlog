from datetime import datetime, timezone
from typing import Optional 
import sqlalchemy as sa
#this file defines the database models used in the application
import sqlalchemy.orm as so
#importing the database instance created in app/__init__.py
#so means sqlalchemy.orm
from app import db, login
#db is the SQLAlchemy instance initialized with the Flask app
from werkzeug.security import generate_password_hash, check_password_hash
#we will use these functions to hash passwords before storing them in the database
from flask_login import UserMixin
#this mixin provides default implementations for the methods that Flask-Login expects user objects to have
from hashlib import md5
#importing hashlib to generate Gravatar URLs for user avatars


#this defines the initial database structure/schema for the application
class User(UserMixin, db.Model):
    #this represents users stored in the database, the class inherits from db.Model which is the base class for all models defined using Flask-SQLAlchemy
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    #this is the primary key column, an integer that uniquely identifies each user
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    #this column stores the username, a string up to 64 characters
    #it is indexed for faster lookups and must be unique
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    #this column stores the user's email address, a string up to 120 characters
    #it is also indexed and must be unique
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    #this column stores the hashed password for the user, a string up to 256 characters
    #it is optional and can be null
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    #this sets up a one-to-many relationship to the Post model
    #it allows access to all posts authored by this user via user.posts
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    #this column stores a brief bio or description about the user, up to 140 characters
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: 
                                datetime.now(timezone.utc))
    #this column stores the last time the user was seen (last active)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    #this method hashes the given password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    #this method checks if the given password matches the stored hashed password
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        #this method generates a Gravatar URL for the user's avatar based on their email
        #i encode the email to UTF-8 because the md5 function requires bytes
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
        #it uses the MD5 hash of the lowercase email to create a unique avatar URL
    #if some day i decide Gravatar is not good, i can change the implementation of this method without affecting other parts of the code 
    #by returning different URL or image source

    def __repr__(self):
        return '<user {}>'.format(self.username)
    #this method defines how to represent a User object as a string, useful for debugging


class Post(db.Model):
    #this represents the blog posts stored in the database 
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda : datetime.now(timezone.utc))
    #this column stores the date and time when the post was created
    #the default value is the current date and time in UTC when the post is created
    #when you pass a function as a default, sa sets the field to the value returned by the function
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    #this column is a foreign key linking to the User model, indicating which user authored the post
    author: so.Mapped[User] = so.relationship(back_populates='posts')
    #this sets up a relationship to the User model, allowing access to the author of the post
    #back_populates links this relationship to the 'posts' relationship defined in the User model
    #the user class has a new "posts" field that is initialized as a relationship to the Post class

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
#this function is used by Flask-Login to load a user from the database given their user ID
#it queries the User model using the provided ID and returns the corresponding User object

