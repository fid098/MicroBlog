from flask import render_template
from app import db
from app.errors import bp

#these return the contents of their templates which is the code number 
@bp.app_errorhandler(404)  #bp is the blueprint instance and it makes the blueprint independent of the application instance
def not_found_error(error):
    return render_template('errors/404.html'), 404

#this could be invoked after a database error
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    #this resets the session to a clean state
    return render_template('errors/500.html'), 500

