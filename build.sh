#!/usr/bin/env bash
# ─── Render.com Build Script for Smart Restaurant ───────────────────────────
set -o errexit   # exit on error

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Build complete!"
