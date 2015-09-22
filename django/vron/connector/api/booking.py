"""
API Class
"""

##########################
# Imports
##########################
from vron.connector.api.api import Api
from django.conf import settings
from datetime import date
from operator import itemgetter





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

        # Retrieves and adjusts TOUR CODE
        tour_code = self.get_element_text( 'SupplierProductCode' )
        if tour_code is None:
            return self.reject_booking( 'SupplierProductCode Missing' )

        # Retrieves and adjusts VOUCHER NUMBER
        voucher_number = self.get_element_text( 'BookingReference' )
        if voucher_number is None:
            return self.reject_booking( 'BookingReference Missing' )


        # Retrieves and adjusts TOUR DATE
        tour_date = self.get_element_text( 'TravelDate' )
        if tour_date is None:
            return self.reject_booking( 'TravelDate Missing' )
        year, month, day = itemgetter( 0, 1, 2) (tour_date.split( '-' ) )
        tour_date = date( int( year ), int( month ), int( day ) )
        tour_date = tour_date.strftime( "%Y-%b-%d" )

        # Retrieves TOUR OPTIONS and stores in variables for later usage
        basis_content = None
        age_band_content = None
        default_pickup_content = None
        tour_options = self.get_element( 'TourOptions' )
        if tour_options is None:
            return self.reject_booking( 'TourOptions Missing' )
        options = list( tour_options )
        for option in options:
            name = self.get_element_text( 'Name', option )
            if name == 'Basis':
                basis_content = self.get_element_text( 'Value', option )
            elif name == 'AgeBandMap':
                age_band_content = self.get_element_text( 'Value', option )
            elif name == 'DefaultPickup':
                default_pickup_content = self.get_element_text( 'Value', option )

        # Retrieves and adjusts BASIS ID, SUB BASIS ID and TOUR TIME ID
        basis_id = None
        sub_basis_id = None
        tour_time_id = None
        if basis_content is None:
            return self.reject_booking( 'Basis element Missing' )
        basis = basis_content.split( ';' )
        for option in basis:

            sub_option = option.split( '=', 2 )
            if sub_option[0] == 'B':
                basis_id = sub_option[1]
            elif sub_option[0] == 'S':
                sub_basis_id = sub_option[1]
            elif sub_option[0] == 'T':
                tour_time_id = sub_option[1]
        if basis_id is None:
            return self.reject_booking( 'Basis ID Missing' )
        if sub_basis_id is None:
            return self.reject_booking( 'Sub Basis ID Missing' )
        if tour_time_id is None:
            return self.reject_booking( 'Tour Time ID Missing' )

        """
        self.request_status['status'] = tour_date
        return True

        reservation = {
            'strCfmNo_Ext': self.external_reference,
            'strTourCode': tour_code,
            'strVoucherNo': voucher_number,
            'intBasisID': basis_id,
            'intSubBasisID': sub_basis_id,
            'dteTourDate': tour_date,
            'intTourTimeID': tour_time_id,
            'strPaxFirstName': '',
            'strPaxLastName': '',
            'strPaxEmail': '',
            'intNoPax_Adults': '',
            'intNoPax_Infant': '',
            'intNoPax_Child': '',
            'intNoPax_FOC': '',
            'intNoPax_UDef1': '',
            'strPickupKey': '',
            'strGeneralComment': '',
        }

        # Tries to confirm booking on RON
        result = self.ron_write_reservation( self.host_id, reservation )
        return result
        """

    def format_response( self ):
        """
        Returns XML response to Viator

        :return: String
        """

        if self.transaction_status['status'] != '':
            return "Transaction Error: " + self.transaction_status['rejection_reason_details']

        return "Status: " + self.request_status['status']


    def reject_booking( self, details, status = 'REJECTED', reason = 'OTHER' ):
        """
        Sets rejection variables and returns false

        :return: Boolean
        """

        self.transaction_status['status'] = status
        self.transaction_status['rejection_reason'] = reason
        self.transaction_status['rejection_reason_details'] = details

        return False