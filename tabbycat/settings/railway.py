import os

import dj_database_url

from .core import TABBYCAT_VERSION

if os.environ.get('TAB_DIRECTOR_EMAIL', ''):
    TAB_DIRECTOR_EMAIL = os.environ.get('TAB_DIRECTOR_EMAIL')

if os.environ.get('DJANGO_SECRET_KEY', ''):
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['*']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if 'DJANGO_SECRET_KEY' in os.environ and os.environ.get('DISABLE_HTTPS_REDIRECTS', '') != 'disable':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ==============================================================================
# Postgres
# ==============================================================================

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://localhost',
        conn_max_age=600,
    )
}

# ==============================================================================
# Redis
# ==============================================================================

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 60,
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
            "group_expiry": 10800,
        },
    },
}

DISABLE_SENTRY = True
