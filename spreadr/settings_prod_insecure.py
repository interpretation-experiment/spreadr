"""
Insecure production Django settings for spreadr project.
"""

# Import default settings
from spreadr.settings import *

# Secret key
import os
SECRET_KEY = os.environ['SECRET_KEY']

# Sentry/raven
RAVEN_CONFIG = {
    'dsn': os.environ['RAVEN_DSN']
}

# No debug
DEBUG = False

# Hosts
ALLOWED_HOSTS = [
    '.gistr.io'
]

# Static files
STATIC_ROOT = 'static'
