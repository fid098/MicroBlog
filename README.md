# MicroBlog 🚀

A full-featured microblogging web application built with **Flask**, designed with scalability, API access, background jobs, and modern web features in mind.

This project demonstrates real-world backend and frontend concepts including REST APIs, authentication, background task queues, search, internationalization, and Docker-based deployment.

---

## ✨ Features

### 👤 User Management

- User registration and secure authentication
- Password hashing with Werkzeug
- Dynamic user profiles with Gravatar avatars
- Follow/unfollow system with relationship tracking
- Session-based and token-based authentication
- Password reset via email with JWT tokens

### 📝 Posts and Timeline

- Create, edit, and delete posts
- Personalized timeline showing followed users' posts
- Post pagination and infinite scroll
- Language detection for posts
- Export posts to JSON via background jobs

### 🔐 RESTful API

- Complete REST API with hypermedia links (HATEOAS)
- Token-based authentication with expiration
- Pagination with metadata
- User, posts, and followers endpoints
- Proper HTTP status codes and error handling
- API rate limiting and security

### 🔍 Full-Text Search

- Elasticsearch integration for advanced search
- Real-time search indexing
- Ranked search results with relevance scoring
- Automatic index synchronization
- Fallback handling when Elasticsearch unavailable

### 💬 Private Messaging

- One-to-one private messaging system
- Real-time unread message counters
- Message notifications via AJAX
- Timestamp tracking for read/unread status

### 🌍 Internationalization (i18n)

- Multi-language support (English, Spanish, Turkish, French, German, Chinese)
- Automatic locale detection from browser
- AJAX-based language switching without page reload
- Microsoft Translator API integration
- Localized date/time formatting with Flask-Moment
- Translatable UI strings with Flask-Babel

### 📧 Email Integration

- Asynchronous email sending via threading
- Password reset emails with secure tokens
- Post export delivery via email attachments
- Configurable SMTP support (Gmail, custom servers)
- HTML and plain-text email templates

### ⚙️ Background Tasks (Redis + RQ)

- Asynchronous task processing with Redis Queue
- Post export to JSON with progress tracking
- Task status monitoring and notifications
- Persistent task records in database
- Worker process management
- Real-time progress updates via AJAX

### 🐳 Docker & Deployment

- Multi-container Docker setup
- Dockerized Flask application
- Redis and Elasticsearch containers
- Gunicorn WSGI server for production
- Database migration automation
- Environment-based configuration
- Health checks and restart policies

### 🎨 Frontend Enhancements

- Responsive Bootstrap UI
- AJAX for dynamic content loading
- Real-time notifications system
- Live search functionality
- Popup messages and alerts
- Moment.js for relative timestamps
- No-JavaScript fallback support

---

## 🛠️ Tech Stack

**Backend**

- Python 3.14 - Core language
- Flask 3.x - Web framework
- Flask-SQLAlchemy - ORM and database management
- Flask-Login - User session management
- Flask-HTTPAuth - API authentication
- Flask-Migrate - Database migrations (Alembic)
- Flask-Mail - Email functionality
- Flask-Babel - Internationalization
- Flask-Moment - Timestamp localization
- Redis - In-memory data store and message broker
- RQ (Redis Queue) - Background job processing
- PyJWT - JSON Web Token implementation

**Frontend**

- Jinja2 - Template engine
- Bootstrap 5 - CSS framework
- JavaScript (Vanilla) - Client-side interactions
- AJAX - Asynchronous requests

**Database**

- SQLite - Development database
- PostgreSQL - Production database (optional)
- Elasticsearch 8.x - Full-text search engine

**DevOps**

- Docker - Containerization
- Gunicorn - Production WSGI server
- Git - Version control

---

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker Desktop (for Redis, Elasticsearch)
- Git

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/microblog.git
cd microblog


```

### Create virtual Environment

windows:
python -m venv venv
venv\Scripts\activate

Linux/MacOs/WSL:
python3 -m venv venv
source venv/bin/activate

```
### Install requirements
pip install -r requirements.txt



```

## Environment Variables

Create a `.flaskenv` file in the project root:
sSECRET_KEY=your-secret-key-here
FLASK_APP=microblog.py
FLASK_DEBUG=1

#Database (SQLite by default)
DATABASE_URL=sqlite:///app.db

#Redis
REDIS_URL=redis://localhost:6379

#Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

#Microsoft Translator (optional)
MS_TRANSLATOR_KEY=your-translator-key
MS_TRANSLATOR_REGION=ukwest

#Elasticsearch (optional)
ELASTICSEARCH_URL=http://localhost:9200

```
### Database Setup
flask db upgrade


```

### Redis and Background Tasks

start redis : redis-server
start RQ worker : rq worker microblog-tasks

```
### Docker setup
docker-compose up --build


```

## Running Services with Docker

docker run -d --name mysql \
 -p 3306:3306 \
 -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
 -e MYSQL_DATABASE=microblog \
 -e MYSQL_USER=microblog \
 -e MYSQL_PASSWORD=password \
 mysql:8.0

```
 ## Elasticsearch

docker run -d --name elasticsearch \
  -p 9200:9200 \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.1


```

### Docker Deployment

### Elasticsearch Indexing

#Build the image
docker build -t microblog:latest .

#Run the container
docker run -d -p 5000:5000 \
 -e DATABASE_URL=sqlite:///app.db \
 -e REDIS_URL=redis://redis:6379 \
 --name microblog \
 microblog:latest

Posts are automatically indexed when created or updated.
If elasticsearch was unavailable, reindex manually:

flask shell
from app.models import Post
for post in Post.query.all():
post.add_to_index()

```

## API authentication example
http --auth username:password POST http://localhost:5000/api/tokens


```

## Export Posts (Background Task)

The export posts feature demonstrates asynchronous processing:

- User clicks "Export Posts"
- Task is queued in Redis
- RQ worker picks up the task
- Posts are exported to JSON
- Progress updates sent via notifications
- Email sent with JSON attachment
- Task marked as complete

Implementation:

- app/tasks.py - Task definitions
- app/models.py - Task and notification models
- Redis Queue for job management
- AJAX polling for progress updates

## Internationalization

- Automatic locale detection
- Language switching via AJAX
- Localized timestamps
- Translatable UI text

## Learning Highlights

- REST API design
- Secure authentication
- Background job queues
- Database modeling
- Asynchronous tasks
- Internationalization
- Dockerized deployment
