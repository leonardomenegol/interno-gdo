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

# Build channels_redis host config from individual env vars if available,
# otherwise fall back to parsing REDIS_URL.
# Railway exposes REDISHOST, REDISPORT, REDISPASSWORD individually which
# are more reliable than the composite REDIS_URL inside Docker networking.
if os.environ.get('REDISHOST'):
    _redis_host = {
        "host": os.environ['REDISHOST'],
        "port": int(os.environ.get('REDISPORT', 6379)),
        "password": os.environ.get('REDISPASSWORD') or os.environ.get('REDIS_PASSWORD') or None,
    }
    if not _redis_host["password"]:
        del _redis_host["password"]
else:
    _parsed = urlparse(REDIS_URL)
    _redis_host = {
        "host": _parsed.hostname,
        "port": _parsed.port or 6379,
        "db": int((_parsed.path or "/0").lstrip("/") or 0),
    }
    if _parsed.password:
        _redis_host["password"] = _parsed.password

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [_redis_host],
            "group_expiry": 10800,
        },
    },
}
