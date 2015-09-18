"""
URLs for the connector app

https://docs.djangoproject.com/en/1.7/topics/http/urls/
"""

##########################
# Imports
##########################
from django.conf.urls import patterns, url
from vron.connector import views




##########################
# URL Patterns
##########################
urlpatterns = patterns('',

    # API
    url( r'^api/$', views.api, name = 'api' ),

)