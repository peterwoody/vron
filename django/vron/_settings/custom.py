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
BASE_URL = 'http://vron.intertech.com.br'
BASE_URL_SECURE = 'http://vron.intertech.com.br'





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
        'ENGINE': 'mysql.connector.django',
        'NAME': 'vron',
        'USER': 'vron',
        'PASSWORD': '99pUq3PAwFjnBsdZe3',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}