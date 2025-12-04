from app import app
from flask import render_template
from app.forms import LoginForm
#i import the LoginForm class from the forms module in the app package
from flask import flash, redirect, url_for
#these are imported to handle flashing messages and redirecting users to different routes


#this is a view function(handlers for the application routes)
@app.route('/')  #this is a decorator that modifies the function that follows it 
@app.route('/index')  #this binds the URL /index to the index() function
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
    return render_template('index.html', title='Home', user=user, posts=posts)
#this converts a template file (index.html) into a complete HTML page
#the render_template() function takes the name of the template file as its first argument
#additional arguments are key-value pairs that are passed to the template engine
#these key-value pairs can be used within the template to dynamically generate content

@app.route('/login', methods=['GET', 'POST'])
#this binds the URL /login to the login() function and allows both GET and POST methods
def login():
    form = LoginForm()
    #this creates an instance of the LoginForm class defined in app/forms.py
    if form.validate_on_submit():
        #this checks if the form has been submitted and if the data is valid according to the validators defined in the form class
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

