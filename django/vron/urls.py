"""
Base URLs for all apps
https://docs.djangoproject.com/en/1.7/topics/http/urls/
"""

##########################
# Imports
##########################
from django.conf.urls import url, patterns, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect





##########################
# URL Patterns
##########################
# Include all desired apps that will have URLs
urlpatterns = patterns('',
    url( r'^admin/', include( 'vron.admin.urls', namespace = "admin" ) ),
    url( r'^$', lambda r: HttpResponseRedirect( 'admin/' ) ),
    url( r'^connector/', include( 'vron.connector.urls', namespace = "connector" ) ),
) + static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT )