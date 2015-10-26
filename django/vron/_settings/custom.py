# -*- coding: utf-8 -*-
"""
PROD SETTINGS

This settings will overwrite the base settings when in PROD environment
"""

##########################
# Imports
##########################
from vron._settings.base import *





#########################################
# URLs
#########################################
BASE_URL = 'https://vron.respax.com'
BASE_URL_SECURE = 'https://vron.respax.com'





#########################################
# DEBUG AND ENVIRONMENT SETTINGS
#########################################
IS_PROD = False
DEBUG = True
SQL_DEBUG = False
TEMPLATE_DEBUG = True





#########################################
# ACCESS RESTRICTIONS
#########################################
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

INTERNAL_IPS = (
    "localhost",
    "127.0.0.1",
)





#########################################
# DATABASES
#########################################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vron',
        'USER': 'vron',
        'PASSWORD': 'uhaRYush72ogHau37iO920',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}