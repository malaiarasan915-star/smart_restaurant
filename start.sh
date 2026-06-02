#!/usr/bin/env bash
# ─── Render.com Start Script for Smart Restaurant ────────────────────────────
# Runs on EVERY container boot.
# Uses Django's own "migrate --fake" to repair phantom migration records.
# Every step prints the exact DB host + name so we can confirm migrations
# and the app are always talking to the SAME PostgreSQL database.
set -o errexit

export DJANGO_SETTINGS_MODULE=restaurant_project.settings

# ── Step 0: Show which database this process will use ────────────────────────
echo "==> [start.sh] Step 0: DATABASE connection being used by THIS process:"
python manage.py shell -c "
import os
from django.db import connection
s = connection.settings_dict
raw_url = os.environ.get('DATABASE_URL', '(not set)')
# Mask the password in the URL for safe logging
import re
masked_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', raw_url)
print(f'  DATABASE_URL  : {masked_url}')
print(f'  ENGINE        : {s[\"ENGINE\"]}')
print(f'  HOST          : {s.get(\"HOST\", \"(empty=localhost)\")}')
print(f'  PORT          : {s.get(\"PORT\", \"(default)\")}')
print(f'  NAME          : {s.get(\"NAME\", \"(empty)\")}')
print(f'  USER          : {s.get(\"USER\", \"(empty)\")}')
"

# ── Step 1: Detect missing core tables ───────────────────────────────────────
echo ""
echo "==> [start.sh] Step 1: Detect missing core tables..."
set +e
python manage.py shell -c "
import sys
from django.db import connection
s = connection.settings_dict
print(f'  (checking on HOST={s.get(\"HOST\")} NAME={s.get(\"NAME\")})')
try:
    tables = connection.introspection.table_names()
    print(f'  Tables found in DB: {sorted(tables)}')
    missing = [t for t in ['menu_category', 'accounts_customuser', 'orders_order'] if t not in tables]
    if missing:
        print(f'  MISSING TABLES: {missing}')
        sys.exit(42)
    print('  Core tables present — no phantom repair needed.')
    sys.exit(0)
except Exception as e:
    print(f'  Introspection failed (fresh DB or error): {e}')
    sys.exit(0)
"
TABLE_STATUS=$?
set -e

# ── Step 2: If tables missing, fake-unapply phantom records ──────────────────
if [ "$TABLE_STATUS" -eq 42 ]; then
    echo ""
    echo "==> [start.sh] Step 2: Tables MISSING — resetting phantom migration records..."
    echo "    Using 'migrate --fake' (Django's own mechanism, NOT raw SQL DELETE)."
    echo "    Order: orders -> menu -> accounts (reverse dependency order)"
    echo ""

    python manage.py migrate orders zero --fake --no-input 2>&1 \
        || echo "    [orders] Nothing to unapply (not yet recorded)"

    python manage.py migrate menu zero --fake --no-input 2>&1 \
        || echo "    [menu] Nothing to unapply (not yet recorded)"

    python manage.py migrate accounts zero --fake --no-input 2>&1 \
        || echo "    [accounts] Nothing to unapply (not yet recorded)"

    echo ""
    echo "    Phantom records cleared. migrate will now create all tables."
else
    echo "==> [start.sh] Step 2: Skipped (tables already present)."
fi

# ── Step 3: Run migrate ───────────────────────────────────────────────────────
echo ""
echo "==> [start.sh] Step 3: Running migrate (--verbosity 2 logs each migration)..."
python manage.py migrate --no-input --verbosity 2

# ── Step 4: Final verification — print DB host + exact table list ─────────────
echo ""
echo "==> [start.sh] Step 4: Final table verification..."
python manage.py shell -c "
from django.db import connection
s = connection.settings_dict
print(f'  Verifying on HOST={s.get(\"HOST\")} NAME={s.get(\"NAME\")}')
tables = connection.introspection.table_names()
print(f'  All tables now in DB: {sorted(tables)}')
required = ['menu_category', 'menu_dish', 'accounts_customuser', 'orders_order', 'orders_orderitem']
missing = [t for t in required if t not in tables]
if missing:
    print(f'  FATAL: Still missing after migrate: {missing}')
    raise SystemExit(1)
print('  SUCCESS: All required tables confirmed.')
"

# ── Step 5: Start daphne ──────────────────────────────────────────────────────
echo ""
echo "==> [start.sh] Step 5: Starting daphne ASGI server..."
echo "    (daphne will connect using the same DATABASE_URL shown in Step 0)"
exec daphne -b 0.0.0.0 -p "$PORT" restaurant_project.asgi:application
