# -*- coding: utf-8 -*-
"""
Django settings for portman_web project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from datetime import timedelta
import posixpath

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qepv7vyyu4-&un2-9opv6n&dwwi9p2nn14kh_dggzjyfu%on#n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# CELERY_RESULT_BACKENDcelery -A proj worker -l INFO
CELERY_RESULT_BACKEND = 'django-cache'

# CELERY_RESULT_BACKEND
CELERY_RESULT_BACKEND = 'django-db'

CELERY_TIMEZONE = "Australia/Tasmania"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['172.28.238.114', '5.202.129.160', 'localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = (
    'adminlte3',
    'adminlte3_theme',
    # 'django.contrib.admin',
    'werkzeug_debugger_runserver',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'rest_framework',
    'rest_framework_swagger',
    'architect',
    'compressor',
    'compress',
    'adminplus',
    'corsheaders',
    'users',
    'dslam',
    'router',
    'switch',
    'contact',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'x-csrftoken',)
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'PAGINATE_BY_PARAM': 'page_size',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


JWT_AUTH = {
        'JWT_SECRET_KEY': SECRET_KEY,
        'JWT_ALGORITHM': 'HS256',
        'JWT_VERIFY': True,
        'JWT_VERIFY_EXPIRATION': True,
        'JWT_LEEWAY': 0,
        'JWT_EXPIRATION_DELTA': timedelta(seconds=24 * 60 * 60),
        'JWT_ALLOW_REFRESH': True,
        'JWT_AUTH_HEADER_PREFIX': 'Token',
}

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = "users.User"
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'portman',
        'USER': 'portman',
        'PASSWORD': 'portman',
        'HOST': '5.202.129.160',
        'PORT': '5432'
    }
}

LOGIN_REDIRECT_URL = '/index/'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
ADMIN_TOOLS_MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'media'),)
COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED', False)
CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': True,
    'DOC_EXPANSION': 'list',
    'APIS_SORTER': 'alpha'
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'nfo': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
        'applogfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('', 'portmanLog.log'),
            'maxBytes': 1024*1024*15, # 15MB
            'backupCount': 10
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['applogfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
