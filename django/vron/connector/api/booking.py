"""
API Class
"""

##########################
# Imports
##########################
from vron.connector.api.api import Api
from django.conf import settings
import xmlrpc.client




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

    def __init__( self, root_element ):
        """
        Constructor responsible to authenticate the request

        :param: xml_root
        :return: None
        """

        # Declares additional class attributes
        self.transaction_status = { 'status': '', 'rejection_reason_details': '', 'rejection_reason': '' }

        # Extends constructor from parent class for extra processing
        super( Booking, self ).__init__( root_element )



    def process( self ):
        """
        Process viator data and makes RON request

        :return: String
        """

        # Logs request in the background (using celery)
        self.log_request( settings.ID_LOG_STATUS_RECEIVED )

        # Validates api key
        if not self.validate_api_key():
            return False

        # Logs in VRON
        if not self.ron_login():
            return False

        # Gets and adjusts tour code
        tour_code = self.get_element_text( 'SupplierProductCode' )
        if tour_code is None:
            self.transaction_status['status'] = 'REJECTED'
            self.transaction_status['rejection_reason'] = 'SupplierProductCode Missing'
            self.transaction_status['rejection_reason_details'] = 'SupplierProductCode Missing'

        reservation = {
            'strTourCode': tour_code,
            'intBasisID': '',
            'intSubBasisID': '',
            'dteTourDate': '',
            'intTourTimeID': '',
            'strPaxFirstName': '',
            'strPaxLastName': '',
            'strPaxEmail': '',
            'intNoPax_Adults': '',
            'strGeneralComment': '',
        }

        # Tries to confirm booking on RON
        result = self.ron_write_reservation( self.host_id, reservation )
        return result

    def format_response( self ):
        """
        Returns XML response to Viator

        :return: String
        """

        return "Status: " + self.request_status['status'] + " Error: " +  self.request_status['error'] + " ErrorCode: " +  self.request_status['error_code']

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