import os
from pathlib import Path
import dj_database_url  # இதைக் கட்டாயம் மேலே சேர்க்கவும்

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-74c^o=m1^zi@n(9r=c01z5mz+3=d0wu9fnqy*#2lrfpt!j48n%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'expenses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files Render-ல் தெரிய இது தேவை
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pk_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'expenses', 'templates')],
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

WSGI_APPLICATION = 'pk_tracker.wsgi.application'

# --- DATABASE CONFIGURATION (PostgreSQL Connection) ---
# Render-ல் DATABASE_URL இருந்தால் அதைப் பயன்படுத்தும், இல்லையெனில் உங்கள் லிங்கைப் பயன்படுத்தும்
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://pk_tracker_db_user:oTL9EcO0g1t9jAghO3amedqXvkAV3HHy@dpg-d53reo0gjchc73fe6kr0-a.virginia-postgres.render.com/pk_tracker_db',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Static files storage for Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings.py கோப்பில் இதைக் கண்டறிந்து மாற்றவும்
LOGIN_URL = 'login'  # இதைச் சேர்ப்பது மிக முக்கியம்
LOGIN_REDIRECT_URL = 'expense_list'
LOGOUT_REDIRECT_URL = 'login'