from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

def wants_json_response():
    #this helper function compares the preference for JSON or HTML selected by the client
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']

#these return the contents of their templates which is the code number 
@bp.app_errorhandler(404)  #bp is the blueprint instance and it makes the blueprint independent of the application instance
def not_found_error(error):
    if wants_json_reponse():
        #if JSON response i import the error_reponse helper from the api blueprint and rename it as an alias
        return api_error_response(404)
    return render_template('errors/404.html'), 404

#this could be invoked after a database error
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    #this resets the session to a clean state
    if wants_json_reponse():
        return api_error_response(500)
    return render_template('errors/500.html'), 500

