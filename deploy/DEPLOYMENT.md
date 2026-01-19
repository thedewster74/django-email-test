# Deployment Guide

This guide provides instructions for deploying the Email Test PoC to a Linux server.

## Prerequisites

- Python 3.12 or higher
- Poetry
- Nginx (optional, for reverse proxy)
- Systemd (for service management)

## Initial Setup

### 1. Install System Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12 and pip
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Create Application Directory

```bash
sudo mkdir -p /opt/email-test-poc
sudo chown $USER:$USER /opt/email-test-poc
```

### 3. Clone/Copy Application Code

```bash
cd /opt/email-test-poc
# Copy your application files here
```

### 4. Install Dependencies

```bash
cd /opt/email-test-poc
poetry install --no-dev
```

### 5. Configure Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with production values
nano .env
```

Update the following variables in `.env`:
- `SECRET_KEY`: Generate a secure random key
- `DEBUG=False`
- `ALLOWED_HOSTS`: Add your server's domain/IP
- Email settings: Configure your SMTP server credentials

### 6. Run Database Migrations

```bash
poetry run python manage.py migrate
```

### 7. Collect Static Files

```bash
poetry run python manage.py collectstatic --noinput
```

### 8. Set Up Systemd Service

```bash
# Copy the service file
sudo cp deploy/email-test-poc.service /etc/systemd/system/

# Update paths in the service file if needed
sudo nano /etc/systemd/system/email-test-poc.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable email-test-poc
sudo systemctl start email-test-poc

# Check status
sudo systemctl status email-test-poc
```

## Nginx Configuration (Optional)

If using Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/email-test-poc/staticfiles/;
    }
}
```

## Deployment Updates

To deploy updates, use the provided deployment script:

```bash
cd /opt/email-test-poc
bash deploy/deploy.sh
```

Or manually:

```bash
cd /opt/email-test-poc
git pull origin main  # If using git
poetry install --no-dev
poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
sudo systemctl restart email-test-poc
```

## Monitoring

Check application logs:
```bash
sudo journalctl -u email-test-poc -f
```

Check service status:
```bash
sudo systemctl status email-test-poc
```

## Security Notes

1. Always set `DEBUG=False` in production
2. Use a strong, random `SECRET_KEY`
3. Configure firewall rules appropriately
4. Keep dependencies updated
5. Use HTTPS (configure SSL/TLS certificate)
6. Restrict `ALLOWED_HOSTS` to your domain only
