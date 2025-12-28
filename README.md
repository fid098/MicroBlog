# MicroBlog 🚀

A full-featured microblogging web application built with **Flask**, designed with scalability, API access, background jobs, and modern web features in mind.

This project demonstrates real-world backend and frontend concepts including REST APIs, authentication, background task queues, search, internationalization, and Docker-based deployment.

---

## ✨ Features

### 👤 User Management

- User registration and login
- Secure password hashing
- User profiles with bio and avatar (Gravatar)
- Follow / unfollow users
- User authentication via session and API tokens

### 📝 Posts

- Create, edit, delete posts
- Followed users timeline
- Export posts using **Redis + RQ background jobs**
- Post counts and user statistics

### 🔐 API Integration

- RESTful API endpoints
- Token-based authentication
- Pagination and hypermedia links
- JSON responses with proper error handling

### 🔍 Search

- Full-text search for posts
- Search index integration
- Ranked search results

### 💬 Private Messaging

- One-to-one private messages
- Unread message counters
- Message timestamps

### 🌍 Internationalization (i18n)

- Multiple language support
- Automatic language detection
- AJAX-based language switching
- International date & time formatting

### 📧 Email Support

- Password reset emails
- Notification emails
- Configurable SMTP support

### ⚙️ Background Tasks (Redis + RQ)

- Asynchronous task processing
- Export posts in the background
- Task progress tracking
- Persistent task records

### 🐳 Docker Integration

- Dockerized application
- Easy local and production deployment
- Consistent runtime environment

### 🎨 Frontend Enhancements

- AJAX interactions
- Popup notifications
- Responsive UI
- Dynamic updates without page reloads

---

## 🛠️ Tech Stack

**Backend**

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-HTTPAuth
- Flask-Migrate
- Redis + RQ

**Frontend**

- Jinja2 templates
- JavaScript (AJAX)
- Bootstrap

**Database**

- SQLite (development)
- Easily adaptable to PostgreSQL/MySQL

**Other**

- Docker
- JWT
- Elasticsearch-style search integration
- SMTP email services

---

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/microblog.git
cd microblog


```

### Create virtual Environment

python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

```
### Install requirements
pip install -r requirements.txt



```

## Environment Variables

Create a `.flaskenv` file in the project root:
setx FLASK_APP=microblog.py
setx FLASK_ENV=developmentl

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

## Elasticsearch Indexing

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

-Triggered from the UI or API
-Runs asynchronously via Redis
-Progress tracked per user
-Exported data delivered once complete

## Internationalization

-Automatic locale detection
-Language switching via AJAX
-Localized timestamps
-Translatable UI text

## Learning Highlights

-REST API design
-Secure authentication
-Background job queues
-Database modeling
-Asynchronous tasks
-Internationalization
-Dockerized deployment
