from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email

@bp.route('/login', methods=['GET', 'POST'])
#this binds the URL /login to the login() function and allows both GET and POST methods
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #if the user is already logged in (authenticated), redirect them to the index page
    form = LoginForm()
    #this creates an instance of the LoginForm class defined in app/forms.py
    if form.validate_on_submit():
        #this checks if the form has been submitted and if the data is valid according to the validators defined in the form class
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        #this queries the database for a user with the username provided in the form
        if user is None or not user.check_password(form.password.data):
            #if no such user exists or the password is incorrect, flash an error message and redirect back to the login page
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        #this logs in the user and sets a session cookie
        #the remember parameter indicates whether to remember the user across sessions
        next_page = request.args.get('next')
        #this gets the next page the user was trying to access before being redirected to the login page
        if not next_page or urlsplit(next_page).netloc != '':
        #urlsplit is used to parse the URL and check its components
        #netloc checks if the URL has a network location (domain) and if it is safe to redirect to
            next_page = url_for('main.index')
        return redirect(next_page)
        #redirect the user to the next page or the index page if no next page is specified
    return render_template('auth/login.html', title=_('Sign In'), form=form)

@bp.route('/logout')
def logout():
    logout_user()
    #this logs out the current user by removing their session cookie
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    #if the user is already logged in (authenticated), redirect them to the index page
    form = RegistrationForm()
    #this creates an instance of the RegistrationForm class defined in app/forms.py
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        #this creates a new User object with the data from the form
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
        #flash a success message and redirect the user to the login page
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        #make sure the user is not logged in
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        #if the form is valid, i look up the user by email
        if user:
            send_password_reset_email(user)
            #then send a password reset email using this helper function
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form, title=_('Reset Password'))

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        #make sure the user is not logged in
    user = User.verify_reset_password_token(token)
    #invoke the token verification method in the User class to determine who the user is
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    #if the token is valid, i show the user the resetpassword form
    if form.validate_on_submit():
        user.set_password(form.password.data)
        #use .set_password() method of User class to change the password
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)