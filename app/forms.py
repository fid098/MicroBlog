from flask_wtf import FlaskForm
#this class is imported from the flask_wtf package to create web forms in flask applications
from wtforms import StringField, PasswordField, BooleanField, SubmitField
#these classes are imported from the wtforms package to create form fields
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
#these are imported to validate form input data, such as ensuring required fields are filled, email format is correct, etc.
#this validator ensures that the field is not submitted empty
from app import db
from app.models import User
import sqlalchemy as sa
from wtforms import TextAreaField #importing TextAreaField for multi-line text input
from wtforms.validators import Length #importing Length validator to limit the length of input text
from flask_babel import _, lazy_gettext as _l #importing _ and _l for translations




class LoginForm(FlaskForm):
    #this class defines a login form that inherits from FlaskForm
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    #this class defines a registration form that inherits from FlaskForm
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    #this field requires the user to enter the same password as in the password field
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        #this method checks if the username already exists in the database
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))
        #if the username is already taken, a ValidationError is raised

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        #this method checks if the email already exists in the database
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))      
        #if the email is already registered, a ValidationError is raised

class EditProfileForm(FlaskForm):
    #this class defines a form for editing user profiles
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    #TextAreaField is a multiline box for user to enter a brief bio or description, limited to 140 characters
    submit = SubmitField(_l('Submit'))       

    #constructor (__init__)
    def __init__(self, original_username, *args, **kwargs):
        #takes an additional argument original_username and saves it in self.original_username for validation later 
        super().__init__(*args, **kwargs)
        #*args and **kwards are passed to FlaskForm's constructor, so the form still works normally 
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))