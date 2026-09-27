"""Development settings — SQLite, debug toolbar, browser-reload."""

from .base import *  # noqa: F401, F403

DEBUG = True

SECRET_KEY = "insecure-development-secret-key-do-not-use-in-production"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

# Use SQLite for development to avoid requiring PostgreSQL locally.
# Override with DATABASE_URL env var if you need PostgreSQL locally.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

INSTALLED_APPS += [  # noqa: F405
    "django_browser_reload",
]

MIDDLEWARE += [  # noqa: F405
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

# Email — print to console in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Tailwind npm path (common Linux locations)
import shutil  # noqa: E402

NPM_BIN_PATH = shutil.which("npm") or "/usr/bin/npm"

# Disable whitenoise in dev (Django dev server serves static directly)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

INTERNAL_IPS = ["127.0.0.1"]
