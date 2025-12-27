import os
import click #this file defines custom command line commands for managing translations in the Flask app
from app import current_app #importing the app instance from the app package
from flask import Blueprint #importing Blueprint class from Flask to create a CLI blueprint

bp = Blueprint('cli', __name__, cli_group=None)

@bp.cli.group() #this decorator creates a new command group called translate
def translate():
    """Translation and localization commands."""
    pass
#this function serves as a container for related translation commands


@translate.command() #this decorator registers the init() function as a command within the translate group
@click.argument('lang') #this decorator specifies that the init command takes a single argument lang
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
            'pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')
#this function initializes a new language for translations
#it uses the pybabel command line tool to extract translatable strings from the source code
#and create a new .po file for the specified language

@translate.command() #this decorator registers the update() function as a command within the translate group
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')
#this function updates all existing language translations
#it extracts translatable strings and updates the .po files for all languages


@translate.command() #this decorator registers the compile() function as a command within the translate group
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')
#this function compiles all language translations
#it converts the .po files into .mo files that can be used by the Flask-Babel extension at runtime