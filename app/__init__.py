#this is the flask application instance
#this creates the application object as an instance of class Flask imported from the flask package

from flask import Flask 
from config import Config 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging #flask uses this package to write its logs and has the ability to send logs by email
from logging.handlers import SMTPHandler #SMTPHandler instance is added to the flask logger object 
from logging.handlers import RotatingFileHandler
import os 
from flask_mail import Mail 


#we create the extension
db = SQLAlchemy() 
migrate = Migrate() 
login = LoginManager() 
mail = Mail() 

#create the flask app
app = Flask(__name__)
app.config.from_object(Config)  #this loads the configuration settings from the Config class in config.py


#then initialize each extension with app and db when needed 
db.init_app(app)  #this initializes the SQLAlchemy object with the flask app instance
migrate.init_app(app, db)  #this sets up database migration support for the app using Flask-Migrate
login.init_app(app) #this initializes the LoginManager with the flask app instance
mail.init_app(app) #we create an object of the class Mail


login.login_view = 'login'
#this sets the endpoint (view function name) for the login view
#when a user tries to access a protected page and is not logged in, they will be



if not app.debug:
    #we enable the email logger with running without debug mode 
    if app.config['MAIL_SERVER']:
        #and also when the email server exists in the config file 
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
        #this code above creates  SMTPHandler instance, sets its level so that it only reports errors 
        #and finally attaches it to the app.logger object from flask 
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')
        #look more into the code above 


#importing routes, errors and models at the bottom avoids circular imports as routes also needs to import the app instance
from app import routes, models , errors, app
#the database model will define the structure of the database tables used in the application


#instead of having to set the FLASK_APP environment variable, we can register it automatically using python-dotenv
#by creating a file named .flaskenv in the project root directory with the content FLASK_APP=microblog.py
#the python-dotenv package will read this file and set the environment variable automatically when the application starts

