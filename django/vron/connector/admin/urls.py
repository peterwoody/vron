"""
URLs for ADMIN panel of CONNECTOR app

https://docs.djangoproject.com/en/1.7/topics/http/urls/
"""

##########################
# Imports
##########################
from django.conf.urls import patterns, url
from vron.connector.admin import views






##########################
# URL Patterns
##########################
urlpatterns = patterns('',

    # Config
    url( r'^config/$', views.config_list, name = 'config' ),
    url( r'^config/json/$', views.config_list_json, name='config_json' ),
    url( r'^config/add/$', views.config_add, name='config_add' ),
    url( r'^config/details/(?P<config_id>\d+)$', views.config_details, name='config_details' ),
    url( r'^config/edit/(?P<config_id>\d+)$', views.config_edit, name='config_edit' ),
    url( r'^config/delete/(?P<config_id>\d+)$', views.config_delete, name='config_delete' ),

)