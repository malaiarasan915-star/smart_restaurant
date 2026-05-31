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

echo "==> Repairing any stale/fake migration records..."
# This handles the case where django_migrations records a migration as applied
# but the actual table was never created (e.g. from a prior failed deploy).
# We check each critical app: if the migration is "applied" but the table is
# missing, we mark it as unapplied so migrate recreates the table cleanly.
python manage.py shell -c "
from django.db import connection, ProgrammingError

def table_exists(name):
    try:
        tables = connection.introspection.table_names()
        return name in tables
    except Exception:
        return False

def migration_recorded(app, name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                \"SELECT COUNT(*) FROM django_migrations WHERE app=%s AND name=%s\",
                [app, name]
            )
            return cursor.fetchone()[0] > 0
    except Exception:
        return False

repairs = [
    ('menu',   '0001_initial', 'menu_category'),
    ('orders', '0001_initial', 'orders_order'),
]

for app, migration, table in repairs:
    if migration_recorded(app, migration) and not table_exists(table):
        print(f'REPAIR: {app}.{migration} is recorded but {table} table is missing — marking unapplied')
        with connection.cursor() as cursor:
            cursor.execute(
                \"DELETE FROM django_migrations WHERE app=%s AND name=%s\",
                [app, migration]
            )
        print(f'REPAIR DONE: {app}.{migration} will be re-applied by migrate')
    elif migration_recorded(app, migration):
        print(f'OK: {app}.{migration} applied and {table} table exists')
    else:
        print(f'PENDING: {app}.{migration} not yet applied')
"

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
