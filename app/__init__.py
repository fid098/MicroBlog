#this is the flask application instance
#this creates the application object as an instance of class Flask imported from the flask package

import logging #importing the logging module to set up error logging
from logging.handlers import SMTPHandler, RotatingFileHandler #importing necessary modules for logging
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from config import Config #importing the Config class from config
from flask_babel import Babel, lazy_gettext as _l
#Flask-Babel is an extension that adds i18n and l10n support to Flask applications, making it easier to translate the app into different languages and format dates, times, and numbers according to the user's locale.
import os 
from elasticsearch import Elasticsearch

def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    #this uses the attribute of Flask's request object called accept_languages. 
    #this provides an interface to work with the Accept-Language header that clients send with a request.
    #the header specifies the client language and locale preferences as a weighted list
    #the best_match method returns the most appropriate language based on the client's preferences and the available languages in the app configuration
    #return 'es' #for testing purposes, we force the locale to spanish


#we create the extension
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):
    #function to create the flask app instance
    app = Flask(__name__)
    app.config.from_object(config_class)  #this loads the configuration settings from the Config class in config.py
    #then initialize each extension with app and db when needed

    #then initialize each extension with app and db when needed 
    db.init_app(app)  #this initializes the SQLAlchemy object with the flask app instance
    migrate.init_app(app, db)  #this sets up database migration support for the app using Flask-Migrate
    login.init_app(app) #this initializes the LoginManager with the flask app instance
    mail.init_app(app) #we create an object of the class Mail
    moment.init_app(app) #we create an object of the class Moment
    babel = Babel(app, locale_selector=get_locale) #the local_selector is set to the function get_locale that is invoked for each request. 
    #didnt continue implementation but will go back to continue if needed 


    es_url = os.environ.get('ELASTICSEARCH_URL') #getting the elasticsearch url from environment variable
    if es_url: #if the elasticsearch url exists
        #create an instance of the Elasticsearch client and attach it to the app instance
        ca_path = os.environ.get("ELASTICSEARCH_CA_CERT")  #getting the path to the CA certificate from environment variable
        app.elasticsearch = Elasticsearch([es_url], basic_auth=( 
            os.environ.get("ELASTICSEARCH_USER"), os.environ.get("ELASTICSEARCH_PASSWORD")
        ), ca_certs=ca_path,) #getting the elasticsearch user, password and ca_certs from environment variables
    else:
        app.elasticsearch = None #if the elasticsearch url does not exist, set the app.elasticsearch attribute to None

    #when a blueprint is registered with the app, all the routes,view functions, static files and error handlers defined in that blueprint become part of the application
    from app.errors import bp as errors_bp #importing the errors blueprint from app/errors/__init__.py
    app.register_blueprint(errors_bp) #registering the errors blueprint with the flask app instance

    from app.auth import bp as auth_bp #importing the auth blueprint from app/auth/__init__.py 
    app.register_blueprint(auth_bp, url_prefix='/auth') #registering the auth blueprint with the flask app instance
    #the url_prefix argument specifies that all routes defined in the auth blueprint will be prefixed with /auth

    from app.main import bp as main_bp #importing the main blueprint from app/main/__init__.py
    app.register_blueprint(main_bp) #registering the main blueprint with the flask app instance

    from app.cli import bp as cli_bp #importing the cli blueprint from app/cli.py
    app.register_blueprint(cli_bp) #registering the cli blueprint with the flask app instance

    
    if not app.debug and not app.testing:
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
    return app


#importing routes, errors and models at the bottom avoids circular imports as routes also needs to import the app instance
from app import models
#the database model will define the structure of the database tables used in the application


#instead of having to set the FLASK_APP environment variable, we can register it automatically using python-dotenv
#by creating a file named .flaskenv in the project root directory with the content FLASK_APP=microblog.py
#the python-dotenv package will read this file and set the environment variable automatically when the application starts

