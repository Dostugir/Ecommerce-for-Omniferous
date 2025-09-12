"""
Django settings for ecommerce project.
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url
from urllib.parse import urlparse

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Add APP_DOMAIN from environment variable for CSRF and other uses
APP_DOMAIN = config('APP_DOMAIN', default=None)

# --- DEBUGGING PRINTS ---
print(f"DEBUG: APP_DOMAIN from env: {APP_DOMAIN}")
# --- END DEBUGGING PRINTS ---

if APP_DOMAIN:
    # Ensure ALLOWED_HOSTS includes the app domain
    _parsed_domain = APP_DOMAIN.lstrip('https://').lstrip('http://').rstrip('/')
    ALLOWED_HOSTS = [_parsed_domain]
    # For CSRF_TRUSTED_ORIGINS, we need the full scheme
    CSRF_TRUSTED_ORIGINS = [APP_DOMAIN.rstrip('/')]
else:
    # Default for local development or if APP_DOMAIN is not set
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = [] # Or include 'http://localhost:8000' for local dev

# --- DEBUGGING PRINTS ---
print(f"DEBUG: Final ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"DEBUG: Final CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
# --- END DEBUGGING PRINTS ---


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    
    # Local apps
    'store',
    'imported_products',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.categories_processor',
                'store.context_processors.cart_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# Database
# Use DATABASE_URL from environment if available, otherwise default to sqlite
_database_url = config('DATABASE_URL', default=None)

if _database_url:
    DATABASES = {
        'default': dj_database_url.config(default=_database_url)
    }
else:
    # Fallback to SQLite for local development or if DATABASE_URL is not set
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = []
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Authentication
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Allauth settings
ACCOUNT_SIGNUP_FIELDS = ['email', 'password1', 'password2']
ACCOUNT_LOGIN_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_RATE_LIMITS = {
    # 'login_failed': '5/300s', # Commented out to disable rate limiting for login failed attempts
}

# Allauth forms
ACCOUNT_FORMS = {
    'login': 'ecommerce.forms.CustomLoginForm',
}

ACCOUNT_ADAPTER = 'ecommerce.adapters.CustomAccountAdapter' # New: Custom Allauth adapter

# Email settings (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Login/Logout URLs
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Stripe settings
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='pk_test_your_stripe_public_key')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_your_stripe_secret_key')

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
CART_SESSION_ID = 'cart'

# Security settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # Crucial for cloud proxies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True # Redirect HTTP to HTTPS
    # --- DEBUGGING PRINTS ---
    print(f"DEBUG: SESSION_COOKIE_SECURE: {SESSION_COOKIE_SECURE}")
    print(f"DEBUG: CSRF_COOKIE_SECURE: {CSRF_COOKIE_SECURE}")
    print(f"DEBUG: SECURE_SSL_REDIRECT: {SECURE_SSL_REDIRECT}")
    print(f"DEBUG: SECURE_PROXY_SSL_HEADER: {SECURE_PROXY_SSL_HEADER}")
    # --- END DEBUGGING PRINTS ---
