from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread 
#this thread  allows the send_email() to be asynchronous(it happens in the background)
#we use a thread so the web request finishes immediately

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    
    # Force an application context so we can render templates and use flask mail 
    with app.app_context():
        text_body = render_template(
            'email/reset_password.txt',
            user=user,
            token=token
        )
        html_body = render_template(
            'email/reset_password.html',
            user=user,
            token=token
        )
    
        #calls the helper function send_email that sends the email asynchronously.
        send_email(
        subject='[Microblog] Reset Your Password',
        sender=app.config['ADMINS'][0]
        #uses the first email from admins as the sender 
        ,recipients=[user.email]
        #sends the email to the users email 
        ,text_body=text_body,
        html_body=html_body
    )

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
    Thread(target=send_async_email, args=(app, msg)).start()
    #creates a new thread, calls send_async_email in the background
    #.start() begins execution without blocking the request 

