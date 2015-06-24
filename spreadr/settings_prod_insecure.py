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
    '.gistr.io'
]

# Sentry/raven
RAVEN_CONFIG = {
    'dsn': os.environ['RAVEN_DSN']
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': 'my.cnf',
        },
    }
}

# Static files
STATIC_ROOT = 'static'
