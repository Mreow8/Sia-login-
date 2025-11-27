from pathlib import Path
import os
import json
from decouple import config
import firebase_admin
from firebase_admin import credentials

# -------------------------
# Basic Django setup
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-defaultkey")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'pipeline',
    'mainapp',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
]

PIPELINE = {
    'STYLESHEETS': {
        'main': {
            'source_filenames': ('css/main.css',),
            'output_filename': 'css/main.min.css',
        },
    },
    'JAVASCRIPT': {
        'main': {
            'source_filenames': ('js/main.js',),
            'output_filename': 'js/main.min.js',
        },
    },
}

# -------------------------
# Firebase configuration
# -------------------------
FIREBASE_CONFIG = {
    "apiKey": config("FIREBASE_API_KEY"),
    "authDomain": config("FIREBASE_AUTH_DOMAIN"),
    "projectId": config("FIREBASE_PROJECT_ID"),
    "storageBucket": config("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": config("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": config("FIREBASE_APP_ID"),
    "measurementId": config("FIREBASE_MEASUREMENT_ID"),
}

# Initialize Firebase Admin using JSON from environment variable
if not firebase_admin._apps:
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if service_account_json:
        cred_dict = json.loads(service_account_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT not set in environment")

# -------------------------
# Email configuration
# -------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
