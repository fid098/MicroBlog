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

#we add it about the User model so that the model can reference later 
#this is an association table that is used for many-to-many relationships 
#i dont declare this table as a model as it is an auxillary table that has no data other than the foreign keys 
followers = sa.Table(
    #the sa.Tabel class directly represents a database table
    'followers',
    #this is the table name 
    db.metadata,
    #this metadata is where SQLAlchemy stores the information about all the tables in the database 
    #the metadata can be obtained with db.metadata
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)

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
    #now i define my many-to-many relationship 
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        #this configures the association table that is used for this relationship
        primaryjoin=(followers.c.follower_id == id),
        #indicates the condition that links the entity to the association table 
        #followers.c.follower_id(follower_id column of the followers assocaition table)
        secondaryjoin=(followers.c.followed_id == id),
        #indicates the condition that links the association table to the user on the other side of the relationship 
        back_populates='followers')
        #back_populates connects it to "followers" property 
    #following relationship means "for the current user, find rows where my ID is follower_id and return the followed_id users"
    #if i follow alice and bob, user.following returns [alice, bob]
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
        #back_populates connects it to "following" property
    #followers relationship means "for the current user, find rows where my ID is followed_id, and return the follower_id users"
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    #follow uses add() method of the write-only relationship object 
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
    #unfollow uses remove() method of the write-only relationship object
    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query)
    #this performs a query on the following relationship to see if a given user is already included in it 
    #all write-only relationships have a select() that constructs a query that returns the elements in the relationship
    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)
    #in this type of query the results are not returned, but just their count 
    #the sa.select() specifies the sa.func.count() function from SQL alchemy to indicate that i want to get the result of a function 
    #select_from() is added with the query that needs to be counted. SQLAlchemy requires the inner query to be converted to a sub-query(.subquery()) 
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    #same as followers_count
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        #we need the user table twice and SQLAlchemy cant distinguish them so we alias(user User table as two roles)
        #users are authors of posts and users are followers of other users
        return (
            sa.select(Post)
            #this defines the entity that needs to be obtained(Post)
            .join(Post.author.of_type(Author))
            #this query gives post with its authors info
            #we join the entries in the posts tables with the Post.author relationship
            .join(Author.followers.of_type(Follower), isouter=True)
            #this query gives post with the authors and with the followers
            #isouter=True makes it a LEFT OUTER JOIN so posts are still included even if an author has no followers
            .where(sa.or_(Follower.id == self.id, Author.id == self.id))
            #shows the posts if the current user follows the author or the current user is the author 
            .group_by(Post)
            #this removes duplicates(in the case of an author having multiple followers)
            .order_by(Post.timestamp.desc())
            #this orders it so it showes the newest post first 
        )


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

