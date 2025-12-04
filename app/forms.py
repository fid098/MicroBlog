from flask_wtf import FlaskForm
#this class is imported from the flask_wtf package to create web forms in flask applications
from wtforms import StringField, PasswordField, BooleanField, SubmitField
#these classes are imported from the wtforms package to create form fields
from wtforms.validators import DataRequired 
#this validator ensures that the field is not submitted empty

class LoginForm(FlaskForm):
    #this class defines a login form that inherits from FlaskForm
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

