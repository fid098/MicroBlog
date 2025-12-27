# MicroBlog

MicroBlog is a full-stack Flask web application featuring user authentication, posts, following, private messaging, notifications, and full-text search powered by Elasticsearch. The project follows modern Flask best practices and supports both local development and Dockerized services.

---

## Features

- User registration and authentication
- User profiles and following system
- Create, edit, and delete posts
- Full-text search with Elasticsearch
- Private messaging and notifications
- Internationalization (Flask-Babel)
- Database migrations with Flask-Migrate
- Docker support for MySQL and Elasticsearch

---

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** MySQL (SQLAlchemy + PyMySQL)
- **Search:** Elasticsearch
- **Auth:** Flask-Login
- **Migrations:** Flask-Migrate / Alembic
- **Mail:** Flask-Mail
- **Containers:** Docker
- **Templates:** Jinja2 + Bootstrap

---

---

## Prerequisites

- Python 3.11+
- Docker
- Git

---

## Environment Variables

Create a `.flaskenv` file in the project root:

```env
FLASK_APP=microblog.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

DATABASE_URL=mysql+pymysql://microblog:password@127.0.0.1:3306/microblog
ELASTICSEARCH_URL=http://127.0.0.1:9200

Do not commit .flaskenv to source control

## Running Services with Docker

docker run -d --name mysql \
  -p 3306:3306 \
  -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
  -e MYSQL_DATABASE=microblog \
  -e MYSQL_USER=microblog \
  -e MYSQL_PASSWORD=password \
  mysql:8.0

 ## Elasticsearch

docker run -d --name elasticsearch \
  -p 9200:9200 \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.1


 ## Local Development

  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt

 ## Initialize the Database

 flask db upgrade

 ## Run the application

 flask run

 ## Elasticsearch Indexing

 Posts are automatically indexed when created or updated.
 If elasticsearch was unavailable, reindex manually:

 flask shell
 from app.models import Post
 for post in Post.query.all():
    post.add_to_index()


```
