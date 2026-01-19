# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 6.0.1 proof-of-concept application for testing email endpoint connectivity. The project uses Poetry for dependency management and django-environ for environment-based configuration. It's designed to be deployed on Linux servers using gunicorn and systemd.

## Common Commands

### Development

```bash
# Install dependencies
poetry install

# Run development server
poetry run python manage.py runserver

# Run database migrations
poetry run python manage.py migrate

# Create new migrations after model changes
poetry run python manage.py makemigrations

# Run tests
poetry run python manage.py test

# Create superuser for admin access
poetry run python manage.py createsuperuser

# Open Django shell
poetry run python manage.py shell

# Send test email
poetry run python manage.py send_test_email recipient@example.com
poetry run python manage.py send_test_email recipient@example.com --subject "Custom Subject" --message "Custom message"
```

### Dependency Management

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show installed packages
poetry show
```

### Production/Deployment

```bash
# Run with gunicorn (production)
poetry run gunicorn config.wsgi:application -c gunicorn_config.py

# Collect static files for production
poetry run python manage.py collectstatic --noinput

# Deploy to server
bash deploy/deploy.sh
```

## Architecture

### Project Structure

- **config/**: Django project settings directory
  - `settings.py`: Main configuration file with django-environ integration
  - `urls.py`: Root URL configuration, includes email_test app URLs under `/api/email/`
  - `wsgi.py`: WSGI application entry point for deployment

- **email_test/**: Django app for email testing functionality
  - `views.py`: Contains three API endpoints (send text, send HTML, get config status)
  - `urls.py`: App-level URL routing
  - `management/commands/send_test_email.py`: Management command for sending test emails
  - All endpoints return JSON responses

- **deploy/**: Deployment configuration files
  - `DEPLOYMENT.md`: Comprehensive deployment guide
  - `email-test-poc.service`: systemd service file template
  - `deploy.sh`: Automated deployment script

### Environment Configuration Pattern

This project uses **django-environ** for all configuration. The pattern is:

1. Environment variables are read from `.env` file at project root
2. `config/settings.py` imports `environ` and initializes it with type casting and defaults
3. All sensitive data (SECRET_KEY, email credentials) must be in `.env`, never committed to git
4. `.env.example` provides a template showing all required variables

**Key settings managed via environment:**
- `SECRET_KEY`: Django secret key (required in production)
- `DEBUG`: Boolean, should be False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames
- Email settings: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- Email backends: Use `django.core.mail.backends.console.EmailBackend` for local dev, `django.core.mail.backends.smtp.EmailBackend` for production

### Email Backend Configuration

The application supports multiple email backends via `EMAIL_BACKEND` environment variable:

- **console**: `django.core.mail.backends.console.EmailBackend` - Prints emails to console (default for local dev)
- **smtp**: `django.core.mail.backends.smtp.EmailBackend` - Sends via SMTP server (production)
- **file**: `django.core.mail.backends.filebased.EmailBackend` - Saves emails to files (testing)
- **memory**: `django.core.mail.backends.locmem.EmailBackend` - Stores in memory (unit tests)

### API Endpoints Architecture

All endpoints are under `/api/email/`:

1. **POST /api/email/send/**: Send plain text email
   - Accepts: `to_email`, `subject`, `message`
   - Uses Django's `send_mail()` function
   - CSRF exempt for API usage

2. **POST /api/email/send-html/**: Send HTML email
   - Accepts: `to_email`, `subject`, `html_content`
   - Uses `EmailMessage` with `content_subtype='html'`
   - CSRF exempt for API usage

3. **GET /api/email/config/**: Get email configuration status
   - Returns current configuration without exposing credentials
   - Shows `has_credentials` boolean instead of actual passwords

All endpoints return JSON with `success` boolean and appropriate status codes (200, 400, 500).

## Python Version Requirement

Django 6.0.1 requires Python >= 3.12. The `pyproject.toml` specifies `requires-python = ">=3.12,<4.0"`. Do not change this requirement without updating Django version.

## Database

The project uses SQLite by default (`db.sqlite3` in project root). For production deployment, consider switching to PostgreSQL or MySQL by updating the `DATABASES` setting in `config/settings.py` and adding the appropriate database adapter dependency.

## Static Files

Static files are configured with `STATIC_URL = 'static/'`. For production deployment, run `collectstatic` to gather all static files into a single directory that can be served by Nginx or Apache.

## Deployment Considerations

- The project includes a gunicorn configuration file (`gunicorn_config.py`) optimized for production
- Systemd service file is provided in `deploy/email-test-poc.service`
- Update service file paths if deploying to a directory other than `/opt/email-test-poc`
- Always set `DEBUG=False` in production `.env`
- Configure `ALLOWED_HOSTS` with actual domain names
- Use a strong, randomly generated `SECRET_KEY` in production

## Adding New Email Features

When adding new email-related functionality:

1. Add new views to `email_test/views.py`
2. Register URLs in `email_test/urls.py`
3. Follow the existing pattern: accept JSON, return JSON with `success` field
4. Use `@csrf_exempt` decorator for API endpoints
5. Add appropriate error handling (400 for client errors, 500 for server errors)
6. Test with console backend first, then SMTP

## Configuration File Locations

- Environment variables: `.env` (root directory, not in git)
- Django settings: `config/settings.py`
- URL routing: `config/urls.py` (root) and `email_test/urls.py` (app)
- Dependencies: `pyproject.toml`
- Gunicorn config: `gunicorn_config.py`
- Git ignore rules: `.gitignore`
