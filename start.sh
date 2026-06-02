#!/usr/bin/env bash
# ─── Render.com Start Script for Smart Restaurant ────────────────────────────
# Runs migrate on EVERY container boot (idempotent — safe to call repeatedly).
# Also detects and repairs phantom migrations (recorded as applied but tables
# missing) — required for Render free-tier where the DB can be wiped between
# deploys while django_migrations still has stale records.
set -o errexit

export DJANGO_SETTINGS_MODULE=restaurant_project.settings

echo "==> [start.sh] Repairing any phantom migration records..."
python manage.py shell -c "
from django.db import connection

def table_exists(name):
    try:
        return name in connection.introspection.table_names()
    except Exception:
        return False

def migration_recorded(app, name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) FROM django_migrations WHERE app=%s AND name=%s',
                [app, name]
            )
            return cursor.fetchone()[0] > 0
    except Exception:
        # django_migrations table does not exist yet — that is fine, migrate will create it
        return False

# Only apps that have real 0001_initial migrations and sentinel tables we can verify
repairs = [
    ('accounts', '0001_initial', 'accounts_customuser'),
    ('menu',     '0001_initial', 'menu_category'),
    ('orders',   '0001_initial', 'orders_order'),
]

repaired = 0
for app, migration, sentinel_table in repairs:
    if migration_recorded(app, migration) and not table_exists(sentinel_table):
        print(f'PHANTOM: {app}.{migration} is in django_migrations but {sentinel_table} table is MISSING — removing stale record')
        with connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM django_migrations WHERE app=%s AND name=%s',
                [app, migration]
            )
        print(f'REPAIRED: {app}.{migration} will be re-applied by migrate')
        repaired += 1
    elif not migration_recorded(app, migration):
        print(f'PENDING: {app}.{migration} not yet in django_migrations — migrate will apply it')
    else:
        print(f'OK: {app}.{migration} applied and {sentinel_table} table confirmed present')

print(f'Phantom repair complete — {repaired} stale record(s) removed.')
"

echo "==> [start.sh] Applying database migrations..."
python manage.py migrate --no-input --verbosity 2

echo "==> [start.sh] Verifying critical tables exist..."
python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
print('All tables in DB:', sorted(tables))
required = ['menu_category', 'menu_dish', 'accounts_customuser', 'orders_order', 'orders_orderitem']
missing = [t for t in required if t not in tables]
if missing:
    print('FATAL: Missing tables at startup:', missing)
    raise SystemExit(1)
print('[start.sh] SUCCESS — all required tables confirmed.')
"

echo "==> [start.sh] Starting daphne ASGI server..."
exec daphne -b 0.0.0.0 -p "$PORT" restaurant_project.asgi:application
