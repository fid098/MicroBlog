# app/models.py — Database Models

## Purpose
Defines all database tables as SQLAlchemy ORM classes, plus the mixins that add search and API serialisation behaviour.

---

## `followers` (Association Table)
A raw SQLAlchemy table (not a model class) that implements the self-referential many-to-many follow relationship. Has two columns: `follower_id` and `followed_id`, both foreign keys to `user.id`.

---

## `PaginatedAPIMixin`
A mixin that adds `to_collection_dict()` to any model. Takes a SQLAlchemy query, a page number, and a page size, and returns a standardised dictionary with:
- `items` — the serialised objects for the current page
- `_meta` — pagination metadata (page, per_page, total_pages, total_items)
- `_links` — hypermedia links to self, next, and previous pages

---

## `User`
The main user model. Inherits from `PaginatedAPIMixin`, `UserMixin` (Flask-Login), and `db.Model`.

### Fields
| Field | Description |
|---|---|
| `id` | Primary key |
| `username` | Unique, indexed |
| `email` | Unique, indexed |
| `password_hash` | Werkzeug-hashed password |
| `about_me` | Optional bio (140 chars) |
| `last_seen` | Updated on every request |
| `last_message_read_time` | Used to calculate unread message count |
| `token` | API auth token (32 chars, unique) |
| `token_expiration` | Token expiry datetime |

### Relationships
- `posts` — one-to-many to `Post`
- `following` / `followers` — self-referential many-to-many via `followers` table
- `messages_sent` / `messages_received` — one-to-many to `Message`
- `notifications` — one-to-many to `Notification`
- `tasks` — one-to-many to `Task`

### Key Methods
- `set_password` / `check_password` — Werkzeug hashing
- `avatar(size)` — generates Gravatar URL from MD5 of email
- `follow` / `unfollow` / `is_following` — manage follow graph
- `followers_count` / `following_count` — aggregate counts
- `following_posts()` — returns a SQLAlchemy query for the personalised feed using a double-aliased JOIN on the followers table
- `get_reset_password_token` / `verify_reset_password_token` — JWT-based password reset (10 minute expiry, signed with SECRET_KEY)
- `unread_message_count()` — counts messages received after `last_message_read_time`
- `add_notification(name, data)` — upserts a notification (deletes existing with same name first)
- `launch_task(name, description, *args)` — enqueues a job on Redis Queue and creates a `Task` DB record
- `get_task_in_progress(name)` — returns a running task by name, or None
- `to_dict` / `from_dict` — API serialisation/deserialisation

---

## `SearchableMixin`
A mixin that automatically keeps an Elasticsearch index in sync with the database.

### How it works
Two SQLAlchemy session event listeners are registered globally:
- `before_commit` — snapshots `session.new`, `session.dirty`, `session.deleted` into `session._changes`
- `after_commit` — iterates `session._changes` and calls `add_to_index` or `remove_from_index` for any object that inherits `SearchableMixin`

The snapshot happens before commit because SQLAlchemy clears the session state after committing.

### `search(expression, page, per_page)`
1. Calls `query_index` to get a list of IDs and a total from Elasticsearch
2. Builds a SQLAlchemy query with `WHERE id IN (ids)`
3. Uses a SQL `CASE` statement in `ORDER BY` to preserve Elasticsearch's relevance ranking

---

## `Post`
Inherits from `SearchableMixin` and `db.Model`. `__searchable__ = ['body']` means only the post body is synced to Elasticsearch.

### Fields
- `id`, `body`, `timestamp`, `user_id`, `language`

---

## `Message`
Private messages between users.
- `sender_id` / `recipient_id` — foreign keys to `user.id`
- `author` / `recipient` — relationships back to User, disambiguated with `foreign_keys`

---

## `Notification`
Stores user notifications as JSON payloads. One record per notification type per user — `add_notification` deletes the old one before inserting a new one, so only the latest value is stored.
- `payload_json` — stored as a JSON string, retrieved with `get_data()`
- `timestamp` — float (Unix time), used for polling (`/notifications?since=...`)

---

## `Task`
Tracks background RQ jobs.
- `id` — the RQ job ID (string UUID)
- `name` — the task function name (e.g. `export_posts`)
- `complete` — set to True when the job finishes
- `get_rq_job()` — fetches the live RQ job object from Redis by ID
- `get_progress()` — reads `job.meta['progress']` from Redis; returns 100 if job has expired
