import time
import sys
import json
from flask import render_template
from rq import get_current_job
from app import create_app, db
from app.models import User, Post, Task
from app.email import send_email
import sqlalchemy as sa

# Create app context for the worker by initializing the flask app
app = create_app() #create an instance
app.app_context().push()  #add context from microblog.py

def _set_task_progress(progress):
    """Helper function to update task progress"""
    job = get_current_job() #get current job context
    if job:
        job.meta['progress'] = progress #store progess in redis
        job.save_meta()  #save to redis
        task = db.session.get(Task, job.get_id())  #load the task from database
        if task:  # Make sure task exists
            task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                         'progress': progress}) #we send a notification to the user
            if progress >= 100: #if task complete
                task.complete = True
            db.session.commit()

def export_posts(user_id):
    """Background task to export user's posts to JSON and email them"""
    #try/except/finally runs in RQ worker not flask so flask wont catch errors here so we have to handle them properly
    try:
        print(f"Starting export for user {user_id}")  # for Debugging
        user = db.session.get(User, user_id) #load the user from the database
        
        if not user:
            print(f"User {user_id} not found!")  #if its not the user return
            return
        
        print(f"Found user: {user.username}")  #if the user is found start the task
        _set_task_progress(0)
        
        data = [] #list to collect post data
        i = 0  #counter for progress calculation
        
        # Count total user posts
        total_posts = db.session.scalar(sa.select(sa.func.count()).select_from(
            user.posts.select().subquery()))
        
        print(f"Total posts to export: {total_posts}") 
        
        if total_posts == 0:
            print("No posts to export")
            _set_task_progress(100)  #if no posts to export mark the task as done and return
            return
        
        # Export each post
        for post in db.session.scalars(user.posts.select().order_by(
                Post.timestamp.asc())): #order the posts from older first
            data.append({
                'body': post.body,
                'timestamp': post.timestamp.isoformat() + 'Z'
            })  #add the post to the collection, post and timestamp
            print(f"Exported post {i+1}/{total_posts}")
            #time.sleep(2)  # Reduced from 5 to 2 seconds for faster testing
            i += 1 #increment the counter
            _set_task_progress(100 * i // total_posts) #update the progress of the task with a percentage

        print(f"Finished exporting {len(data)} posts")
        
        # Send email with data
        print("Sending email...")
        send_email(
            '[Microblog] Your blog posts',
            sender=app.config['ADMINS'][0], 
            recipients=[user.email],
            text_body=render_template('email/export_posts.txt', user=user),
            html_body=render_template('email/export_posts.html', user=user),
            attachments=[('posts.json', 'application/json',
                          json.dumps({'posts': data}, indent=4))],
            sync=True)
        print("Email sent successfully")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        _set_task_progress(100) #marks task as done even though it failed
        app.logger.error('Unhandled exception', exc_info=sys.exc_info()) #then we log the error with the full stack trace(sys.exc_info())
    finally: #always runs success or failure
        _set_task_progress(100) #mark task as done
        print("Task completed") 
