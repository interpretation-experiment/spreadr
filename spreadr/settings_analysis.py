"""
Django settings for spreadr project for analysis of the data.
"""

# Import default settings
from spreadr.settings import *

# Hosts
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.gistr.io'
]

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
