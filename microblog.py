from app import app, db, cli
#this imports the app variable that is a member of the app package.
#the app variable is the Flask application instance created in app/__init__.py
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'sa' : sa, 'so' : so, 'db' : db, 'User' : User, 'Post' : Post}
#this function registers a shell context processor with the Flask app
#it makes certain objects automatically available in the Flask shell
#when you run flask shell from the command line