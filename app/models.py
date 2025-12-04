from datetime import datetime, timezone
from typing import Optional 
import sqlalchemy as sa
#this file defines the database models used in the application
import sqlalchemy.orm as so
#importing the database instance created in app/__init__.py
#so means sqlalchemy.orm
from app import db
#db is the SQLAlchemy instance initialized with the Flask app



#this defines the initial database structure/schema for the application
class User(db.Model):
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
    