"""
Applications configurations file.

Here you can change settings for app name, path, label, verbose_name, you can import
extra modules, etc...

Check documentation on: https://docs.djangoproject.com/en/1.7/ref/applications/
"""

##########################
# Imports
##########################
from django.apps import AppConfig





##########################
# Classes definitions
##########################
class CoreConfig( AppConfig ):
 
    name = 'vron.core'
    verbose_name = 'Core'
 
    def ready( self ):
 
        # import signal handlers
        import vron.core.signals