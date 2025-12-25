import os 
basedir = os.path.abspath(os.path.dirname(__file__))
#this gets the absolute path of the directory where this config.py file is located


class Config:
    #this class is used to hold configuration variables/settings for the flask app, such as secret keys, database URLS, mail server credentials e.t.c
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #flask uses this for securely signing the session cookie and other security related needs
    #it looks for an environment variable named SECRET_KEY, if not found it defaults to 'you-will-never-guess'
    #The Flask-WTF extension uses it to protect web forms from CSRF attacks
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'app.db')
    )
    #this sets the database connection URI for SQLAlchemy
    #it first checks for an environment variable named DATABASE_URL
    #if not found it defaults to a SQLite database file named app.db located in the same directory as this config.py file


    #first we add the email server details to the config file 
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    #email server credentials by default are not used but can be provided if needed. 
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    #mail server and port are a boolean flag to enable encrypted connections
    #the email server port can be given in an environment variable but if not set, the standard port 25 is used 
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #optional username and password
    ADMINS = ['fidel.ehirim1@gmail.com'] #list of email addresses that will recieve error reports
    #when the app is deployed on a production server, we can configure Flask to email me after an error with the stack trace of the error 
    #the five configuration variables are sourced from their environment variable counterparts 

    POSTS_PER_PAGE = 3
    #i add this configuration item, it determines how many itesm will be displayed per page 
    #this can be changed to accomodate more posts in the future 

    SERVER_NAME = 'localhost:5000'
    PREFERRED_URL_SCHEME = 'http'

    LANGUAGES = ['en_US', 'en_GB', 'es', 'tur', 'fr', 'de', 'zh_CN']
    #holds the available languages that the application can be translated to 

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    MS_TRANSLATOR_REGION = os.environ.get('MS_TRANSLATOR_REGION') or 'global'
    #this configuration variable holds the API key for the Microsoft Translator service
    #it is sourced from an environment variable named MS_TRANSLATOR_KEY

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') or None
    #this configuration variable holds the URL for the Elasticsearch server
    #it is sourced from an environment variable named ELASTICSEARCH_URL

