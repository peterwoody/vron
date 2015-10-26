"""
API Handling Class

"""

##########################
# Imports
##########################
from lxml import etree, objectify
from django.conf import settings
from vron.core.util import get_object_or_false
from vron.connector.models import Config, Key
from vron.connector.tasks import log_request
from vron.connector.api.xml_manager import XmlManager
from vron.connector.api.ron import Ron
from vron.connector.api.viator import Viator
from vron.core.util import date_range
from datetime import timedelta, date
from operator import itemgetter
import datetime





##########################
# Class definitions
##########################
class Api( object ):
    """
    The API class responsible to receive the request and
    redirect to the right objects

    """

    def __init__( self, xml_raw, mode = 'train' ):
        """
        Constructor responsible to set class attributes and
        to process the right request

        :param: xml_raw
        :param: mode
        :return: None
        """

        # Gets all config from the DB
        config_options = Config.objects.all()
        config = {}
        for config_option in config_options:
            config[config_option.id] = config_option.value

        # Instantiates class attributes
        self.mode = mode
        self.config_info = config
        self.request_xml = XmlManager( xml_raw )
        self.response_xml = XmlManager()
        self.ron = Ron( config, mode )
        self.viator = Viator( self.request_xml, self.response_xml )

        # Errors
        self.errors = {
            'VRONERR001': 'Malformed or missing elements',
            'VRONERR002': 'Invalid API KEY',
            'VRONERR003': 'RON authentication failed',
            'VRONERR004': 'Nothing returned',
        }

    def process( self ):
        """
        Executes the API actions and returns formatted
        xml response.

        :return: XML
        """
        # If XML is valid, gets root tag name to call appropriate API method
        if self.request_xml.validated:
            tag = self.request_xml.get_tag_name()
            if 'BookingRequest' in tag:
                return self.booking_request()
            elif 'AvailabilityRequest' in tag:
                return self.availability_request()
            else:
                return self.basic_error_response( 'Request not supported - ' + tag )
        else:
            return self.basic_error_response( self.request_xml.error_message )

    def basic_error_response( self, error_message ):
        """
        Return error response when no supported tag was found

        :param: error_message
        :return: XML
        """
        self.response_xml.create_root_element( 'Error' )
        message = self.response_xml.create_element( 'message' )
        self.response_xml.create_element_text( error_message, message )
        return self.response_xml.return_xml_string()

    def booking_request( self ):
        """
        Receives a xml request from viator, convert the data for
        RON requirments and write a reservation in RON

        :return: XML
        """
        # Logs request in the background (using celery) and mark it as 'pending'
        self.log_request( settings.ID_LOG_STATUS_PENDING, self.viator.get_external_reference() )

        # Gets all required viator data and checks if any is empty
        booking_empty_check = self.viator.check_booking_data()
        if booking_empty_check != True:
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR001'] )
            return self.viator.booking_response( '', '', 'VRONERR001', booking_empty_check, self.errors['VRONERR001'] )

        # Validates api key
        if not self.validate_api_key( self.viator.get_api_key() ):
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR002'] )
            return self.viator.booking_response( '', '', 'VRONERR002', 'ApiKey', self.errors['VRONERR002'] )

        # Logs in RON
        if not self.ron.login( self.viator.get_distributor_id() ):
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR003'] )
            return self.viator.booking_response( '', '', 'VRONERR003', 'ResellerId', self.errors['VRONERR003'] )

        # Get tour pickups in RON
        tour_pickups = self.ron.read_tour_pickups(
            self.viator.get_tour_code(),
            self.viator.get_tour_time_id(),
            self.viator.get_basis_id()
        )

        # Creates reservation dictionary for RON
        reservation = {
            'strCfmNo_Ext': self.viator.get_external_reference(),
            'strTourCode': self.viator.get_tour_code(),
            'strVoucherNo': self.viator.get_voucher_number(),
            'intBasisID': self.viator.get_basis_id(),
            'intSubBasisID': self.viator.get_sub_basis_id(),
            'dteTourDate': self.viator.get_tour_date(),
            'intTourTimeID': self.viator.get_tour_time_id(),
            'strPaxFirstName': 'TEST PLEASE DELETE' if self.mode == 'live' else self.viator.get_first_name(),
            'strPaxLastName': self.viator.get_last_name(),
            'strPaxEmail': self.viator.get_email(),
            'strPaxMobile': self.viator.get_mobile(),
            'intNoPax_Adults': self.viator.get_pax_adults(),
            'intNoPax_Infant': self.viator.get_pax_infants(),
            'intNoPax_Child': self.viator.get_pax_child(),
            'intNoPax_FOC': self.viator.get_pax_foc(),
            'intNoPax_UDef1': self.viator.get_pax_udef1(),
            'strPickupKey': self.viator.get_pickup_key( tour_pickups ),
            'strGeneralComment': self.viator.get_general_comments(),
        }

        # Writes booking in RON
        booking_result = self.ron.write_reservation( reservation )

        # Logs response
        if booking_result:
            self.log_request( settings.ID_LOG_STATUS_COMPLETE_APPROVED, self.viator.get_external_reference(), '', booking_result )
        else:
            self.log_request( settings.ID_LOG_STATUS_COMPLETE_REJECTED, self.viator.get_external_reference(), 'Rejected or Error on RON request' )

        # Returnx XML formatted response
        return self.viator.booking_response( booking_result, self.ron.error_message )

    def availability_request( self ):
        """
        Receives a xml request from viator, convert the data for
        RON requirements and run an availability check in RON

        :return: Boolean
        """
        # Logs request in the background (using celery) and mark it as 'pending'
        self.log_request( settings.ID_LOG_STATUS_PENDING, self.viator.get_external_reference() )

        # Gets all required viator data and checks if any is empty
        availability_empty_check = self.viator.check_availability_data()
        if availability_empty_check != True:
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR001'] )
            return self.viator.availability_response( '', '', 'VRONERR001', availability_empty_check, self.errors['VRONERR001'] )

        # Validates api key
        if not self.validate_api_key( self.viator.get_api_key() ):
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR002'] )
            return self.viator.availability_response( '', '', 'VRONERR002', 'ApiKey', self.errors['VRONERR002'] )

        # Logs in RON
        if not self.ron.login( self.viator.get_distributor_id() ):
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR003'] )
            return self.viator.availability_response( '', '', 'VRONERR003', 'ResellerId', self.errors['VRONERR003'] )


        # Initial settings for query
        options = []
        basis_id = self.viator.get_basis_id()
        start_date = self.viator.get_start_date()
        end_date = self.viator.get_end_date()
        tour_code = self.viator.get_tour_code()
        interval_start_date = ''
        interval_end_date = ''

        # If there's an end date, we need these 2 dates to calculate the interval
        if end_date:
            interval_start_date = self.request_xml.get_element_text( 'StartDate' )
            if interval_start_date:
                try:
                    year, month, day = itemgetter( 0, 1, 2) ( interval_start_date.split( '-' ) )
                    interval_start_date = date( int( year ), int( month ), int( day ) )
                except ValueError:
                    interval_start_date = ''
            interval_end_date = self.request_xml.get_element_text( 'EndDate' )
            if interval_end_date:
                try:
                    year, month, day = itemgetter( 0, 1, 2) ( interval_end_date.split( '-' ) )
                    interval_end_date = date( int( year ), int( month ), int( day ) )
                except ValueError:
                    interval_end_date = ''

        # Determines what product options should be searched
        if basis_id:
            base_option = {
                'strHostID': self.ron.host_id,
                'strTourCode': tour_code,
                'intBasisID': basis_id,
                'intSubBasisID': self.viator.get_sub_basis_id(),
                'intTourTimeID': self.viator.get_tour_time_id(),
                'dteTourDate': start_date,
            }
            options.append( base_option )

            # if there's and END-DATE here, add all dates in the interval to the options
            if interval_start_date and interval_end_date:
                count = 0
                for single_date in date_range( interval_start_date, interval_end_date ):
                    if count:
                        option = {
                            'strHostID': base_option['strHostID'],
                            'strTourCode': base_option['strTourCode'],
                            'intBasisID': base_option['intBasisID'],
                            'intSubBasisID': base_option['intSubBasisID'],
                            'intTourTimeID': base_option['intTourTimeID'],
                            'dteTourDate': single_date.strftime( "%Y-%b-%d" ),
                        }
                        options.append( option )
                    count += 1
        else:

            # Gets all options for this product
            tour_times = self.ron.read_tour_times( tour_code )
            tour_bases = self.ron.read_tour_bases( tour_code )
            if not tour_times or not tour_bases:
                self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR004'] )
                return self.viator.availability_response( '', '', 'VRONERR004', 'SupplierProductCode', self.errors['VRONERR004'] )
            for tour_time in tour_times:
                for tour_base in tour_bases:
                    base_option = {
                        'strHostID': self.ron.host_id,
                        'strTourCode': tour_code,
                        'intBasisID': tour_base['intBasisID'],
                        'intSubBasisID': tour_base['intSubBasisID'],
                        'intTourTimeID': tour_time['intTourTimeID'],
                        'dteTourDate': start_date,
                    }
                    options.append( base_option )
                    if interval_start_date and interval_end_date:
                        count = 0
                        for single_date in date_range( interval_start_date, interval_end_date ):
                            if count:
                                option = {
                                    'strHostID': base_option['strHostID'],
                                    'strTourCode': base_option['strTourCode'],
                                    'intBasisID': base_option['intBasisID'],
                                    'intSubBasisID': base_option['intSubBasisID'],
                                    'intTourTimeID': base_option['intTourTimeID'],
                                    'dteTourDate': single_date.strftime( "%Y-%b-%d" ),
                                }
                                options.append( option )
                            count += 1

        # Makes availability request in RON
        availability_results = self.ron.read_tour_availability_range( options )

        # Logs response
        self.log_request( settings.ID_LOG_STATUS_COMPLETE_APPROVED, self.viator.get_external_reference() )

        # Returnx XML formatted response
        return self.viator.availability_response( availability_results, self.ron.error_message )

    def log_request( self, log_status_id, external_reference, error_message = None, confirmation_number = None ):
        """
        Saves request info to the database

        :param: log_status_id
        :param: external_reference
        :param: error_message
        :param: confirmation_number
        :return: Boolean
        """
        # sends to the background with celery
        log_request( external_reference, log_status_id, error_message, confirmation_number )

    def validate_api_key( self, api_key ):
        """
        Checks if API key is valid

        :return: Boolean
        """
        # Uses base key (set on config) to split the text and identify host id
        base_key = self.config_info[settings.ID_CONFIG_BASE_API_KEY]
        if api_key is not None and base_key in api_key:
            host_id = api_key.replace( base_key, '' )
            self.viator.host_id = host_id
            self.ron.host_id = host_id

            # Searches for key/host_id in the DB
            key = get_object_or_false( Key, name = self.ron.host_id )
            if key:
                return True
        return False