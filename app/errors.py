from flask import render_template 
from app import app, db

#these return the contents of their templates which is the code number 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

#this could be invoked after a database error
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    #this resets the session to a clean state
    return render_template('500.html'), 500

