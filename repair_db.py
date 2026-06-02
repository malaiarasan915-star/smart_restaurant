#!/usr/bin/env python3
"""
repair_db.py — Standalone psycopg2 phantom-migration repair.

Called by start.sh BEFORE manage.py migrate.
Uses psycopg2 directly — NOT Django ORM — so conn.autocommit=True is set at
the driver level, guaranteeing every DELETE commits immediately regardless of
any Django transaction wrapper that might exist in manage.py shell -c.

Repair logic:
  If menu_category (or accounts_customuser / orders_order) is MISSING,
  delete any stale django_migrations records for those apps so that
  the subsequent "manage.py migrate" will re-apply them from scratch
  and CREATE the missing tables.
"""
import os
import sys


database_url = os.environ.get("DATABASE_URL", "")
if not database_url:
    print("[repair_db] DATABASE_URL not set — SQLite mode, nothing to repair.")
    sys.exit(0)

try:
    import psycopg2
    from urllib.parse import urlparse, urlunparse

    url = urlparse(database_url)

    # ── Log which DB we are connecting to (mask password) ──────────────────
    masked = urlunparse((
        url.scheme, f"{url.username}:***@{url.hostname}:{url.port}",
        url.path, url.params, url.query, url.fragment
    ))
    print(f"[repair_db] DATABASE_URL (masked): {masked}")

    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port or 5432,
        dbname=url.path.lstrip("/"),
        user=url.username,
        password=url.password,
        sslmode="require",
    )
    # ── True autocommit at the psycopg2 driver level ─────────────────────────
    # Every statement commits the instant it executes — no Django transaction
    # wrapper can intercept or roll this back.
    conn.autocommit = True

    with conn.cursor() as cur:
        # ── A: Print the actual PostgreSQL DB identity ──────────────────────
        cur.execute("SELECT current_database(), current_user, version()")
        row = cur.fetchone()
        print(f"[repair_db] Connected → database={row[0]}  user={row[1]}")
        print(f"[repair_db] PostgreSQL version: {row[2][:40]}")

        # ── B: Check which core tables exist ────────────────────────────────
        core_tables = ["menu_category", "accounts_customuser", "orders_order"]
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """,
        )
        existing = {row[0] for row in cur.fetchall()}
        missing = [t for t in core_tables if t not in existing]

        print(f"[repair_db] Tables in 'public' schema ({len(existing)} total): "
              f"{sorted(existing)}")
        print(f"[repair_db] Core tables missing: {missing if missing else 'none'}")

        if not missing:
            print("[repair_db] All core tables present — no phantom repair needed.")
            conn.close()
            sys.exit(0)

        # ── C: Remove phantom migration records ─────────────────────────────
        print("[repair_db] Removing phantom django_migrations records...")
        try:
            cur.execute(
                "DELETE FROM django_migrations "
                "WHERE app IN ('menu', 'orders', 'accounts')"
            )
            deleted = cur.rowcount
            print(f"[repair_db] Deleted {deleted} phantom record(s) "
                  f"(autocommit=True — committed immediately).")

            # Show what remains so we can verify
            cur.execute(
                "SELECT app, name FROM django_migrations ORDER BY id"
            )
            remaining = cur.fetchall()
            print(f"[repair_db] Remaining django_migrations ({len(remaining)} rows):")
            for r in remaining:
                print(f"  [{r[0]}] {r[1]}")

        except psycopg2.errors.UndefinedTable:
            print("[repair_db] django_migrations table does not exist yet "
                  "(fresh DB) — migrate will create it.")

    conn.close()
    print("[repair_db] Repair complete.")

except ImportError:
    print("[repair_db] psycopg2 not importable — skipping direct repair.")
except Exception as exc:
    print(f"[repair_db] Non-fatal repair error: {exc}")
    # Do NOT exit 1 — let manage.py migrate handle whatever state exists
