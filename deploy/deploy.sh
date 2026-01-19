#!/bin/bash
# Deployment script for Email Test PoC

set -e  # Exit on error

echo "Starting deployment..."

# Configuration
APP_DIR="/opt/email-test-poc"
SERVICE_NAME="email-test-poc"

# Navigate to application directory
cd "$APP_DIR"

# Pull latest code (if using git)
# git pull origin main

# Install/update dependencies
echo "Installing dependencies..."
poetry install --no-dev

# Collect static files
echo "Collecting static files..."
poetry run python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
poetry run python manage.py migrate --noinput

# Restart the service
echo "Restarting service..."
sudo systemctl restart "$SERVICE_NAME"

# Check service status
sudo systemctl status "$SERVICE_NAME"

echo "Deployment completed successfully!"
