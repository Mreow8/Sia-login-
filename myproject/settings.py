from pathlib import Path
import os
from decouple import config

# ---------------------------
# BASE DIR
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------
# SECRET KEY & DEBUG
# ---------------------------
SECRET_KEY = config("SECRET_KEY", default="django-insecure-dummy-key")
DEBUG = config("DEBUG", default=True, cast=bool)

# ---------------------------
# ALLOWED HOSTS
# ---------------------------
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').replace(' ', '').split(',')

# ---------------------------
# DATABASE
# ---------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------
# INSTALLED APPS
# ---------------------------
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

# ---------------------------
# MIDDLEWARE
# ---------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------
# URLS & WSGI
# ---------------------------
ROOT_URLCONF = 'myproject.urls'
WSGI_APPLICATION = 'myproject.wsgi.application'

# ---------------------------
# TEMPLATES
# ---------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Add custom template dirs if needed
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

# ---------------------------
# AUTH & PASSWORD VALIDATORS
# ---------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------
# LANGUAGE & TIME
# ---------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------
# STATIC FILES & PIPELINE
# ---------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

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

# ---------------------------
# EMAIL / OTP SETTINGS
# ---------------------------
BREVO_API_KEY = config("BREVO_API_KEY", default="dummy-key-for-ci")
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="no-reply@example.com")
BREVO_SENDER_NAME = config("BREVO_SENDER_NAME", default="SIA Project")

# ---------------------------
# FIREBASE CONFIG (JS Frontend)
# ---------------------------
FIREBASE_CONFIG = {
    "apiKey": config("FIREBASE_API_KEY", default="dummy"),
    "authDomain": config("FIREBASE_AUTH_DOMAIN", default="dummy.firebaseapp.com"),
    "projectId": config("FIREBASE_PROJECT_ID", default="dummy"),
    "storageBucket": config("FIREBASE_STORAGE_BUCKET", default="dummy.appspot.com"),
    "messagingSenderId": config("FIREBASE_MESSAGING_SENDER_ID", default="dummy"),
    "appId": config("FIREBASE_APP_ID", default="dummy"),
    "measurementId": config("FIREBASE_MEASUREMENT_ID", default="dummy"),
}

# ---------------------------
# OPTIONAL: Add Firebase Python Init here if you want it global
# ---------------------------
# You can also rely on myproject/firebase.py for initialization

# ---------------------------
# LOGIN / LOGOUT REDIRECTS
# ---------------------------
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

