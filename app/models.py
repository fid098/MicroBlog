from datetime import datetime, timezone
from typing import Optional 
import sqlalchemy as sa
#this file defines the database models used in the application
import sqlalchemy.orm as so
#importing the database instance created in app/__init__.py
#so is the alias of sqlalchemy.orm
from app import db, login
#db is the SQLAlchemy instance initialized with the Flask app
from werkzeug.security import generate_password_hash, check_password_hash
#we will use these functions to hash passwords before storing them in the database
from flask_login import UserMixin
#this mixin provides default implementations for the methods that Flask-Login expects user objects to have
from hashlib import md5
#importing hashlib to generate Gravatar URLs for user avatars
from time import time 
import jwt #imports JSON web tokens for password reset functionality
from app.search import add_to_index, remove_from_index, query_index
# we import the search functions defined in app/search.py to integrate full-text search capabilities with our models
from flask import current_app
import json
from time import time 
import redis 
import rq
from flask import url_for
from datetime import timedelta
import secrets



# we add it above the User model so that the model can reference later
# this is an association table that is used for many-to-many relationships
# i dont declare this table as a model as it is an auxillary table that has no data other than the foreign keys
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


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs): #it takes an sql query, a page number and a page size
        #the to_collection_dict method produces a dictionary with the user collection(collection of user data) representation
        #including the items, _meta and _links sections
        resources = db.paginate(query, page=page, per_page=per_page, error_out=False)
        #this obtains a page worth of items
        data = {
          'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                #includes a self reference and links to the next and previous pages
                #couldve been made more complicated by using url_for('api.get_users',..) for self
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs), #takes the endpoint argument for the view function that needs to be used in the url_for calls
                                #also captures any additional route arguments in kwargs
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

#this defines the initial database structure/schema for the application
class User(PaginatedAPIMixin, UserMixin, db.Model):
    __tablename__ = "user"
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
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
           current_app.config['SECRET_KEY'], algorithm='HS256')
    #this function returns a JWT token as a string which is generated directly by the jwt.encode function
    #the payload data {'reset_password': self.id, 'exp': time() + expires_in}, a dic that stores the id and expiring time 
    # current_app.config['SECRET_KEY'] used to sign the token(to ensure it cant be tampered with)
    # algorithm specifies the signing algorithm 

    @staticmethod
    #doesnt take the instance of the class, it can be involked directly from the class 
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return 
        return db.session.get(User, id)
    #this method takes a token and attempts to decode it by using jwt.decode.
    #if the token cannot be validated or expired an exception is raised to return None 
    #if the token is valid, the value of the reset_password key from the token's payload is the ID of the user so i can load the user and return it 

    last_message_read_time: so.Mapped[Optional[datetime]]
    #this whill have the last time the user visited the messages page
    messages_sent: so.WriteOnlyMapped['Message'] = so.relationship(foreign_keys='Message.sender_id', back_populates='author')
    messages_recieved: so.WriteOnlyMapped['Message'] = so.relationship(foreign_keys='Message.recipient_id', back_populates='recipient')
    def unread_message_count(self):
        #uses the last_message_read field to return how many unread messages the user has
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        query = sa.select(Message).where(Message.recipient == self, Message.timestamp > last_read_time)
        return db.session.scalar(sa.select(sa.func.count()).select_from(query.subquery()))
    notifications: so.WriteOnlyMapped['Notification'] = so.relationship(back_populates='user')
    def add_notification(self, name, data):
        db.session.execute(self.notifications.delete().where(Notification.name == name))
        #this adds a notification and if a noti with the same name already exists, it is removed first
        #the delete() method removes all elements without loading them.
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n
    tasks: so.WriteOnlyMapped['Task'] = so.relationship(back_populates='user')
    #add a relationship between the user and the task
    def launch_task(self, name, description, *args, **kwargs):
        #takes the name of the task function, the description and additional arguments to pass to the task 
        rq_job = current_app.task_queue.enqueue(f'app.tasks.{name}', self.id, *args, **kwargs)
        #adds the job to the redis queue created in __init__, taking the name(path), the user id and other arguments
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        #then we create a task database record, using the RQ's job id
        db.session.add(task)
        #then we add that task to the database session
        return task #return the task object
    def get_tasks_in_progress(self):
        query = self.tasks.select().where(Task.complete == False)
        #we query all tasks for this user and filter to only incomplete tasks and returns them as a list
        return db.session.scalars(query)
    def get_task_in_progress(self, name):
        query = self.tasks.select().where(Task.name == name, Task.complete == False)
        #finds a specific task by name if it is still in progress and returns that single task or None
        return db.session.scalar(query)
    def posts_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.posts.select().subquery())
        return db.session.scalar(query)

    def to_dict(self, include_email=False):
        #to_dict() converts the user object to a python representaion then to a JSON
        #the current user's dictionary is generated and returned
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.replace(
                tzinfo=timezone.utc).isoformat() if self.last_seen else None, #we use the ISO 8601 format for the date and time fields
            'about_me': self.about_me,
            'post_count': self.posts_count(), #use helper function above to calculate
            'follower_count': self.followers_count(), #use helper function above to calculate
            'following_count': self.following_count(), #use helper function above to calculate
            '_links': {
                #for the hypermedia links, url_for generates urls pointing to the viewfunctions in api/users.py and pass the id arguments
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'following': url_for('api.get_following', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            #in the case of the email being included(user requesting their own data)
            #add a new email key and value
            data['email'] = self.email
        return data
    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            #impoer the fields which the user can set which are these ones
            if field in data:
                #for each field, check if there is a value provided in the data argument
                setattr(self, field, data[field])
                #if there is, we set the new value in the corresponding attribute for the object
        if new_user and 'password' in data:
            #if this is a registration and a password is included
            self.set_password(data['password'])
            #use the set_password method to create a password hash
    token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32), index=True, unique=True)
    #add a token attribute and make it unique and indexed since its going to be used to search the database
    token_expiration: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime)
    #holds the date and time at which the token expires
    def get_token(self, expires_in=3600):
        #returns the token for the user
        now = datetime.now(timezone.utc)
        #before creation, it checks if the currently assigned token has at least a minute left before expiration, in that case the existing token is returned
        if self.token and self.token_expiration and self.token_expiration.replace(tzinfo=timezone.utc) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        #this generates the token
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    def revoke_token(self):
        self.token_expiration = datetime.now(timezone.utc) - timedelta(seconds=1)
        #this makes the token invalid by setting the expiration date to one second before the current time
    @staticmethod
    def check_token(token):
        #takes a token input and returns the user the token belongs to 
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None #if invalid or expired
        return user

