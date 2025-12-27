from flask import current_app
from flask_mail import Message
from app import mail
from threading import Thread 
#this thread  allows the send_email() to be asynchronous(it happens in the background)
#we use a thread so the web request finishes immediately
from flask_babel import _ #import _ for translations

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
#this function now runs in the background thread, invoked in the last line of send_email().
#now the email sending function will run in the thread. 
#it still requires the app.app_context() becasue the thread is outside the main Flask request 


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    #creates a new thread, calls send_async_email in the background
    #.start() begins execution without blocking the request 

