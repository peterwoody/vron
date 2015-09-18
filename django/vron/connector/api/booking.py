"""
API Class
"""

##########################
# Imports
##########################
from vron.connector.api.api import Api
from django.conf import settings





##########################
# Class definitions
##########################
class Booking( Api ):
    """
    Booking Class. Responsible for:

     1- Reading the fields from Viator request
     2- Creating the request for RON
     3- Returning XML response to Viator
    """

    def __init__( self, xml_root ):
        """
        Constructor responsible to authenticate the request

        :param: xml_root
        :return: None
        """

        # Extends constructor from parent class for extra processing
        super( Booking, self ).__init__( xml_root )

        # Declares additional class attributes
        self.request_status = { 'Status': '', 'Error': '', 'ErrorCode': '', 'ErrorMessage': '', 'ErrorDetails': '' }
        self.transaction_status = { 'Status': '', 'RejectionReasonDetails': '', 'RejectionReason': '' }

    def process( self ):
        """
        Passes viator data and makes RON request

        :return: String
        """

        # Logs request in the background (using celery)
        self.log_request( settings.ID_LOG_STATUS_RECEIVED )

        # Validates api key
        if not self.validate_api_key():
            self.request_status['Status'] = 'ERROR'
            self.request_status['Error'] = 'ApiKey'
            self.request_status['ErrorCode'] = 'Invalid ApiKey'
            return False

        # Login to VRON
        if not self.login_ron():
            self.request_status['Status'] = 'ERROR'
            self.request_status['Error'] = 'SupplierId'
            self.request_status['ErrorCode'] = "Can't login to RON"
            return False

        # Performs booking on VRON
        #@TODO

        return True

    def format_response( self ):
        """
        Returns XML response to Viator

        :return: String
        """

        # formats xml response here
        return """<?xml version="1.0"?>
<BookingResponse xmlns="http://toursgds.com/api/01">
  <ApiKey>cdqu60CykKeca1Qc000VXwgchV000L2fNOOf0bv9gPp</ApiKey>
  <ResellerId>1000</ResellerId>
  <SupplierId>1004</SupplierId>
  <ExternalReference>10051374722992645</ExternalReference>
  <Timestamp>2015-09-17T13:46:35.000Z</Timestamp>
  <RequestStatus>
    <Status>SUCCESS</Status>
  </RequestStatus>
  <TransactionStatus>
    <Status>REJECTED</Status>
    <RejectionReasonDetails>This should contain some alternate days available.</RejectionReasonDetails>
    <RejectionReason>BOOKED_OUT_ALT_DATES</RejectionReason>
  </TransactionStatus>
  <SupplierConfirmationNumber/>
</BookingResponse>"""