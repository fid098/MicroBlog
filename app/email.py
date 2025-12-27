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

#we add a new parameter for file attachments and a parameter to control async vs sync sending(which we set to async)
def send_email(subject, sender, recipients, text_body, html_body, attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        #if an attachement(post) is provided 
        for attachment in attachments:
            #we attach each post to the email message
            msg.attach(*attachment) #*attachment expands the tuple into arguments
    if sync:
        mail.send(msg)
        #if synchronous sending is requested, send the message immediately
    else:
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
        #creates a new thread, calls send_async_email in the background
        #.start() begins execution without blocking the request 

