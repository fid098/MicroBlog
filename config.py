import os 

class Config:
    #this class is used to hold configuration variables/settings for the flask app, such as secret keys, database URLS, mail server credentials e.t.c
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #flask uses this for securely signing the session cookie and other security related needs
    #it looks for an environment variable named SECRET_KEY, if not found it defaults to 'you-will-never-guess'
    #The Flask-WTF extension uses it to protect web forms from CSRF attacks

    

