from app import app
from flask import render_template

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


