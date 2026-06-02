#!/usr/bin/env bash
# ─── Render.com Start Script for Smart Restaurant ────────────────────────────
# Runs on EVERY container boot.
# Uses Django's own "migrate --fake" to repair phantom migration records
# (recorded as applied in django_migrations but tables actually missing).
# This is safer than raw SQL DELETE because each manage.py call is a separate
# process with its own DB connection — raw DELETEs in one process are NOT
# visible to the next process if the connection pool rolled them back.
set -o errexit

export DJANGO_SETTINGS_MODULE=restaurant_project.settings

echo "==> [start.sh] Step 1: Detect missing core tables..."
# Use a dedicated exit code (42) to signal tables are missing.
# set +e / set -e lets us capture that code without killing the script.
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
    print('Core tables present:', ['menu_category', 'accounts_customuser', 'orders_order'])
    sys.exit(0)
except Exception as e:
    # Fresh DB or connection issue — let migrate handle it
    print('Introspection skipped (fresh DB or connection error):', e)
    sys.exit(0)
"
TABLE_STATUS=$?
set -e

if [ "$TABLE_STATUS" -eq 42 ]; then
    echo ""
    echo "==> [start.sh] Step 2: Tables missing — resetting phantom migration records..."
    echo "    Using 'migrate --fake' (Django's own mechanism, NOT raw SQL DELETE)."
    echo "    Unapplying in reverse dependency order: orders -> menu -> accounts"
    echo ""

    # orders depends on menu + accounts, so unapply it first
    python manage.py migrate orders zero --fake --no-input 2>&1 \
        || echo "    [orders] Nothing to unapply (not recorded — that is OK)"

    # menu has no dependencies among our apps
    python manage.py migrate menu zero --fake --no-input 2>&1 \
        || echo "    [menu] Nothing to unapply (not recorded — that is OK)"

    # accounts has no dependencies among our apps
    python manage.py migrate accounts zero --fake --no-input 2>&1 \
        || echo "    [accounts] Nothing to unapply (not recorded — that is OK)"

    echo ""
    echo "    Phantom records cleared. 'migrate' will now re-create all tables."
else
    echo "==> [start.sh] Step 2: All core tables present — no phantom repair needed."
fi

echo ""
echo "==> [start.sh] Step 3: Running migrate (--verbosity 2 shows each migration applied)..."
python manage.py migrate --no-input --verbosity 2

echo ""
echo "==> [start.sh] Step 4: Final table verification..."
python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
print('Tables in PostgreSQL DB:', sorted(tables))
required = ['menu_category', 'menu_dish', 'accounts_customuser', 'orders_order', 'orders_orderitem']
missing = [t for t in required if t not in tables]
if missing:
    print('FATAL: Still missing after migrate:', missing)
    raise SystemExit(1)
print('SUCCESS: All required tables confirmed.')
"

echo ""
echo "==> [start.sh] Step 5: Starting daphne ASGI server..."
exec daphne -b 0.0.0.0 -p "$PORT" restaurant_project.asgi:application
