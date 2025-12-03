#this is the flask application instance
#this creates the application object as an instance of class Flask imported from the flask package

from flask import Flask 

app = Flask(__name__)

#importing routes at the bottom avoids circular imports as routes also needs to import the app instance
from app import routes 


