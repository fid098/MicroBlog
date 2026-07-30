FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=microblog.py \
    LOG_TO_STDOUT=true

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod +x boot.sh

# Compile the .po catalogs into the .mo files Babel loads at runtime; the
# compiled output is deliberately not committed to the repository.
RUN flask translate compile

# Run as an unprivileged user. Logs go to stdout, so no writable paths needed.
RUN useradd --create-home --shell /bin/bash microblog && chown -R microblog:microblog /app
USER microblog

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
