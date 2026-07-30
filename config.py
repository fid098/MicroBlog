import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# .env holds secrets and takes precedence; .flaskenv holds non-secret defaults.
load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(basedir, '.flaskenv'), override=False)


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ('true', '1', 'yes')


def _env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-insecure-key'

    # Heroku-style DATABASE_URL uses the legacy postgres:// scheme, which
    # SQLAlchemy 1.4+ no longer accepts.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Containerised deployments capture stdout; local runs write a rotating file.
    LOG_TO_STDOUT = _env_bool('LOG_TO_STDOUT')

    MAIL_SERVER = os.environ.get('MAIL_SERVER', '').strip()
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = _env_bool('MAIL_USE_TLS')
    MAIL_USE_SSL = _env_bool('MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '').strip()
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '').strip()

    # Recipients for unhandled-exception tracebacks in production. Also used as
    # the From address for password-reset and export emails, so it falls back to
    # the SMTP account rather than being empty.
    ADMINS = _env_list('ADMINS') or ([MAIL_USERNAME] if MAIL_USERNAME else [])

    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE') or 25)

    # Only locales with a catalog under app/translations/ belong here; anything
    # else silently falls back to English.
    LANGUAGES = ['en', 'es']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    MS_TRANSLATOR_REGION = os.environ.get('MS_TRANSLATOR_REGION') or 'global'

    # Search and background jobs degrade gracefully when unset.
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') or None
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
