import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (local dev only)
load_dotenv(BASE_DIR / '.env')

# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS: supports comma-separated list + auto-detects Render hostname
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ─── Apps ─────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'channels',
    'corsheaders',

    # Local apps
    'apps.accounts',
    'apps.menu',
    'apps.orders',
    'apps.kitchen',
    'apps.supplier',
    'apps.payments',
    'apps.notifications',
    'apps.admin_dashboard',
]

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # Serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',            # CORS (before CommonMiddleware)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'restaurant_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'restaurant_project.wsgi.application'
ASGI_APPLICATION = 'restaurant_project.asgi.application'

# ─── Database ────────────────────────────────────────────────────────────────
# Database — PostgreSQL on Render (DATABASE_URL), SQLite locally
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            # ssl_require is intentionally omitted: Render's DATABASE_URL already
            # includes sslmode=require in the connection string. Setting it here
            # separately can cause SSL negotiation failures on the internal network.
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── Password Validation ─────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalisation ────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ─── Static & Media Files ────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── Authentication ──────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# ─── Django Channels (WebSockets) ────────────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# ─── CORS Configuration ───────────────────────────────────────────────────────
# Since this is a Django-only project (templates served by Django),
# CORS is only needed for API calls from external clients.
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

# In production, set CORS_ALLOWED_ORIGINS env var instead of allowing all
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

# ─── Security Headers (Production) ───────────────────────────────────────────
# IMPORTANT: SECURE_SSL_REDIRECT is intentionally NOT set here.
# On Render, the build phase runs `python manage.py migrate` with DEBUG=False.
# If SECURE_SSL_REDIRECT=True during that phase, Django's internal HTTP client
# gets redirect-looped, causing migrations to fail or the health check to fail.
# Render's load balancer already enforces HTTPS externally — we only need
# SECURE_PROXY_SSL_HEADER so Django knows requests arrived over HTTPS.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Do NOT set SECURE_SSL_REDIRECT = True on Render — Render's edge handles it
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ─── Razorpay Payment Gateway ─────────────────────────────────────────────────
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_dummy_key_id')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'dummy_key_secret_12345')
BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8000')

# ─── Misc ─────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
