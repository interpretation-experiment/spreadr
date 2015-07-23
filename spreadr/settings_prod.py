"""
Insecure production Django settings for spreadr project.
"""

# Import default settings
from spreadr.settings import *

# Secret key
import os
SECRET_KEY = os.environ['SECRET_KEY']

# No debug
DEBUG = False

# Hosts
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.gistr.io'
]

# Sentry/raven
RAVEN_CONFIG = {
    'dsn': os.environ['RAVEN_DSN']
}

# Database
CONN_MAX_AGE = 300
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.environ['MY_CNF']
        },
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[Gistr.io Staff] '

# Static files
STATIC_ROOT = 'static'
