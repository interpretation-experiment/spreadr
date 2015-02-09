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

# Static files
STATIC_ROOT = '/var/www/spreadr/static'
