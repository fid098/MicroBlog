# app/main/routes.py — Main Blueprint Routes

## Purpose
The core application routes — feed, profiles, follow/unfollow, search, messaging, notifications, and post export.

## `before_request`
Runs before every request for authenticated users:
- Updates `current_user.last_seen` to the current UTC time
- Attaches a `SearchForm` instance to `g.search_form` so it's available in every template (renders the search bar in the navbar)
- Sets `g.locale` for template-level locale access

---

## Routes

### `GET/POST /` and `/index`
The home feed. Requires login.
- On POST: detects the language of the post body using `langdetect`, creates a `Post` record, commits, and redirects (Post/Redirect/Get pattern)
- On GET: paginates `current_user.following_posts()` and renders `index.html`

### `GET/POST /edit_profile`
Edit username and about_me. Pre-populates the form on GET. Validates username uniqueness on POST.

### `POST /follow/<username>` and `/unfollow/<username>`
Follow/unfollow actions. Both use `EmptyForm` for CSRF protection (no visible form fields needed).

### `GET /explore`
Shows all posts from all users, newest first. Reuses `index.html` but without the post submission form.

### `POST /translate`
Receives JSON `{text, source_language, dest_language}` from an AJAX call, calls `translate()`, returns JSON `{text: translated_text}`.

### `GET /user/<username>`
User profile page. Shows the user's posts paginated. Passes `EmptyForm` for follow/unfollow CSRF tokens.

### `GET /user/<username>/popup`
Renders a small popup card for hover-over user previews.

### `GET /search`
Calls `Post.search()` with the query from `g.search_form.q`. Returns paginated results via Elasticsearch. Redirects to `/explore` if the form is invalid.

### `GET/POST /send_message/<recipient>`
Creates a `Message` record and calls `user.add_notification()` to update the recipient's unread count badge.

### `GET /messages`
Inbox view. Resets `last_message_read_time` and sets the unread count notification to 0 on visit.

### `GET /notifications`
Polling endpoint. Accepts a `since` float (Unix timestamp) query parameter and returns a JSON array of notifications newer than that timestamp. Used by the frontend to update the message badge and task progress bar without page reloads.

### `GET /export_posts`
Checks for an in-progress export task. If none exists, calls `current_user.launch_task('export_posts', ...)` to enqueue the job. Redirects to the user's profile.

### `POST /delete_post/<id>`
Deletes a post. Validates CSRF, confirms the post belongs to the current user, deletes from both the database (which triggers Elasticsearch removal via `SearchableMixin`).
