# MicroBlog

A microblogging web application built with Flask, covering session and token
authentication, a REST API, full-text search, background job processing, and a
containerised deployment.

## Features

**Users and authentication**
- Registration and login with session-based authentication (Flask-Login)
- Password hashing via Werkzeug
- Password reset by email using time-limited JWTs
- Token authentication for API clients, with expiry and revocation
- Profile pages with Gravatar avatars and follow/unfollow

**Posts and timeline**
- Create posts, with a personalised timeline of followed users' posts
- Pagination throughout
- Automatic language detection on posts (`langdetect`)
- On-demand translation of posts via the Microsoft Translator API
- Export a user's posts to JSON, delivered by email as a background job

**REST API**
- User, follower, and following endpoints under `/api`
- Token auth via `POST /api/tokens`, revocation via `DELETE /api/tokens`
- Paginated collections with `_meta` and `_links` (HATEOAS-style)
- Structured JSON error responses with correct HTTP status codes

**Search**
- Elasticsearch full-text search over post bodies
- Index kept in sync through SQLAlchemy commit hooks
- Degrades gracefully to no search when `ELASTICSEARCH_URL` is unset

**Private messaging**
- One-to-one messages with unread counters
- Unread counts and job progress delivered by a notification polling endpoint

**Background jobs**
- Redis Queue (RQ) worker for asynchronous work
- Job progress tracked in Redis job metadata and surfaced to the browser
- Task records persisted in the database

**Internationalisation**
- Flask-Babel with locale selected from the browser `Accept-Language` header
- English and Spanish catalogs (`app/translations/`)
- Localised relative timestamps via Flask-Moment

**Deployment**
- Docker image running Gunicorn as an unprivileged user
- `docker compose` stack: app, RQ worker, PostgreSQL, Redis, Elasticsearch
- Migrations applied automatically on container start
- Configuration entirely via environment variables

## Tech stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.12 |
| Framework | Flask 3, Jinja2 |
| ORM / migrations | SQLAlchemy 2, Flask-SQLAlchemy, Flask-Migrate (Alembic) |
| Auth | Flask-Login, Flask-HTTPAuth, PyJWT |
| Database | PostgreSQL (production), SQLite (local default) |
| Search | Elasticsearch 8 |
| Jobs | Redis, RQ |
| Frontend | Bootstrap 5, vanilla JavaScript |
| Server | Gunicorn |
| Container | Docker, Docker Compose |

## Quick start with Docker

The fastest path to a running stack — no local Python required.

```bash
git clone https://github.com/<your-username>/microblog.git
cd microblog
docker compose up --build
```

The app is served at http://localhost:5000. Migrations run automatically on
startup. Email and translation features stay inert unless you supply the
relevant variables (see [Configuration](#configuration)).

## Local development

```bash
git clone https://github.com/<your-username>/microblog.git
cd microblog

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements-dev.txt
flask db upgrade
flask translate compile   # builds the .mo catalogs
flask run
```

This uses a local SQLite database at `app.db`. Redis and Elasticsearch are
optional; without them, search returns no results and background jobs cannot be
queued, but the rest of the app works.

To run background jobs locally, start Redis and then a worker:

```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
./start_worker.sh
```

To enable search, start Elasticsearch and set `ELASTICSEARCH_URL`:

```bash
docker run -d --name elasticsearch -p 9200:9200 \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.1
```

Posts are indexed automatically on commit. To rebuild the index from scratch:

```bash
flask shell
>>> Post.reindex()
```

## Configuration

Create a `.env` file in the project root. Every variable is optional; defaults
are shown where they exist.

```ini
SECRET_KEY=change-me                       # required in production
DATABASE_URL=sqlite:///app.db              # postgresql://... in production
REDIS_URL=redis://localhost:6379
ELASTICSEARCH_URL=                         # unset disables search
POSTS_PER_PAGE=25
LOG_TO_STDOUT=false                        # true in containers

MAIL_SERVER=                               # unset disables all email
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
ADMINS=you@example.com                     # error reports and From address

MS_TRANSLATOR_KEY=                         # unset disables translation
MS_TRANSLATOR_REGION=global
```

`.flaskenv` holds non-secret Flask settings (`FLASK_APP`, `FLASK_DEBUG`) and is
read after `.env` without overriding it. Neither file is committed.

## Tests

```bash
python tests.py
```

## API usage

```bash
# Obtain a token
curl -u <username>:<password> -X POST http://localhost:5000/api/tokens

# Call an authenticated endpoint
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/users/1

# Revoke the token
curl -H "Authorization: Bearer <token>" -X DELETE http://localhost:5000/api/tokens
```

## Project layout

```
app/
  __init__.py      application factory, extension setup, logging
  models.py        SQLAlchemy models, search and pagination mixins
  main/            timeline, profiles, messaging, search routes
  auth/            login, registration, password reset
  api/             REST API blueprint
  errors/          error handlers
  tasks.py         RQ job definitions
  search.py        Elasticsearch index helpers
  translate.py     Microsoft Translator client
  cli.py           `flask translate` commands
  templates/       Jinja2 templates
  translations/    Babel message catalogs
migrations/        Alembic migration history
config.py          environment-driven configuration
microblog.py       application entry point
```

## Background job flow

The post export illustrates the async pipeline end to end:

1. The user requests an export; `User.launch_task` enqueues an RQ job and
   records a `Task` row.
2. The worker picks up `app.tasks.export_posts`, writing progress into the job's
   metadata as it serialises posts.
3. The browser polls the notifications endpoint and updates a progress bar.
4. On completion the worker emails the JSON as an attachment and marks the
   `Task` complete.
