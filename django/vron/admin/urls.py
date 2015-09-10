"""
URLs for points app

https://docs.djangoproject.com/en/1.7/topics/http/urls/
"""

##########################
# Imports
##########################
from django.conf.urls import patterns, url, include
from vron.admin import views





##########################
# URL Patterns
##########################
urlpatterns = patterns('',
   
    # Home, Login, Personal Data                    
    url( r'^$', views.home_index, name='home' ),
    url( r'^login/$', views.login_index, name='login' ),
    url( r'^logout/$', views.login_logout, name='logout' ),
    url( r'^my_account/$', views.login_my_account, name='my_account' ),
    url( r'^edit_my_account/$', views.login_edit_my_account, name='edit_my_account' ),

    # CORE APP urls
    url( r'^core/', include( 'vron.core.admin.urls', namespace = "core" ) ),

)