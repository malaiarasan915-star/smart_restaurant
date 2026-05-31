#!/usr/bin/env bash
# ─── Render.com Start Script for Smart Restaurant ────────────────────────────
# Runs migrate on EVERY container boot (idempotent — safe to call repeatedly).
# This guarantees the database schema is current even if the runtime DB differs
# from what the build container saw (common on Render free tier).
set -o errexit

export DJANGO_SETTINGS_MODULE=restaurant_project.settings

echo "==> [start.sh] Applying database migrations..."
python manage.py migrate --no-input --verbosity 1

echo "==> [start.sh] Verifying critical tables exist..."
python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
required = ['menu_category', 'menu_dish', 'accounts_customuser', 'orders_order', 'orders_orderitem']
missing = [t for t in required if t not in tables]
if missing:
    print('FATAL: Missing tables at startup:', missing)
    raise SystemExit(1)
print('[start.sh] All required tables confirmed:', required)
"

echo "==> [start.sh] Starting daphne ASGI server..."
exec daphne -b 0.0.0.0 -p "$PORT" restaurant_project.asgi:application
