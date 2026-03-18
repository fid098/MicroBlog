# app/email.py — Email Sending

## Purpose
Provides a single `send_email()` helper used throughout the app for all outgoing emails (password reset, post export).

## Functions

### `send_async_email(app, msg)`
Runs inside a background thread. Requires its own `app.app_context()` because it executes outside the main Flask request context.

### `send_email(subject, sender, recipients, text_body, html_body, attachments=None, sync=False)`
Builds a `flask_mail.Message` object and sends it either:
- **Async (default)** — spins up a new `Thread` running `send_async_email`. The web request returns immediately without waiting for the email to send.
- **Sync** — calls `mail.send(msg)` directly. Used by the RQ export worker which is already running in a background process, so threading is unnecessary.

### Attachments
Each attachment is a tuple of `(filename, mimetype, data)`. The `*attachment` unpacking passes these as positional arguments to `msg.attach()`.
