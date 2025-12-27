MicroBlog

MicroBlog is a full-stack Flask web application that provides user authentication, posting, following, private messaging, notifications, and full-text search powered by Elasticsearch. It is built as a learning and demonstration project using modern Flask patterns and Dockerized services.

Features
User registration and authentication
User profiles and following system
Create, edit, and delete posts
Full-text search using Elasticsearch
Private messaging and notifications
Internationalization (Flask-Babel)
Database migrations with Flask-Migrate
Docker support for MySQL and Elasticsearch

Tech Stack
Backend: Flask (Python)
Database: MySQL (via SQLAlchemy + PyMySQL)
Search Engine: Elasticsearch
Authentication: Flask-Login
Migrations: Flask-Migrate / Alembic
Email: Flask-Mail
Containers: Docker
Frontend: Jinja2 templates, Bootstrap

Project Structure
MicroBlog/
│
├── app/
│ ├── auth/ # Authentication blueprint
│ ├── main/ # Main application routes
│ ├── errors/ # Error handlers
│ ├── models.py # Database models
│ ├── search.py # Elasticsearch helpers
│ └── **init**.py # App factory
│
├── migrations/ # Database migrations
├── Dockerfile # MicroBlog container image
├── config.py # Configuration settings
├── microblog.py # Application entry point
├── requirements.txt
└── README.md

Prerequisites
Make sure you have the following installed:
Python 3.11+
Docker & Docker Compose
Git

Environment Variables
Create a .flaskenv file (do not commit this):
FLASK_APP=microblog.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

DATABASE_URL=mysql+pymysql://microblog:password@127.0.0.1:3306/microblog
ELASTICSEARCH_URL=http://127.0.0.1:9200

-Add .flaskenv to .gitignore.

Running Services with Docker
Start MySQL
docker run -d --name mysql \
 -p 3306:3306 \
 -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
 -e MYSQL_DATABASE=microblog \
 -e MYSQL_USER=microblog \
 -e MYSQL_PASSWORD=password \
 mysql:8.0

Start Elasticsearch
docker run -d --name elasticsearch \
 -p 9200:9200 \
 -e discovery.type=single-node \
 -e xpack.security.enabled=false \
 -e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
 docker.elastic.co/elasticsearch/elasticsearch:8.11.1

Verify:
curl http://127.0.0.1:9200

Running the Application (Local Development)
Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Initialize the database
flask db upgrade

Run the app
flask run

Open:
http://127.0.0.1:5000

Elasticsearch Indexing
Posts are automatically indexed when created or updated.

If Elasticsearch was down when posts were created, you can reindex manually:

flask shell

from app import db
from app.models import Post

for post in Post.query.all():
post.add_to_index()

Dockerizing the Application (Optional)
Build the MicroBlog image:

docker build -t microblog:latest .

Run it (inside Docker network):

docker run -d --name microblog \
 -p 8000:5000 \
 --network microblog-network \
 -e DATABASE_URL="mysql+pymysql://microblog:password@mysql/microblog" \
 -e ELASTICSEARCH_URL="http://elasticsearch:9200" \
 microblog:latest
