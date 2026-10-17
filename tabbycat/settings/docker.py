# ==============================================================================
# Docker
# ==============================================================================

import logging
import os
from urllib.parse import urlparse

import dj_database_url

_log = logging.getLogger(__name__)

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

# Build channels_redis host — try every source in order
_redishost = os.environ.get('REDISHOST')
_redispassword = os.environ.get('REDISPASSWORD') or os.environ.get('REDIS_PASSWORD')
_redisport = int(os.environ.get('REDISPORT', 6379))

_log.warning(
    "REDIS cfg: REDIS_URL_set=%s REDISHOST=%s REDISHOST_set=%s REDISPASSWORD_set=%s",
    bool(os.environ.get('REDIS_URL')),
    _redishost or 'NONE',
    bool(_redishost),
    bool(_redispassword),
)

if _redishost and _redispassword:
    _redis_host = {"host": _redishost, "port": _redisport, "password": _redispassword}
elif REDIS_URL != 'redis://redis:6379/1':
    # REDIS_URL was explicitly set (not default), use it directly
    _redis_host = {"address": REDIS_URL}
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

# ==============================================================================
# Email
# ==============================================================================

if os.environ.get('RESEND_API_KEY', ''):
    ANYMAIL = {"RESEND_API_KEY": os.environ['RESEND_API_KEY']}
    EMAIL_BACKEND = 'anymail.backends.resend.EmailBackend'
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'onboarding@resend.dev')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

elif os.environ.get('EMAIL_HOST', ''):
    SERVER_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
    DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'false').lower() == 'true'

elif os.environ.get('SENDGRID_API_KEY', ''):
    SERVER_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'root@localhost')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'notconfigured@tabbycatsite')
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_API_KEY']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
