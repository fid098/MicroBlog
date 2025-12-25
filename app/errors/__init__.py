from flask import Blueprint

bp = Blueprint('errors', __name__)
#the blueprint class takes the name of the blueprint and the name of the base moduel

from app.errors import handlers
#this imports the handlers module to register the error handlers with the blueprint
#this import is placed at the end to avoid circular imports