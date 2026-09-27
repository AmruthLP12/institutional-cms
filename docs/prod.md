# Development, Production and Operations Guide

## 1. Prerequisites

Verify versions before starting:

```bash
python --version
git --version
psql --version
```

Target current stable Python 3.14.x.

Do not install Python 3.15 pre-release builds for production.

## 2. Create environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## 3. Install dependencies

Use the generated lock/requirements workflow.

At minimum:

```bash
python -m pip install Django Wagtail django-tailwind psycopg[binary]
python -m pip install pytest pytest-django ruff
```

The actual project must pin resolved versions after compatibility testing.

Do not install packages merely because they are popular.

## 4. Tailwind

Use django-tailwind's official installation process.

Reference:

https://django-tailwind.readthedocs.io/en/latest/installation.html

Do not replace this with Vite.

The project should use the django-tailwind management commands.

Typical flow:

```bash
python manage.py tailwind init
python manage.py tailwind install
python manage.py tailwind build
```

For development, use the supported django-tailwind development command when appropriate.

If DaisyUI is used, use the current compatible npm-based django-tailwind plugin workflow. Do not assume DaisyUI compatibility without checking it.

## 5. Database

Production database:

PostgreSQL.

Example development environment:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/institutional_cms
```

Never commit real credentials.

## 6. Environment variables

Provide `.env.example`.

Possible values:

```env
DJANGO_SETTINGS_MODULE=config.settings.development
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=
CSRF_TRUSTED_ORIGINS=
DEFAULT_FROM_EMAIL=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

Only add variables actually used by the project.

## 7. First run

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py tailwind install
python manage.py tailwind build
python manage.py createsuperuser
python manage.py runserver
```

CMS:

```text
/admin/
```

or the project's Wagtail admin URL.

## 8. Seed data

Provide a management command such as:

```bash
python manage.py seed_cms
```

Options should include:

```bash
python manage.py seed_cms --help
python manage.py seed_cms --demo
python manage.py seed_cms --legal
python manage.py seed_cms --navigation
```

The command must be idempotent.

It must not create duplicate pages on repeated runs.

Seed content must be obviously fictional/demo content unless real institution data has been supplied.

## 9. Testing

```bash
python manage.py check
python manage.py test
pytest
```

Optional:

```bash
pytest --cov
```

Do not report a coverage percentage unless the command was actually run.

## 10. Static checks

```bash
ruff check .
ruff format --check .
```

If type checking is configured:

```bash
mypy .
```

or the project's selected type checker.

## 11. Security check

Before deployment:

```bash
python manage.py check --deploy
```

Verify:

- DEBUG=False
- SECRET_KEY is secret
- ALLOWED_HOSTS is restricted
- CSRF trusted origins are correct
- secure cookies enabled
- HTTPS enforced
- HSTS configured appropriately
- static/media permissions are correct
- private files are not public
- database credentials are not in Git

## 12. Production settings

Production should include:

```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Only enable HSTS after confirming HTTPS is correct across the domain.

Configure allowed hosts explicitly.

## 13. Apache

If Apache is the institution's standard web server, keep Apache.

Do not replace Apache with nginx simply because a tutorial uses nginx.

Apache should:

- terminate TLS where appropriate
- serve static files
- serve permitted public media
- proxy application requests to the Django application server
- block access to secrets and internal files

## 14. Application server

Use a maintained WSGI/ASGI server appropriate to the Django deployment.

The exact process model must be documented after checking the host environment.

## 15. Backups

Back up:

- PostgreSQL
- media
- important configuration
- deployment configuration

Test restoration.

A backup that has never been restored is not a verified backup.

## 16. Media backup

Media should be stored outside ephemeral application directories.

If using local filesystem storage:

```text
/var/lib/institutional-cms/media/
```

or an institution-approved location.

Restrict permissions.

## 17. Database migrations

Before production:

```bash
python manage.py makemigrations --check
python manage.py migrate --plan
```

Then:

```bash
python manage.py migrate
```

Never edit already-applied migrations casually.

## 18. Release process

Recommended:

```text
Develop
  |
Tests
  |
Security checks
  |
Migration review
  |
Backup
  |
Deploy
  |
Smoke test
  |
Monitor
```

## 19. Smoke tests

Verify:

- homepage
- navigation
- news
- events
- documents
- search
- legal pages
- admin login
- media
- sitemap
- robots.txt
- redirects
- forms

## 20. Rollback

Document:

- application rollback
- migration rollback strategy
- database restore procedure
- static/media rollback
- configuration rollback

Never assume a Django migration can always be safely reversed.

## 21. Package maintenance

Monthly or before planned releases:

1. Check Django security releases.
2. Check Wagtail security releases.
3. Check django-tailwind.
4. Check Tailwind.
5. Check frontend plugins.
6. Check Python patch releases.
7. Review release notes.
8. Run tests.
9. Upgrade deliberately.

Security releases should be prioritized.

## 22. Production checklist

```text
[ ] DEBUG=False
[ ] HTTPS working
[ ] Secure cookies enabled
[ ] HSTS reviewed
[ ] Allowed hosts restricted
[ ] Database backups active
[ ] Media backups active
[ ] Restore procedure tested
[ ] Error monitoring active
[ ] Logs accessible
[ ] Static files collected
[ ] Private media protected
[ ] Wagtail permissions reviewed
[ ] Editorial workflows tested
[ ] Legal content approval workflow tested
[ ] Seed/demo data not exposed
[ ] Sitemap available
[ ] robots.txt available
[ ] Accessibility smoke test complete
[ ] Mobile smoke test complete
[ ] Django deploy checks pass
```
