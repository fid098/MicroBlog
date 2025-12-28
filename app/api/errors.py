#this will deal with error responses
from werkzeug.http import HTTP_STATUS_CODES #this provides a short descriptive name for each HTTP status code
from app.api import bp
from werkzeug.exceptions import HTTPException

def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    #it feeds in the status code into the error key, if the status code cannot be found, "unknown error is displayed"
    if message:
        payload['message'] = message
        #if there is a message we add it to the message key
    return payload, status_code
    
def bad_request(message):
    return error_response(400, message)

@bp.errorhandler(HTTPException) #this decorator will now be invoked to handle all errors based on the HTTPException class
def handle_exception(e):
    return error_response(e.code)