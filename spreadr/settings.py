"""
Django settings for spreadr project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ovn7%xtw=_$w4qaqj$9y18)^s-boet5vk*v$3at+oq)o_e06n('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

VERSION = '0.14.2'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',

    'raven.contrib.django.raven_compat',
    'solo',
    'corsheaders',
    'glue',
    'gists',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'spreadr.urls'

WSGI_APPLICATION = 'spreadr.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# REST Settings

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'spreadr.pagination.SpreadrPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
    'localhost:4200',
)

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'glue.serializers.UserSerializer'
}

OLD_PASSWORD_FIELD_ENABLED = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Gists configuration

DEFAULT_TARGET_BRANCH_DEPTH = 8
DEFAULT_TARGET_BRANCH_COUNT = 6
DEFAULT_BRANCH_PROBABILITY = 0.8

DEFAULT_READ_FACTOR = 1
DEFAULT_WRITE_FACTOR = 5
DEFAULT_MIN_TOKENS = 10
DEFAULT_PAUSE_PERIOD = 10

DEFAULT_EXPERIMENT_WORK = 50
DEFAULT_TRAINING_WORK = 5
DEFAULT_BASE_CREDIT = 0


# Caching

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}


# Solo caching (singleton models)

SOLO_CACHE = 'default'
SOLO_CACHE_TIMEOUT = 60 * 5  # 5 mins
SOLO_CACHE_PREFIX = 'solo'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Site ID, for the 'sites framework' to work, used by django-allauth
SITE_ID = 1
