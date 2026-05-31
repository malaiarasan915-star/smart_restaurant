#!/usr/bin/env bash
# ─── Render.com Build Script for Smart Restaurant ───────────────────────────
set -o errexit   # exit immediately on any error

echo "==> Python version:"
python --version

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Verifying DATABASE_URL is set..."
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set. Aborting build."
  exit 1
fi
echo "==> DATABASE_URL is configured (PostgreSQL)."

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Build complete!"
