from pathlib import Path
import os
from decouple import config, UndefinedValueError
import firebase_admin
from firebase_admin import credentials

# --- BASE DIRECTORY ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECRET & DEBUG ---
SECRET_KEY = config("SECRET_KEY", default="django-insecure-default-key")
DEBUG = config("DEBUG", default=True, cast=bool)

# --- ALLOWED HOSTS ---
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').replace(' ', '').split(',')

# --- EMAIL / BREVO SETTINGS ---
BREVO_API_KEY = config("BREVO_API_KEY", default="dummy-key-for-ci")
BREVO_SENDER_NAME = config("BREVO_SENDER_NAME", default="SIA Project")
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="no-reply@example.com")

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- INSTALLED APPS ---
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

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URL & WSGI ---
ROOT_URLCONF = 'myproject.urls'
WSGI_APPLICATION = 'myproject.wsgi.application'

# --- TEMPLATES ---
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

# --- AUTH PASSWORD VALIDATORS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- LANGUAGE / TIMEZONE ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- PIPELINE CONFIG ---
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
]

PIPELINE = {
    'STYLESHEETS': {
        'main': {
            'source_filenames': (
                'css/main.css',
            ),
            'output_filename': 'css/main.min.css',
        },
    },
    'JAVASCRIPT': {
        'main': {
            'source_filenames': (
                'js/main.js',
            ),
            'output_filename': 'js/main.min.js',
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- FIREBASE CONFIG ---
try:
    FIREBASE_CONFIG = {
        "apiKey": config("FIREBASE_API_KEY", default="dummy"),
        "authDomain": config("FIREBASE_AUTH_DOMAIN", default="dummy.firebaseapp.com"),
        "projectId": config("FIREBASE_PROJECT_ID", default="dummy-project"),
        "storageBucket": config("FIREBASE_STORAGE_BUCKET", default="dummy.appspot.com"),
        "messagingSenderId": config("FIREBASE_MESSAGING_SENDER_ID", default="0000000000"),
        "appId": config("FIREBASE_APP_ID", default="1:0000000000:web:dummy"),
        "measurementId": config("FIREBASE_MEASUREMENT_ID", default="G-DUMMY"),
    }
except UndefinedValueError:
    FIREBASE_CONFIG = {}

# --- INITIALIZE FIREBASE ---
if not firebase_admin._apps:
    try:
        cred_path = config("FIREBASE_SERVICE_ACCOUNT", default=None)
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            print("WARNING: Firebase credentials missing. Skipping initialization.")
    except Exception as e:
        print(f"WARNING: Firebase init failed: {e}")
