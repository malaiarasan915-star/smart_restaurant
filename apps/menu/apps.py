from django.apps import AppConfig

class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.menu'

    def ready(self):
        # Avoid running during management commands like makemigrations or collectstatic
        import sys
        if any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'collectstatic', 'showmigrations']):
            return

        import os
        if os.path.exists("startup_error.txt"):
            try:
                os.remove("startup_error.txt")
            except Exception:
                pass

        # Run startup database repair and migration
        try:
            from django.db import connection
            from django.core.management import call_command
            
            # 1. Print diagnostic connection info
            db_engine = connection.settings_dict.get('ENGINE', '')
            db_host = connection.settings_dict.get('HOST', '')
            db_name = connection.settings_dict.get('NAME', '')
            
            print(f"[MenuConfig.ready] Django initializing. DB Engine: {db_engine}, Host: {db_host}, Name: {db_name}")
            
            if 'sqlite' in db_engine:
                print("[MenuConfig.ready] SQLite database detected. Skipping production repair/migration.")
                return
                
            # 2. Check which core tables exist using introspection
            tables = connection.introspection.table_names()
            core_tables = ["menu_category", "accounts_customuser", "orders_order"]
            missing = [t for t in core_tables if t not in tables]
            
            print(f"[MenuConfig.ready] Existing tables ({len(tables)}): {sorted(tables)[:10]}...")
            print(f"[MenuConfig.ready] Missing core tables: {missing}")
            
            # 3. If tables are missing, delete stale django_migrations records
            if missing:
                print("[MenuConfig.ready] Core tables missing! Repairing django_migrations records...")
                with connection.cursor() as cursor:
                    # Let's delete the records
                    try:
                        cursor.execute(
                            "DELETE FROM django_migrations WHERE app IN ('menu', 'orders', 'accounts')"
                        )
                        print(f"[MenuConfig.ready] Deleted stale migration records. Rows affected: {cursor.rowcount}")
                    except Exception as e:
                        print(f"[MenuConfig.ready] Error deleting stale migration records: {e}")
            
            # 4. Run migrate programmatically to create/verify all tables
            print("[MenuConfig.ready] Running programmatically: manage.py migrate...")
            call_command('migrate', interactive=False, verbosity=1)
            print("[MenuConfig.ready] Programmatic migration complete.")
            
            # 5. Verify again
            tables_after = connection.introspection.table_names()
            missing_after = [t for t in core_tables if t not in tables_after]
            if missing_after:
                print(f"[MenuConfig.ready] WARNING: Core tables still missing after migrate: {missing_after}")
            else:
                print("[MenuConfig.ready] SUCCESS: All core tables verified and present.")
                
            # 6. Auto-seed / update dishes data on startup
            if not missing_after:
                print("[MenuConfig.ready] Seeding/updating sample menu data (seed_menu)...")
                call_command('seed_menu')
                print("[MenuConfig.ready] Seeding/updating completed successfully.")
                
                # 7. Auto-create superuser if not exists
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if not User.objects.filter(is_superuser=True).exists():
                    print("[MenuConfig.ready] No superuser found! Creating default superuser...")
                    User.objects.create_superuser(
                        username='admin',
                        email='admin@example.com',
                        password='adminpassword123',
                        role='admin'
                    )
                    print("[MenuConfig.ready] Default superuser 'admin' created successfully.")
                else:
                    print("[MenuConfig.ready] Superuser already exists in database.")
                
                # 8. Auto-collect static files if STATIC_ROOT is missing or empty
                import os
                from django.conf import settings
                static_root = getattr(settings, 'STATIC_ROOT', None)
                if static_root and (not os.path.exists(static_root) or not os.listdir(static_root)):
                    print("[MenuConfig.ready] STATIC_ROOT is missing or empty! Running programmatic collectstatic...")
                    call_command('collectstatic', interactive=False, verbosity=1)
                    print("[MenuConfig.ready] Programmatic collectstatic successfully completed.")
                else:
                    print("[MenuConfig.ready] STATIC_ROOT exists and is not empty. Skipping collectstatic.")
                
        except Exception as e:
            error_msg = f"Database repair/migration/seeding/superuser/static failed during startup: {e}"
            print(f"[MenuConfig.ready] {error_msg}")
            try:
                with open("startup_error.txt", "w") as f:
                    f.write(error_msg + "\n")
            except Exception as e_file:
                print(f"[MenuConfig.ready] Failed to write startup error file: {e_file}")