class SearchableMixin(object):
    @classmethod #class method decorator that indicates the method is bound to the class and not the instance
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        #this calls the query_index function defined in app/search.py to perform the search and takes these parameters:
        #cls.__tablename__: the name of the database table associated with the model class
        if total == 0 or not ids:
            empty_query = sa.select(cls).where(sa.false())
            return db.session.scalars(empty_query), 0
            #if no results are found, return an empty query
        when = [] #this will hold the ordering conditions
        for i in range(len(ids)):
            when.append((ids[i], i)) #this creates a list of tuples mapping each ID to its position in the search results by iterating over the list of IDs and appending a tuple (id, index) to the when list
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        #this constructs a SQLAlchemy query to retrieve the model instances corresponding to the search results
        #it selects all columns from the model's table where the ID is in the list of IDs returned by the search
        #the order_by clause uses a CASE statement to preserve the order of the search results based
        return db.session.scalars(query), total
    #this executes the constructed query and returns the results as a list of model instances along with the total number of matches found
    
    @classmethod
    def before_commit(cls, session):
        session._changes = { #session._changes is a custom attribute added to the session object to track changes made during the session
            'add': list(session.new), #list of new objects to be added
            'update': list(session.dirty), #list of modified objects
            'delete': list(session.deleted) #list of deleted objects
        }
    #this method is called before a database commit to track changes made to the session

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        #this method is called after a database commit to perform any necessary actions based on the changes made during the session
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        #this updates the search index for updated objects
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        #this removes deleted objects from the search index
        session._changes = None
        #clears the tracked changes after processing

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__,obj)
    #this method reindexes all instances of the model class in the search index

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
#this sets up an event listener that calls the before_commit method of SearchableMixin before a database commit
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
#this sets up an event listener that calls the after_commit method of SearchableMixin after a database commit

class Post(SearchableMixin, db.Model):
    __tablename__ = "post"
    #searchablemixin is added as a base class to enable full-text search capabilities for the Post model
    __searchable__ = ['body'] #this indicates that the body field of the Post model should be indexed for full-text search
    #this represents the blog posts stored in the database 
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    #this column stores the date and time when the post was created
    #the default value is the current date and time in UTC when the post is created
    #when you pass a function as a default, sa sets the field to the value returned by the function
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    #this column is a foreign key linking to the User model, indicating which user authored the post
    author: so.Mapped[User] = so.relationship(back_populates='posts')
    #this sets up a relationship to the User model, allowing access to the author of the post
    #back_populates links this relationship to the 'posts' relationship defined in the User model
    #the user class has a new "posts" field that is initialized as a relationship to the Post class
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))
    #this column stores the language of the post, represented as a string (e.g., 'en', 'es')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
#this function is used by Flask-Login to load a user from the database given their user ID
#it queries the User model using the provided ID and returns the corresponding User object


class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    sender_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    recipient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    author: so.Mapped[User] = so.relationship(foreign_keys='Message.sender_id', back_populates='messages_sent')
    recipient: so.Mapped[User] = so.relationship(foreign_keys='Message.recipient_id', back_populates='messages_recieved')

    def __repr__(self):
        return '<Message {}>'.format(self.body)

class Notification(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    timestamp: so.Mapped[float] = so.mapped_column(index=True, default=time)
    #timestamp gets its default value from the time.time() function
    payload_json: so.Mapped[str] = so.mapped_column(sa.Text)
    #payload is going to be different for each type of notification, so i write it as a JSON string
    #this will allow me to write lists, dictionaries or single values.
    user: so.Mapped[User] = so.relationship(back_populates='notifications')

    def get_data(self):
        return json.loads(str(self.payload_json))
    #getter function to get the json string file

class Task(db.Model):
    #add a task model with columns 
    id: so.Mapped[str] = so.mapped_column(sa.String(36), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))
    complete: so.Mapped[bool] = so.mapped_column(default=False)

    user: so.Mapped[User] = so.relationship(back_populates='tasks')
    #relationship back to user

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
            #job object that loads the RQ job from redis, uses the tasks id and uses app's redic connection
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            #if redis is down, or job is expired, returns none
            return None
        return rq_job
        #other wise return the job object

    def get_progress(self):
        job = self.get_rq_job()
        #we get the result from the above function, if job is None then job expired, then must be complete so we return 100
        return job.meta.get('progress', 0) if job is not None else 100
        #otherwise return the progress from job.meta 