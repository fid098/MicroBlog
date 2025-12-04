#this is the flask application instance
#this creates the application object as an instance of class Flask imported from the flask package

from flask import Flask 
from config import Config 

app = Flask(__name__)
app.config.from_object(Config)  #this loads the configuration settings from the Config class in config.py

#importing routes at the bottom avoids circular imports as routes also needs to import the app instance
from app import routes 

#instead of having to set the FLASK_APP environment variable, we can register it automatically using python-dotenv
#by creating a file named .flaskenv in the project root directory with the content FLASK_APP=microblog.py
#the python-dotenv package will read this file and set the environment variable automatically when the application starts

