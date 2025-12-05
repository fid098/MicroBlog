#this is the flask application instance
#this creates the application object as an instance of class Flask imported from the flask package

from flask import Flask 
from config import Config 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)  #this loads the configuration settings from the Config class in config.py
db = SQLAlchemy(app)  #this initializes the SQLAlchemy object with the flask app instance
migrate = Migrate(app, db)  #this sets up database migration support for the app using Flask-Migrate
login = LoginManager(app) #this initializes the LoginManager with the flask app instance

#importing routes and models at the bottom avoids circular imports as routes also needs to import the app instance
from app import routes, models 
#the database model will define the structure of the database tables used in the application

login.login_view = 'login'
#this sets the endpoint (view function name) for the login view
#when a user tries to access a protected page and is not logged in, they will be


#instead of having to set the FLASK_APP environment variable, we can register it automatically using python-dotenv
#by creating a file named .flaskenv in the project root directory with the content FLASK_APP=microblog.py
#the python-dotenv package will read this file and set the environment variable automatically when the application starts

