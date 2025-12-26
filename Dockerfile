FROM python:slim
# from python:slim, this image is based on the official Python slim image
# the FROM command specifies the base container image on which the new image will be built
# the slim tag selects a container image that has only the minimal packages required to run the Python interpreter

# Install system dependencies
# COPY command transfers files from the host machine to the container's filesystem
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql cryptography
# gunicorn is a Python WSGI HTTP Server for UNIX. It is a pre-fork worker model, which means that it forks multiple worker processes to handle requests. This makes it suitable for handling multiple requests simultaneously in a production environment.

# Set working directory
COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod a+x boot.sh
# RUN chmod a+x boot.sh boot.sh ensures this new boot.sh file is correctly set as an executable inside the container

# Set environment variables inside the container
ENV FLASK_APP=microblog.py
RUN flask translate compile
# this compiles the translation files for the Flask application

# Expose port and define entrypoint
EXPOSE 5000
# this configures the port that this container will be using for its server.
ENTRYPOINT ["./boot.sh"]
# this defines the default command that should be executed when a container is started with this image.
# this will run the boot.sh script, which typically contains commands to start the Flask application using Gunicorn.