from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import User


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
