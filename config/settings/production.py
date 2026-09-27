"""Production settings — PostgreSQL, HTTPS, secure cookies, whitenoise."""

from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = False

SECRET_KEY = config("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS", cast=lambda v: [h.strip() for h in v.split(",")]
)

# HTTPS and secure cookies
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HSTS — only enable after confirming HTTPS works end-to-end
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool
)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool)

# Content Security Policy — permissive baseline; tighten after audit
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# PostgreSQL from environment
import dj_database_url  # noqa: E402

DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=60,
        conn_health_checks=True,
    )
}

# Static files via whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Email — use real SMTP in production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "wagtail": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
