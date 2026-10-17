# ==============================================================================
# Docker
# ==============================================================================

import os
from urllib.parse import urlparse

import dj_database_url

ALLOWED_HOSTS = ["*"]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if os.environ.get('DJANGO_SECRET_KEY', ''):
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Use DATABASE_URL if set (Railway), otherwise fall back to local docker-compose defaults
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tabbycat',
            'USER': 'tabbycat',
            'PASSWORD': 'tabbycat',
            'HOST': 'db',
            'PORT': 5432,
        }
    }

REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/1')

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

# Parse REDIS_URL into components so channels_redis receives password explicitly
_redis = urlparse(REDIS_URL)
_redis_host = {
    "host": _redis.hostname,
    "port": _redis.port or 6379,
    "db": int((_redis.path or "/0").lstrip("/") or 0),
}
if _redis.password:
    _redis_host["password"] = _redis.password

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [_redis_host],
            "group_expiry": 10800,
        },
    },
}
