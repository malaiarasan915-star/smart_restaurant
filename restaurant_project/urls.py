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
#   - whether menu_category actually exists in that database
# Compare this with the migrate logs (which print the same HOST/NAME) to
# confirm both the migration process and the app target the same database.
def health_check(request):
    import re
    from django.db import connection
    lines = ["=== Smart Restaurant — Health Check ===", ""]
    try:
        s = connection.settings_dict
        lines.append(f"DB Engine : {s.get('ENGINE', 'unknown')}")
        lines.append(f"DB Host   : {s.get('HOST', '(empty=localhost)')}")
        lines.append(f"DB Port   : {s.get('PORT', '(default)')}")
        lines.append(f"DB Name   : {s.get('NAME', 'unknown')}")
        lines.append(f"DB User   : {s.get('USER', 'unknown')}")
        lines.append("")

        # List all tables so we can see exactly what exists
        tables = connection.introspection.table_names()
        lines.append(f"Tables in DB ({len(tables)} total):")
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

# Always serve media files in development (required for dish images to display)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

