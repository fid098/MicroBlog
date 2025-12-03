from app import app

#this is a view function(handlers for the application routes)
@app.route('/')  #this is a decorator that modifies the function that follows it 
@app.route('/index')  #this binds the URL /index to the index() function
def index():
    return "Hello, world"
#the route() decorator in flask is used to bind a function to a URL
#when a user accesses the root URL or /index, the index() function is called and "Hello, world" is returned as the response
#the app.route() decorator takes the URL pattern as an argument and associates it with the index() function

