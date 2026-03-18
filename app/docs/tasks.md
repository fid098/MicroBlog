# app/tasks.py — Background Task Worker

## Purpose
Defines functions that run as background jobs on the Redis Queue (RQ) worker process. Each function runs outside the Flask request context in a separate process.

## App Context
Because this file runs in the RQ worker (not the Flask dev server), it manually creates a Flask app instance and pushes an app context at module load time:
```python
app = create_app()
app.app_context().push()
```
This gives the task functions access to `db`, `current_app`, and email sending.

## `_set_task_progress(progress)`
Helper that updates task progress in two places simultaneously:
1. Sets `job.meta['progress']` and calls `job.save_meta()` to store the percentage in Redis
2. Loads the `Task` record from the database and calls `user.add_notification()` so the frontend can poll `/notifications` for live updates
3. Sets `task.complete = True` when progress reaches 100

## `export_posts(user_id)`
The only background task currently in the app. Triggered when a user clicks "Export your posts" on their profile.

### Flow
1. Load the user from the database
2. Set progress to 0%
3. Query all posts for that user ordered by timestamp ascending
4. Iterate through posts, collecting `body` and `timestamp` into a list, updating progress after each post
5. Send an email with the JSON data as an attachment using `send_email(..., sync=True)`
6. `finally` block always sets progress to 100%, whether the task succeeded or failed

### Error Handling
The entire task is wrapped in `try/except/finally`. If an exception occurs (e.g. email failure), the error is logged with a full stack trace via `app.logger.error`, and the `finally` block marks the task as complete so it doesn't stay stuck.
