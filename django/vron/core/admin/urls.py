"""
URLs for ADMIN panel of POINTS app

https://docs.djangoproject.com/en/1.7/topics/http/urls/
"""

##########################
# Imports
##########################
from django.conf.urls import patterns, url
from wannamigrate.core.admin import views






##########################
# URL Patterns
##########################
urlpatterns = patterns('',

    # Users
    url( r'^users/$', views.user_list, name='users' ),
    url( r'^users/json/$', views.user_list_json, name='user_json' ),
    url( r'^users/add/$', views.user_add, name='user_add' ),
    url( r'^users/details/(?P<user_id>\d+)$', views.user_details, name='user_details' ),
    url( r'^users/login_as_user/(?P<user_id>\d+)$', views.login_as_user, name='login_as_user' ),
    url( r'^users/edit/(?P<user_id>\d+)$', views.user_edit, name='user_edit' ),
    url( r'^users/delete/(?P<user_id>\d+)$', views.user_delete, name='user_delete' ),

    # Admin Users
    url( r'^admin_users/$', views.admin_user_list, name='admin_users' ),
    url( r'^admin_users/json/$', views.admin_user_list_json, name='admin_user_json' ),
    url( r'^admin_users/add/$', views.admin_user_add, name='admin_user_add' ),
    url( r'^admin_users/details/(?P<user_id>\d+)$', views.admin_user_details, name='admin_user_details' ),
    url( r'^admin_users/edit/(?P<user_id>\d+)$', views.admin_user_edit, name='admin_user_edit' ),
    url( r'^admin_users/delete/(?P<user_id>\d+)$', views.admin_user_delete, name='admin_user_delete' ),

    # Groups
    url( r'^groups/$', views.group_list, name='groups' ),
    url( r'^groups/json/$', views.group_list_json, name='group_json' ),
    url( r'^groups/add/$', views.group_add, name='group_add' ),
    url( r'^groups/details/(?P<group_id>\d+)$', views.group_details, name='group_details' ),
    url( r'^groups/edit/(?P<group_id>\d+)$', views.group_edit, name='group_edit' ),
    url( r'^groups/delete/(?P<group_id>\d+)$', views.group_delete, name='group_delete' ),

)