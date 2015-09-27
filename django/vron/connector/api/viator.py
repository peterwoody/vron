"""
Viator Class

http://supplierapitestharness.viatorinc.com/documentation.php

"""

##########################
# Imports
##########################
from vron.connector.api.xml_manager import XmlManager
from django.conf import settings
from datetime import date
from operator import itemgetter
import datetime





##########################
# Class definitions
##########################
class Viator( XmlManager ):
    """
    Viator Class. Responsible for reading the
    fields from Viator request

    """

    def __init__( self, request_xml, response_xml ):
        """
        Constructor responsible to set class attributes
        We use RON attribute names so that the mapping is clear

        :param: XmlManager xml
        :return: None
        """

        # Declares class attributes
        self.request_xml = request_xml
        self.response_xml = response_xml
        self.host_id = ''
        self.api_key = ''
        self.external_reference = ''
        self.timestamp = ''
        self.distributor_id = ''
        self.tour_code = ''
        self.tour_date = ''
        self.voucher_number = ''
        self.tour_options = ''
        self.basis_id = ''
        self.sub_basis_id = ''
        self.tour_time_id = ''
        self.pax_adults = ''
        self.pax_infants = ''
        self.pax_child = ''
        self.pax_foc = ''
        self.pax_udef1 = ''
        self.default_pickup_key = ''
        self.pickup_key = ''
        self.pickup_point = ''
        self.lead_traveller = ''
        self.first_name = ''
        self.last_name = ''
        self.traveller_identifier = ''
        self.contact_detail = ''
        self.email = ''
        self.mobile = ''

        # Viator/RON mapping
        self.booking_mapping = {
            'api_key': { 'tag': 'ApiKey', 'required': True },
            'external_reference': { 'tag': 'ExternalReference', 'required': True },
            'timestamp': { 'tag': 'Timestamp', 'required': True },
            'distributor_id': { 'tag': 'ResellerId', 'required': True },
            'tour_code': { 'tag': 'SupplierProductCode', 'required': True },
            'tour_date': { 'tag': 'TravelDate', 'required': True },
            'voucher_number': { 'tag': 'BookingReference', 'required': True },
            'tour_options': { 'tag': 'TourOptions', 'required': True },
            'basis_id': { 'tag': 'TourOptions', 'required': True },
            'sub_basis_id': { 'tag': 'TourOptions', 'required': True },
            'tour_time_id': { 'tag': 'TourOptions', 'required': True },
            'pax_adults': { 'tag': 'TourOptions', 'required': True },
            'pax_infants': { 'tag': 'TourOptions', 'required': True },
            'pax_child': { 'tag': 'TourOptions', 'required': True },
            'pax_foc': { 'tag': 'TourOptions', 'required': True },
            'pax_udef1': { 'tag': 'TourOptions', 'required': True },
            'default_pickup_key': { 'tag': 'TourOptions', 'required': True },
            'pickup_key': { 'tag': '', 'required': False },
            'pickup_point': { 'tag': 'PickupPoint', 'required': True },
            'lead_traveller': { 'tag': 'Traveller', 'required': True },
            'first_name': { 'tag': 'GivenName', 'required': True },
            'last_name': { 'tag': 'SurName', 'required': True },
            'traveller_identifier': { 'tag': 'TravellerIdentifier', 'required': True },
            'contact_detail': { 'tag': 'ContactDetail', 'required': False },
            'email': { 'tag': 'ContactValue', 'required': False },
            'mobile': { 'tag': 'ContactValue', 'required': False },
        }

    def check_booking_data( self ):
        """
        Gets all required viator data for a booking and
        checks if any is empty or missing
        :return: Mixed (True on success, String tag name on failure)
        """
        # in python2 use: booking_mapping.iteritems():
        for field, info in self.booking_mapping.items():
            if info['required']:
                value = getattr( self, 'get_' + field )()
                if value == '' or value is None:
                    return info['tag'] + ' - ' + field
        return True

    def get_content( self, field ):
        """
        Returns content of a given field
        :return: String
        """
        if getattr( self, field ) == '':
            setattr( self, field, self.request_xml.get_element_text( self.booking_mapping[field]['tag'] ) )
        return getattr( self, field )

    def get_host_id( self ):
        """
        Returns host_id attribute
        :return: String
        """
        return self.host_id

    def get_api_key( self ):
        """
        Returns ApiKey tag from root xml
        :return: String
        """
        return self.get_content( 'api_key' )

    def get_external_reference( self ):
        """
        Returns ExternalReference tag from root xml
        :return: String
        """
        return self.get_content( 'external_reference' )

    def get_timestamp( self ):
        """
        Returns Timestamp tag from root xml
        :return: String
        """
        return self.get_content( 'timestamp' )

    def get_distributor_id( self ):
        """
        Returns ResellerId tag from root xml
        :return: String
        """
        return self.get_content( 'distributor_id' )

    def get_tour_code( self ):
        """
        Returns SupplierProductCode tag from root xml
        :return: String
        """
        return self.get_content( 'tour_code' )

    def get_voucher_number( self ):
        """
        Returns BookingReference tag from root xml
        :return: String
        """
        return self.get_content( 'voucher_number' )

    def get_tour_date( self ):
        """
        Returns TravelDate converted from
        'YYYY-MM-DD' to 'DD-MMM-YYYY
        :return: String
        """
        if self.tour_date == '':
            tour_date = self.request_xml.get_element_text( self.booking_mapping['tour_date']['tag'] )
            if tour_date:
                try:
                    datetime.datetime.strptime( tour_date, '%Y-%m-%d')
                    year, month, day = itemgetter( 0, 1, 2) ( tour_date.split( '-' ) )
                    tour_date = date( int( year ), int( month ), int( day ) )
                    self.tour_date = tour_date.strftime( "%Y-%b-%d" )
                except ValueError:
                    self.tour_date = ''
        return self.tour_date

    def get_basis_id( self ):
        """
        Gets basis_id out of tour options
        :return: String
        """
        if self.basis_id == '':
            self.get_tour_options()
        return self.basis_id

    def get_sub_basis_id( self ):
        """
        Gets sub_basis_id out of tour options
        :return: String
        """
        if self.sub_basis_id == '':
            self.get_tour_options()
        return self.sub_basis_id

    def get_tour_time_id( self ):
        """
        Gets tour_time_id out of tour options
        :return: String
        """
        if self.tour_time_id == '':
            self.get_tour_options()
        return self.tour_time_id

    def get_pax_adults( self ):
        """
        Gets pax_adults out of tour options
        :return: String
        """
        if self.pax_adults == '':
            self.get_tour_options()
        return self.pax_adults

    def get_pax_infants( self ):
        """
        Gets pax_infants out of tour options
        :return: String
        """
        if self.pax_infants == '':
            self.get_tour_options()
        return self.pax_infants

    def get_pax_child( self ):
        """
        Gets pax_child out of tour options
        :return: String
        """
        if self.pax_child == '':
            self.get_tour_options()
        return self.pax_child

    def get_pax_foc( self ):
        """
        Gets pax_foc out of tour options
        :return: String
        """
        if self.pax_foc == '':
            self.get_tour_options()
        return self.pax_foc

    def get_pax_udef1( self ):
        """
        Gets pax_udef1 out of tour options
        :return: String
        """
        if self.pax_udef1 == '':
            self.get_tour_options()
        return self.pax_udef1

    def get_default_pickup_key( self ):
        """
        Gets default_pickup_key out of tour options
        :return: String
        """
        if self.default_pickup_key == '':
            self.get_tour_options()
        return self.default_pickup_key

    def get_pickup_point( self ):
        """
        Returns PickupPoint tag from root xml
        :return: String
        """
        return self.get_content( 'pickup_point' )

    def get_pickup_key( self, tour_pickups ):
        """
        Returns PickupPoint tag from root xml
        :param: Dictionary tour_pickups
        :return: String
        """
        if self.pickup_key == '':
            self.pickup_key = self.get_default_pickup_key()
            pickup_point = self.get_pickup_point()
            if pickup_point:
                if tour_pickups and len( tour_pickups ) > 0 :
                    for pickup in tour_pickups:
                        if pickup_point == pickup['strPickupName']:
                            self.pickup_key = pickup['strPickupKey']
        return self.pickup_key

    def get_first_name( self ):
        """
        Gets first_name out of lead traveller
        :return: String
        """
        if self.first_name == '':
            self.get_lead_traveller()
        return self.first_name

    def get_last_name( self ):
        """
        Gets last_name out of lead traveller
        :return: String
        """
        if self.last_name == '':
            self.get_lead_traveller()
        return self.last_name

    def get_traveller_identifier( self ):
        """
        Gets last_name out of lead traveller
        :return: String
        """
        if self.traveller_identifier == '':
            self.get_lead_traveller()
        return self.traveller_identifier

    def get_email( self ):
        """
        Gets email out of ContactDetail
        :return: String
        """
        if self.email == '':
            self.get_contact_detail()
        return self.email

    def get_mobile( self ):
        """
        Gets mobile out of ContactDetail
        :return: String
        """
        if self.mobile == '':
            self.get_contact_detail()
        return self.mobile

    def get_contact_detail( self ):
        """
        Returns ContactDetail tag from root xml
        :return: String
        """
        if self.contact_detail == '':
            self.contact_detail = self.request_xml.get_element( self.booking_mapping['contact_detail']['tag'] )
            if self.contact_detail:
                type = self.get_element_text( 'ContactType', self.contact_detail )
                if type == 'MOBILE':
                    self.mobile = self.get_element_text( 'ContactValue', self.contact_detail )
                elif type == 'EMAIL':
                    self.email = self.get_element_text( 'ContactValue', self.contact_detail )
        return self.contact_detail

    def get_lead_traveller( self ):
        """
        Retrieves TRAVELER INFORMATION to get FIRST AND LAST NAME
        :return: String
        """
        if self.lead_traveller == '':
            travellers = self.request_xml.get_element_list( self.booking_mapping['lead_traveller']['tag'] )
            if travellers:
                self.lead_traveller = travellers
                for traveller in travellers:
                    lead_traveller = self.request_xml.get_element_text( 'LeadTraveller', traveller )
                    if lead_traveller and lead_traveller == 'true':
                        self.first_name = self.request_xml.get_element_text( 'GivenName', traveller )
                        self.last_name = self.request_xml.get_element_text( 'Surname', traveller )
                        self.traveller_identifier = self.request_xml.get_element_text( 'TravellerIdentifier', traveller )
        return self.lead_traveller

    def get_tour_options( self ):
        """
        Returns TourOptions tag from root xml
        :return: String
        """
        if self.tour_options == '':
            tour_options = self.request_xml.get_element( self.booking_mapping['tour_options']['tag'] )
            if tour_options:
                self.tour_options = tour_options
                options = list( tour_options )
                for option in options:
                    name = self.request_xml.get_element_text( 'Name', option )
                    value = self.request_xml.get_element_text( 'Value', option )
                    if name and value:
                        if name == 'Basis':
                            self.get_basis_values( value )
                        elif name == 'AgeBandMap':
                            self.get_age_band_values( value )
                        elif name == 'DefaultPickup':
                            self.default_pickup_key = value
        return self.tour_options

    def get_basis_values( self, content ):
        """
        Gets basis values in format 'B=30;S=37;T=38'

        B - Basis ID
        S - Sub Basis ID
        T - Tour Time ID

        :param: String content
        :return: String
        """
        if content:
            content = content.split( ';' )
            if len( content ) > 1:
                for option in content:
                    sub_option = option.split( '=', 2 )
                    if len( sub_option ) > 1:
                        if sub_option[0] == 'B':
                            self.basis_id = sub_option[1]
                        elif sub_option[0] == 'S':
                            self.sub_basis_id = sub_option[1]
                        elif sub_option[0] == 'T':
                            self.tour_time_id = sub_option[1]

    def get_age_band_values( self, content ):
        """
        Gets AgeBandMap values in format 'A=P1;C=P1;Y=P1;I=P5;S=P1'

        A - Adults, C - Child, Y - Youth, I - Infant, S - Senior

        :param: String content
        :return: String
        """
        age_band_map = {}
        if content:

            # Retrieves and adjusts AGE BAND MAP for later usage in traveller mix
            content = content.split( ';' )
            if len( content ) > 1:
                for option in content:
                    sub_option = option.split( '=', 2 )
                    if len( sub_option ) > 1:
                        age_band_map[sub_option[0]] = sub_option[1]
                if 'A' not in age_band_map or 'C' not in age_band_map or 'Y' not in age_band_map \
                        or 'I' not in age_band_map or 'S' not in age_band_map:
                        return None

                # Retrieves TRAVELER MIX to count number of pax
                total_pax = 0
                total_pax_per_type = { 'P1': 0, 'P2': 0, 'P3': 0, 'P4': 0, 'P5': 0 }
                viator_traveler_map = { 'A': 'Adult', 'C': 'Child', 'Y': 'Youth', 'I': 'Infant', 'S': 'Senior' }
                traveller_mix = self.request_xml.get_element( 'TravellerMix' )
                if traveller_mix:
                    for ( code, tag ) in viator_traveler_map.items():
                        quantity = self.request_xml.get_element_text( tag, traveller_mix )
                        if quantity:
                            total_pax_per_type[age_band_map[code]] += int( quantity )
                            total_pax += int( quantity )
                    if total_pax > 0:
                        self.pax_adults = total_pax_per_type['P1']
                        self.pax_infants = total_pax_per_type['P2']
                        self.pax_child = total_pax_per_type['P3']
                        self.pax_foc = total_pax_per_type['P4']
                        self.pax_udef1 = total_pax_per_type['P5']

    def booking_response( self, confirmation_number, transaction_error, request_error_code = None,
                          request_error_tag = None, request_error_message = None ):
        """
        Formats response in XML for VIATOR

        :return: String
        """

        # Creates root tag to identify it as a Booking Response
        self.response_xml.create_root_element( 'BookingResponse' )

        # Creates elements to identify the booking request
        self.response_xml.create_element( 'ApiKey', None, self.get_api_key() )
        self.response_xml.create_element( 'ResellerId', None, self.get_distributor_id() )
        self.response_xml.create_element( self.request_xml.get_element( 'SupplierId' ) )
        self.response_xml.create_element( self.request_xml.get_element( 'Timestamp' ) )
        #self.response_xml.create_element( 'ExternalReference', None, self.get_external_reference() )

        # Copies the custom TourOptions made for RESPAX
        #tour_options_element = self.request_xml.get_element( 'TourOptions' )
        #self.response_xml.create_element( tour_options_element )

        # Creates elements to identify the Request Status
        request_status_element = self.response_xml.create_element( 'RequestStatus' )
        request_status = 'ERROR' if request_error_code else 'SUCCESS'
        self.response_xml.create_element( 'Status', request_status_element, request_status )
        if request_status == 'ERROR':
            request_error_element = self.response_xml.create_element( 'Error', request_status_element )
            self.response_xml.create_element( 'ErrorCode', request_error_element, request_error_code )
            self.response_xml.create_element( 'ErrorMessage', request_error_element, request_error_message )
            self.response_xml.create_element( 'ErrorDetails', request_error_element, 'Error on TAG ' + request_error_tag )

        # Creates elements to identify the traveller
        self.response_xml.create_element( 'TravellerIdentifier', None, self.get_traveller_identifier() )
        
        # Creates elements to identify the Transaction Status
        transaction_status_element = self.response_xml.create_element( 'TransactionStatus' )
        transaction_status = 'CONFIRMED' if confirmation_number else 'REJECTED'
        self.response_xml.create_element( 'Status', transaction_status_element, transaction_status )
        if transaction_status == 'REJECTED':
            reject_reason = 'Error on RON: ' + transaction_error
            self.response_xml.create_element( 'RejectionReasonDetails', transaction_status_element, reject_reason )
            self.response_xml.create_element( 'RejectionReason', transaction_status_element, 'OTHER' )

        # Creates elements to identify the booking request
        supplier_confirmation = confirmation_number if confirmation_number else ''
        self.response_xml.create_element( 'SupplierConfirmationNumber', None, supplier_confirmation )

        # Returns XML as string
        return self.response_xml.return_xml_string()