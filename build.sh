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

echo "==> Detecting and repairing phantom migration records (using migrate --fake)..."
# Raw SQL DELETEs against django_migrations are unreliable because each
# manage.py invocation is a separate process with its own connection. If the
# DB uses connection pooling (PgBouncer on Render) the DELETE may be rolled
# back silently before the next process connects.
# Django's own 'migrate --fake' is the correct, process-safe approach.
set +e
python manage.py shell -c "
import sys
from django.db import connection
try:
    tables = connection.introspection.table_names()
    missing = [t for t in ['menu_category', 'accounts_customuser', 'orders_order'] if t not in tables]
    if missing:
        print('MISSING TABLES:', missing)
        sys.exit(42)
    print('Core tables present.')
    sys.exit(0)
except Exception as e:
    print('Introspection skipped (fresh DB):', e)
    sys.exit(0)
"
TABLE_STATUS=$?
set -e

if [ "$TABLE_STATUS" -eq 42 ]; then
  echo "  Tables missing — resetting phantom migration records with --fake..."
  python manage.py migrate orders zero --fake --no-input 2>&1 \
      || echo "  [orders] Nothing to unapply"
  python manage.py migrate menu zero --fake --no-input 2>&1 \
      || echo "  [menu] Nothing to unapply"
  python manage.py migrate accounts zero --fake --no-input 2>&1 \
      || echo "  [accounts] Nothing to unapply"
  echo "  Phantom records cleared. migrate will re-create tables."
else
  echo "  Core tables present — no phantom repair needed."
fi

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
