import os
from importlib.util import find_spec

from django.core.management.utils import get_random_secret_key

from .default_basedir import BASE_DIR
from .util import convert_http_header_to_django

########
# General
####
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key())
TIME_ZONE = "UTC"

########
# Network
####
ALLOWED_HOSTS = [
    os.getenv("ALLOWED_HOST", "localhost"),
]

if os.getenv("CSRF_TRUSTED_ORIGIN"):
    CSRF_TRUSTED_ORIGINS = [os.getenv("CSRF_TRUSTED_ORIGIN")]

SECURE_PROXY_SSL_HEADER = (
    os.getenv(
        "SECURE_PROXY_SSL_HEADER_NAME",
        convert_http_header_to_django("X-Forwarded-Proto"),
    ),
    os.getenv("SECURE_PROXY_SSL_HEADER_VALUE", "https"),
)
TLS_ENABLED = os.getenv("TLS_ENABLED", "false").lower() == "true"
if TLS_ENABLED:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "3600"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = (
        os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "false").lower() == "true"
    )
    SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "false").lower() == "true"

########
# Database
####
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME", "app"),
        "USER": os.getenv("DATABASE_USER", "postgres"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "app"),
        "HOST": os.getenv("DATABASE_HOST", "localhost"),
        "PORT": os.getenv("DATABASE_PORT", 5432),
        "CONN_MAX_AGE": 0,
    }
}

########
# Storage and Staticfiles
####
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.getenv("STORAGE_BUCKET_NAME", "app"),
            "endpoint_url": os.getenv("STORAGE_ENDPOINT", "http://localhost:9000"),
            "region_name": os.getenv("STORAGE_REGION", "eu-central-1"),
        },
    },
}

OBJECT_STORAGE_ENABLED = os.getenv("OBJECT_STORAGE_ENABLED", "false").lower() == "true"
if OBJECT_STORAGE_ENABLED:
    AWS_S3_FILE_OVERWRITE = False
else:
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    MEDIA_URL = "/media/"

########
# E-Mail
####
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 1025))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "false").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

########
# Miscellaneous
####
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

########
# Background Tasks via django-q2
####
if find_spec("django_q"):
    Q_CLUSTER = {
        "name": "DjangORM",
        "workers": 2,
        "timeout": 90,
        "retry": 120,
        "queue_limit": 50,
        "bulk": 10,
        "orm": "default",
        "catch_up": False,
    }
