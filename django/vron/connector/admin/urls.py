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

    # Availability
    url( r'^list_availability_requests/$', views.list_availability_requests, name = 'list_availability_requests' ),

    # Booking
    url( r'^list_booking_requests/$', views.list_booking_requests, name = 'list_booking_requests' ),

)