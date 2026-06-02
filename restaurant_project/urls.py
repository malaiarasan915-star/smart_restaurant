"""
URL configuration for restaurant_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse

# Health check + DB diagnostic view.
# Hitting /health/ shows:
#   - which database HOST and NAME the RUNNING app is connected to
#   - PG connection settings, current schema, search_path
#   - whether menu_category actually exists in that database
# Compare this with the migrate logs (which print the same HOST/NAME) to
# confirm both the migration process and the app target the same database.
def health_check(request):
    import io
    from django.db import connection
    from django.http import HttpResponse
    from django.core.management import call_command
    lines = ["=== Smart Restaurant — Health Check ===", ""]
    try:
        s = connection.settings_dict
        lines.append(f"DB Engine : {s.get('ENGINE', 'unknown')}")
        lines.append(f"DB Host   : {s.get('HOST', '(empty=localhost)')}")
        lines.append(f"DB Port   : {s.get('PORT', '(default)')}")
        lines.append(f"DB Name   : {s.get('NAME', 'unknown')}")
        lines.append(f"DB User   : {s.get('USER', 'unknown')}")
        
        with connection.cursor() as cursor:
            # Query current database and user in Postgres
            if 'postgresql' in s.get('ENGINE', ''):
                try:
                    cursor.execute("SELECT current_database(), current_user, current_schema(), current_setting('search_path')")
                    row = cursor.fetchone()
                    lines.append(f"PG Database: {row[0]}")
                    lines.append(f"PG User    : {row[1]}")
                    lines.append(f"PG Schema  : {row[2]}")
                    lines.append(f"PG Search Path: {row[3]}")
                except Exception as epg:
                    lines.append(f"Failed to read PG settings: {epg}")
            
            # Introspect Static Files Directory
            import os
            from django.conf import settings
            lines.append("")
            lines.append("=== Static Files Introspection ===")
            static_root = getattr(settings, 'STATIC_ROOT', None)
            lines.append(f"  STATIC_URL : {getattr(settings, 'STATIC_URL', None)}")
            lines.append(f"  STATIC_ROOT: {static_root}")
            if static_root:
                exists = os.path.exists(static_root)
                lines.append(f"  STATIC_ROOT exists: {exists}")
                if exists:
                    all_files = []
                    for root, dirs, files in os.walk(static_root):
                        for f in files:
                            rel_path = os.path.relpath(os.path.join(root, f), static_root)
                            all_files.append(rel_path)
                    lines.append(f"  Total files in STATIC_ROOT: {len(all_files)}")
                    lines.append("  Sample files in STATIC_ROOT (first 20):")
                    for f in sorted(all_files)[:20]:
                        lines.append(f"    - {f}")
                else:
                    lines.append("  STATIC_ROOT directory does not exist physically!")

            
            # Query superusers in Database
            try:
                cursor.execute("SELECT username, is_superuser, role FROM accounts_customuser WHERE is_superuser = True")
                superusers = cursor.fetchall()
                lines.append("")
                lines.append(f"Superusers in Database ({len(superusers)} total):")
                for u in superusers:
                    lines.append(f"  - {u[0]} (role={u[2]})")
            except Exception as esu:
                lines.append(f"Could not read superusers: {esu}")

            
            # Query migration history from django_migrations table
            try:
                cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY id")
                migrations = cursor.fetchall()
                lines.append("")
                lines.append(f"Migrations in django_migrations ({len(migrations)} total):")
                for app, name, applied in migrations:
                    lines.append(f"  [{'X' if applied else ' '}] {app} : {name}")
            except Exception as em:
                lines.append(f"Could not read django_migrations: {em}")

            # 1. Output all table names from information_schema.tables
            try:
                cursor.execute(
                    "SELECT table_schema, table_name "
                    "FROM information_schema.tables "
                    "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') "
                    "ORDER BY table_schema, table_name"
                )
                info_tables = cursor.fetchall()
                lines.append("")
                lines.append(f"All table names from information_schema.tables ({len(info_tables)} total):")
                for schema, name in info_tables:
                    lines.append(f"  - {schema}.{name}")
            except Exception as eit:
                lines.append(f"Could not query information_schema.tables: {eit}")

            # 2. Direct existence checks
            lines.append("")
            lines.append("=== Direct Existence Checks (information_schema.tables) ===")
            for table in ['menu_category', 'menu_dish', 'orders_order']:
                try:
                    cursor.execute(
                        "SELECT EXISTS ("
                        "  SELECT 1 "
                        "  FROM information_schema.tables "
                        "  WHERE table_name = %s"
                        ")",
                        [table]
                    )
                    exists = cursor.fetchone()[0]
                    lines.append(f"  Table '{table}' exists: {exists}")
                except Exception as eex:
                    lines.append(f"  Error checking '{table}': {eex}")
            
            # Direct count and sample rows checks
            lines.append("")
            lines.append("=== Table Row Counts & Samples ===")
            for table in ['menu_category', 'menu_dish']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    lines.append(f"  Table '{table}' row count: {count}")
                    
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    cols = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    if rows:
                        lines.append(f"  Sample rows from '{table}':")
                        for row in rows:
                            # Safely convert Decimal or other complex types to string for presentation
                            str_row = {k: str(v) for k, v in zip(cols, row)}
                            lines.append(f"    {str_row}")
                    else:
                        lines.append(f"    (No rows present in '{table}')")
                except Exception as ec:
                    lines.append(f"  Error checking '{table}' counts/samples: {ec}")
                
        # 3. Output the result of showmigrations menu, orders, accounts
        lines.append("")
        lines.append("=== Django showmigrations (menu, orders, accounts) ===")
        out = io.StringIO()
        try:
            call_command('showmigrations', 'menu', 'orders', 'accounts', stdout=out)
            lines.append(out.getvalue())
        except Exception as esm:
            lines.append(f"Failed to run showmigrations: {esm}")

        # Prefetch Queryset Diagnostic
        try:
            from apps.menu.models import Category, Dish
            from django.db.models import Prefetch
            lines.append("")
            lines.append("=== ORM Queryset & Prefetch Introspection ===")
            cats = Category.objects.prefetch_related(
                Prefetch('dishes', queryset=Dish.objects.filter(is_available=True))
            ).order_by('order')
            lines.append(f"  Categories loaded: {len(cats)}")
            for c in cats:
                dishes_all = list(c.dishes.all())
                lines.append(f"  Category '{c.name}' (id={c.id}):")
                lines.append(f"    - .dishes.count()      : {c.dishes.count()}")
                lines.append(f"    - .dishes.all() list   : {[d.name for d in dishes_all]}")
                lines.append(f"    - .dishes.all() count  : {len(dishes_all)}")
        except Exception as eorm:
            lines.append(f"  ORM introspection error: {eorm}")

        lines.append("")


        # Django connection introspection check
        tables = connection.introspection.table_names()
        lines.append(f"Tables resolved by Django introspection ({len(tables)} total):")
        for t in sorted(tables):
            lines.append(f"  {'[OK]' if t in ('menu_category','menu_dish','orders_order','accounts_customuser') else '    '} {t}")
        lines.append("")

        required = ['menu_category', 'menu_dish', 'accounts_customuser', 'orders_order', 'orders_orderitem']
        missing  = [t for t in required if t not in tables]
        if missing:
            lines.append(f"STATUS: DEGRADED — missing tables: {missing}")
            return HttpResponse("\n".join(lines), content_type="text/plain", status=500)

        lines.append("STATUS: OK — all required tables present")
        return HttpResponse("\n".join(lines), content_type="text/plain", status=200)

    except Exception as e:
        lines.append(f"STATUS: ERROR — {e}")
        return HttpResponse("\n".join(lines), content_type="text/plain", status=500)



urlpatterns = [
    path('health/', health_check, name='health_check'),   # Render health check
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='menu:list', permanent=False)),
    path('accounts/', include('apps.accounts.urls')),
    path('menu/', include('apps.menu.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payments/', include('apps.payments.urls')),
    path('admin-dashboard/', include('apps.admin_dashboard.urls')),
    path('kitchen/', include('apps.kitchen.urls')),
    path('chef/', RedirectView.as_view(url='/kitchen/', permanent=False)),
    path('supplier/', include('apps.supplier.urls')),
    path('waiter/', RedirectView.as_view(url='/supplier/', permanent=False)),
]

from django.views.static import serve
from django.urls import re_path

# Serve media files in both development and production (as we are self-hosting them)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

