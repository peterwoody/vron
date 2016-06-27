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
# PAYMENT OPTIONS
#########################################
UPDATE_PAYMENT_INTERVAL_DAYS = 30
ALLOWED_PAYMENT_OPTIONS = ['full-agent', 'bal-agent/levy-pob']
DEFAULT_PAYMENT_OPTION = ALLOWED_PAYMENT_OPTIONS[0]




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
# EMAIL SETTINGS
#########################################

# SMTP Config
ADMINS = (('Ademar Victorino', 'ademarvictorino@gmail.com'),) # ERROR EMAILS
EMAIL_PAYMENT_OPTION_TO = ["support@respax.com"]
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp-tls.respax.com'
EMAIL_HOST_USER = 'support@respax.com.au'
EMAIL_HOST_PASSWORD = '91a35021-f00d-4cae-8422-fdbdb1e52674'
EMAIL_PORT = 2525


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
    #,'default_local': {
    #    'ENGINE': 'django.db.backends.mysql',
    #    'NAME': 'vron',
    #    'USER': 'root',
    #    'PASSWORD': 'qw34rt',
    #    'HOST': '127.0.0.1',
    #    'PORT': '',
    #}
}