# app/__init__.py — Application Factory

## Purpose
Creates and configures the Flask application instance using the **application factory pattern**. All extensions and blueprints are registered here.

## Extensions Initialised
| Extension | Purpose |
|---|---|
| SQLAlchemy | ORM — database models and queries |
| Flask-Migrate | Database schema migrations |
| Flask-Login | User session management |
| Flask-Mail | Email sending |
| Flask-Moment | Timestamp formatting in templates |
| Flask-Babel | Internationalisation and translations |

## Key Setup Steps

### Locale Detection
`get_locale()` reads the `Accept-Language` header from each request and returns the best matching language from `LANGUAGES` in config. This is passed to Babel so every request renders in the user's preferred language.

### Redis & Task Queue
A Redis connection is created from `REDIS_URL` and attached to the app as `app.redis`. A Redis Queue named `microblog-tasks` is created on that connection and attached as `app.task_queue`. Both are accessible anywhere via `current_app`.

### Elasticsearch
If `ELASTICSEARCH_URL` is set, an Elasticsearch client is created with optional basic auth and CA certificate for HTTPS. If no URL is configured, `app.elasticsearch` is set to `None` — all search functions check for this and gracefully return empty results.

### Blueprint Registration
Four blueprints are registered:
- `errors` — 404 and 500 error handlers (no prefix)
- `auth` — login, register, password reset (`/auth`)
- `main` — feed, profiles, search, messaging (no prefix)
- `api` — REST API endpoints (`/api`)
- `cli` — translation management CLI commands

### Logging
In production (non-debug, non-testing mode):
- Errors are emailed to `ADMINS` via `SMTPHandler`
- If `LOG_TO_STDOUT` is set (Heroku), logs go to stdout
- Otherwise logs rotate in `logs/microblog.log` (max 10KB, 10 backups)
