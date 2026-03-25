import time
import sys
import json
from flask import render_template
from rq import get_current_job
from app import create_app, db
from app.models import User, Post, Task
from app.email import send_email
import sqlalchemy as sa

# Worker runs outside Flask, so we create and push an app context manually
app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = db.session.get(Task, job.get_id())
        if task:
            task.user.add_notification('task_progress', {
                'task_id': job.get_id(),
                'progress': progress
            })
            if progress >= 100:
                task.complete = True
            db.session.commit()


def export_posts(user_id):
    # try/except/finally required here — RQ worker won't propagate errors to Flask
    try:
        print(f"Starting export for user {user_id}")
        user = db.session.get(User, user_id)

        if not user:
            print(f"User {user_id} not found!")
            return

        print(f"Found user: {user.username}")
        _set_task_progress(0)

        data = []
        i = 0

        total_posts = db.session.scalar(sa.select(sa.func.count()).select_from(
            user.posts.select().subquery()))

        print(f"Total posts to export: {total_posts}")

        if total_posts == 0:
            print("No posts to export")
            _set_task_progress(100)
            return

        for post in db.session.scalars(user.posts.select().order_by(Post.timestamp.asc())):
            data.append({
                'body': post.body,
                'timestamp': post.timestamp.isoformat() + 'Z'
            })
            print(f"Exported post {i+1}/{total_posts}")
            i += 1
            _set_task_progress(100 * i // total_posts)

        print(f"Finished exporting {len(data)} posts")
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
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)
        print("Task completed")
