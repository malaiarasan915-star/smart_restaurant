#!/usr/bin/env bash
# ─── Render.com Start Script for Smart Restaurant ────────────────────────────
# Runs on EVERY container boot.
#
# Repair strategy (final version):
#   repair_db.py uses psycopg2 DIRECTLY with conn.autocommit=True set at the
#   driver level. This is the only fully reliable way to commit a DELETE against
#   django_migrations — Django manage.py shell -c commands run inside ORM
#   transaction contexts that can silently roll back on process exit.
#
# After repair, manage.py migrate re-creates any missing tables.
set -o errexit

export DJANGO_SETTINGS_MODULE=restaurant_project.settings

# ── Step 0: Show which DB this process will use ───────────────────────────────
echo ""
echo "==> [start.sh] Step 0: DATABASE_URL identity check"
python -c "
import os, re
url = os.environ.get('DATABASE_URL', '(not set)')
masked = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', url)
print(f'  DATABASE_URL: {masked}')
print(f'  DJANGO_SETTINGS_MODULE: {os.environ.get(\"DJANGO_SETTINGS_MODULE\", \"(not set)\")}')
"

# ── Step 1: Direct psycopg2 phantom migration repair ──────────────────────────
echo ""
echo "==> [start.sh] Step 1: psycopg2 phantom migration repair (repair_db.py)"
python repair_db.py

# ── Step 2: Run Django migrations ─────────────────────────────────────────────
echo ""
echo "==> [start.sh] Step 2: Running manage.py migrate (--verbosity 2)"
python manage.py migrate --no-input --verbosity 2

# ── Step 3: Verify tables and show runtime DB identity ────────────────────────
echo ""
echo "==> [start.sh] Step 3: Final table verification"
python manage.py shell -c "
from django.db import connection
s = connection.settings_dict
print(f'  Runtime DB HOST: {s.get(\"HOST\")}')
print(f'  Runtime DB NAME: {s.get(\"NAME\")}')
print(f'  Runtime DB USER: {s.get(\"USER\")}')
tables = connection.introspection.table_names()
print(f'  All tables ({len(tables)}): {sorted(tables)}')
required = ['menu_category', 'menu_dish', 'accounts_customuser', 'orders_order', 'orders_orderitem']
missing = [t for t in required if t not in tables]
if missing:
    print(f'  FATAL: Missing after migrate: {missing}')
    raise SystemExit(1)
print('  SUCCESS: All required tables confirmed.')
"

# ── Step 4: Start daphne ──────────────────────────────────────────────────────
echo ""
echo "==> [start.sh] Step 4: Starting daphne"
echo "    daphne inherits the same DATABASE_URL env shown in Step 0"
exec daphne -b 0.0.0.0 -p "$PORT" restaurant_project.asgi:application
