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
