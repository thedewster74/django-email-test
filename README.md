<<<<<<< HEAD
# Email Test PoC

A Django 6.0.1 proof-of-concept application for testing email endpoint connectivity. This project provides REST API endpoints to test email sending functionality with configurable SMTP settings managed through environment variables.

## Features

- REST API endpoints for testing email delivery
- Support for plain text and HTML emails
- Environment-based configuration using django-environ
- Production-ready deployment configuration
- Poetry for dependency management

## Prerequisites

- Python 3.12 or higher
- Poetry

## Installation

1. Install dependencies:
```bash
poetry install
```

2. Copy the example environment file and configure:
```bash
cp .env.example .env
# Edit .env with your email settings
```

3. Run database migrations:
```bash
poetry run python manage.py migrate
```

4. Start the development server:
```bash
poetry run python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## API Endpoints

### 1. Send Test Email
**POST** `/api/email/send/`

Send a plain text test email.

Request body:
```json
{
    "to_email": "recipient@example.com",
    "subject": "Test Subject",
    "message": "Test message body"
}
```

### 2. Send HTML Email
**POST** `/api/email/send-html/`

Send an HTML formatted email.

Request body:
```json
{
    "to_email": "recipient@example.com",
    "subject": "Test HTML Subject",
    "html_content": "<h1>Test HTML Email</h1><p>This is a test.</p>"
}
```

### 3. Get Email Configuration Status
**GET** `/api/email/config/`

Returns current email configuration (credentials are masked).

Response:
```json
{
    "success": true,
    "config": {
        "email_backend": "django.core.mail.backends.smtp.EmailBackend",
        "email_host": "smtp.gmail.com",
        "email_port": 587,
        "email_use_tls": true,
        "email_use_ssl": false,
        "default_from_email": "noreply@example.com",
        "has_credentials": true
    }
}
```

## Environment Variables

Configure these in your `.env` file:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@example.com
SERVER_EMAIL=noreply@example.com
```

## Development

Run tests:
```bash
poetry run python manage.py test
```

Run development server:
```bash
poetry run python manage.py runserver
```

## Deployment

See [deploy/DEPLOYMENT.md](deploy/DEPLOYMENT.md) for detailed deployment instructions to a Linux server.

Quick deployment with gunicorn:
```bash
poetry run gunicorn config.wsgi:application -c gunicorn_config.py
```

## Project Structure

```
.
├── config/              # Django project settings
│   ├── settings.py      # Main settings with environ integration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI configuration
├── email_test/          # Email testing app
│   ├── views.py         # API endpoints
│   └── urls.py          # App URL routing
├── deploy/              # Deployment configuration
│   ├── DEPLOYMENT.md    # Deployment guide
│   ├── deploy.sh        # Deployment script
│   └── email-test-poc.service  # Systemd service file
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment file
├── gunicorn_config.py   # Gunicorn configuration
├── manage.py            # Django management script
└── pyproject.toml       # Poetry dependencies
```
=======
# django-email-test
A Django 6.0.1 proof-of-concept application for testing email endpoint connectivity.
>>>>>>> 2a382e764f1e0a89c1690346d33c8303bb18bff2
