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

# Explicitly set the settings module (defensive — Render may not always inject it)
export DJANGO_SETTINGS_MODULE=restaurant_project.settings

echo "==> Testing database connection..."
python manage.py shell -c "
from django.db import connection
try:
    connection.ensure_connection()
    print('DB connection OK:', connection.settings_dict['HOST'])
except Exception as e:
    print('DB CONNECTION FAILED:', e)
    raise SystemExit(1)
"

echo "==> Checking migration status BEFORE migrate..."
python manage.py showmigrations

echo "==> Running database migrations..."
python manage.py migrate --no-input --verbosity 2

echo "==> Verifying critical tables were created..."
python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
print('Tables in DB:', sorted(tables))
required = ['menu_category', 'menu_dish', 'accounts_customuser', 'orders_order', 'orders_orderitem']
missing = [t for t in required if t not in tables]
if missing:
    print('MISSING TABLES:', missing)
    raise SystemExit(1)
else:
    print('SUCCESS: All required tables exist.')
"

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Build complete!"
