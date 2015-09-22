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
        self.booking_result = {}

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
        content = basis_content.split( ';' )
        for option in content:
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

        # Retrieves and adjusts AGE BAND MAP for later usage in traveller mix
        age_band_map = {}
        if age_band_content is None:
            return self.reject_booking( 'AgeBandMap Missing' )
        content = age_band_content.split( ';' )
        for option in content:
            sub_option = option.split( '=', 2 )
            age_band_map[sub_option[0]] = sub_option[1]
        if 'A' not in age_band_map or 'C' not in age_band_map or 'Y' not in age_band_map \
                or 'I' not in age_band_map or 'S' not in age_band_map:
            return self.reject_booking( 'AgeBandMap content is incomplete' )

        # Retrieves TRAVELER MIX to count number of pax
        total_pax = 0
        total_pax_per_type = { 'P1': 0, 'P2': 0, 'P3': 0, 'P4': 0, 'P5': 0 }
        viator_traveler_map = { 'A': 'Adult', 'C': 'Child', 'Y': 'Youth', 'I': 'Infant', 'S': 'Senior' }
        traveller_mix = self.get_element( 'TravellerMix' )
        if traveller_mix is None:
            return self.reject_booking( 'TravellerMix Missing' )
        for ( code, tag ) in viator_traveler_map.items():
            quantity = self.get_element_text( tag, traveller_mix )
            if quantity is not None:
                total_pax_per_type[age_band_map[code]] += int( quantity )
                total_pax += int( quantity )
        if total_pax == 0:
            return self.reject_booking( 'PAX Quantities Missing' )

        # Retrieves TRAVELER INFORMATION to get FIRST AND LAST NAME
        first_name = None
        last_name = None
        travellers = self.get_element_list( 'Traveller' )
        if travellers is None:
            return self.reject_booking( 'Traveller tag Missing' )
        for traveller in travellers:
            lead_traveller = self.get_element_text( 'LeadTraveller', traveller )
            if lead_traveller is not None and lead_traveller == 'true':
                first_name = self.get_element_text( 'GivenName', traveller )
                last_name = self.get_element_text( 'Surname', traveller )
        if first_name is None or last_name is None:
            return self.reject_booking( 'First and Last Name Missing' )

        # Retrieves CONTACT DETAILS To get EMAILS or MOBILE, if available
        email = ''
        mobile = ''
        contact_detail = self.get_element( 'ContactDetail' )
        if contact_detail is not None:
            type = self.get_element_text( 'ContactType', contact_detail )
            if type == 'MOBILE':
                mobile = self.get_element_text( 'ContactValue', contact_detail )
            elif type == 'EMAIL':
                email = self.get_element_text( 'ContactValue', contact_detail )

        # Retrieves and adjusts PICKUP KEY
        pickup_key = default_pickup_content
        pickup_point = self.get_element_text( 'PickupPoint' )
        if pickup_point is None:
            return self.reject_booking( 'PickupPoint Missing' )
        tour_pickups = self.ron_read_tour_pickups( tour_code, tour_time_id, basis_id )
        if len( tour_pickups ) > 0 :
            for pickup in tour_pickups:
                if pickup_point == pickup['strPickupName']:
                    pickup_key = pickup['strPickupKey']
                    break

        # Tries to confirm booking on RON
        reservation = {
            'strCfmNo_Ext': self.external_reference,
            'strTourCode': tour_code,
            'strVoucherNo': voucher_number,
            'intBasisID': basis_id,
            'intSubBasisID': sub_basis_id,
            'dteTourDate': tour_date,
            'intTourTimeID': tour_time_id,
            'strPaxFirstName': first_name,
            'strPaxLastName': last_name,
            'strPaxEmail': email,
            'strPaxMobile': mobile,
            'intNoPax_Adults': total_pax_per_type['P1'],
            'intNoPax_Infant': total_pax_per_type['P2'],
            'intNoPax_Child': total_pax_per_type['P3'],
            'intNoPax_FOC': total_pax_per_type['P4'],
            'intNoPax_UDef1': total_pax_per_type['P5'],
            'strPickupKey': pickup_key,
            'strGeneralComment': 'First tests',
        }
        self.booking_result = self.ron_write_reservation( reservation )
        if not self.booking_result['status']:
            return self.reject_booking( self.booking_result['response'] )

    def format_response( self ):
        """
        Returns XML response to Viator

        :return: String
        """
        if self.request_status['status'] != '':
            return "REQUEST Error: " + self.request_status['status'] + " - " + self.request_status['error'] + " - " + self.request_status['error_code']
        elif self.transaction_status['status'] != '':
            return "TRANSACTION Error: " + self.transaction_status['rejection_reason_details']
        return "Booking Confirmed! Confirmation number:" + str( self.booking_result['response'] )

    def reject_booking( self, details, status = 'REJECTED', reason = 'OTHER' ):
        """
        Sets rejection variables and returns false

        :return: Boolean
        """
        self.transaction_status['status'] = status
        self.transaction_status['rejection_reason'] = reason
        self.transaction_status['rejection_reason_details'] = details
        return False