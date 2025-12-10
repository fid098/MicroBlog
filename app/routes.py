from app import app, db
from flask import render_template, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm
#i import the LoginForm class from the forms module in the app package
#i import the RegistrationForm class from the forms module in the app package
from flask import flash, redirect, url_for
#these are imported to handle flashing messages and redirecting users to different routes
from flask_login import current_user, login_user, logout_user, login_required
#these are imported to manage user login sessions
from app.models import User
import sqlalchemy as sa
from urllib.parse import urlsplit
#this module defines the routes (URL endpoints) for the Flask web application
from datetime import datetime, timezone


#this is a view function(handlers for the application routes)
@app.route('/')  #this is a decorator that modifies the function that follows it 
@app.route('/index')  #this binds the URL /index to the index() function
@login_required
#this decorator ensures that only authenticated (logged-in) users can access this route
def index():
#the route() decorator in flask is used to bind a function to a URL
#when a user accesses the root URL or /index, the index() function is called and "Hello, world" is returned as the response
#the app.route() decorator takes the URL pattern as an argument and associates it with the index() function
    user = {'username': 'Miguel'}
    posts = [
        {'author': {'username': 'John'}, 
         'body': 'Beautiful day in Portland!'},
        {'author': {'username': 'Susan'}, 
         'body': 'The Avengers movie was so cool!'}
    ]
    return render_template('index.html', title='Home Page', posts=posts)
#this converts a template file (index.html) into a complete HTML page
#the render_template() function takes the name of the template file as its first argument
#additional arguments are key-value pairs that are passed to the template engine
#these key-value pairs can be used within the template to dynamically generate content

@app.route('/login', methods=['GET', 'POST'])
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
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        #this logs in the user and sets a session cookie
        #the remember parameter indicates whether to remember the user across sessions
        next_page = request.args.get('next')
        #this gets the next page the user was trying to access before being redirected to the login page
        if not next_page or urlsplit(next_page).netloc != '':
        #urlsplit is used to parse the URL and check its components
        #netloc checks if the URL has a network location (domain) and if it is safe to redirect to
            next_page = url_for('index')
        return redirect(next_page)
        #redirect the user to the next page or the index page if no next page is specified
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    #this logs out the current user by removing their session cookie
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
        return redirect(url_for('login'))
        #flash a success message and redirect the user to the login page
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
#decorator to define a route with a dynamic segment <username> which captures the username from the URL
@login_required 
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username ==username))
    #db.first_or_404 queries the database for a User with the given username
    #if no such user exists, it returns a 404 error
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    #this route displays the profile page for a user with the given username
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        #this function is executed before every request, if the user is authenticated
        #it updates the last_seen field of the current_user to the current UTC time

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required 
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        #this updates the current user's username and about_me fields with the data from the form
        db.session.commit()
        flash('Your changed have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        #this populates the form fields with the current user's data when the form is first loaded
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
        if user is None:
            flash(f'User {username} not found')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
    
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
    