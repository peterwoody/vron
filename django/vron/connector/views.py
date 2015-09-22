"""
Connector Views

These are the views that control the requests received
"""

##########################
# Imports
##########################
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from lxml import etree
import requests
from vron.connector.api.booking import Booking
from vron.connector.api.availability import Availability
from vron.connector.api.batch_availability import BatchAvailability





######################
# API Views
#######################
@csrf_exempt
def api( request ):
    """
    Receives and handles a request from VIATOR

    :param: request
    :return: String
    """

    # Reads XML request from Viator
    # @TODO This is a temporary way to test VIATOR request
    # @TODO Change this to read from the Viator's POST request
    response = requests.get( "http://www.intertech.com.br/viator_request.xml" )
    xml = response.content

    # Parses XML string into object (http://lxml.de/parsing.html)
    parser = etree.XMLParser( remove_blank_text = True )
    root = etree.fromstring( xml, parser )

    # Reads root tag name to determine the kind of request call
    if 'BookingRequest' in root.tag:
        api = Booking( root )

    elif 'AvailabilityRequest' in root.tag:
        api = Availability( root )

    elif 'BatchAvailabilityRequest' in root.tag:
        api = BatchAvailability( root )

    # Process API request
    result = api.process()

    # Returns formatted response to Viator
    return HttpResponse( api.format_response() )