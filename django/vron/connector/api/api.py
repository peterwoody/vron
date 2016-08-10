"""
API Handling Class

"""

##########################
# Imports
##########################
from django.utils import timezone
from lxml import etree, objectify
from django.conf import settings
from vron.core.mailer import Mailer
from vron.core.util import get_object_or_false
from vron.connector.models import Config, Key
from vron.connector.tasks import log_request
from vron.connector.api.xml_manager import XmlManager
from vron.connector.api.ron import Ron
from vron.connector.api.viator import Viator
from vron.core.util import date_range
from datetime import timedelta, date, datetime
from operator import itemgetter





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
            elif 'TourListRequest' in tag:
                return self.tour_list_request()
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

        key = self.update_payment_option()

        # Get tour pickups details if needed
        pickup_point = self.viator.get_pickup_point()
        pickup_key = ''
        if pickup_point:
            tour_pickups = self.ron.read_tour_pickups(
                self.viator.get_tour_code(),
                self.viator.get_tour_time_id(),
                self.viator.get_basis_id()
            )
            pickup_key = self.viator.get_pickup_key( tour_pickups )

        # Creates reservation dictionary for RON
        reservation = {
            'strCfmNo_Ext': self.viator.get_external_reference(),
            'strTourCode': self.viator.get_tour_code(),
            'strVoucherNo': self.viator.get_voucher_number(),
            'intBasisID': self.viator.get_basis_id(),
            'intSubBasisID': self.viator.get_sub_basis_id(),
            'dteTourDate': self.viator.get_tour_date(),
            'intTourTimeID': self.viator.get_tour_time_id(),
            'strPaxFirstName': self.viator.get_first_name(),
            'strPaxLastName': self.viator.get_last_name(),
            'strPaxEmail': self.viator.get_email(),
            'strPaxMobile': self.viator.get_mobile(),
            'intNoPax_Adults': self.viator.get_pax_adults(),
            'intNoPax_Infant': self.viator.get_pax_infants(),
            'intNoPax_Child': self.viator.get_pax_child(),
            'intNoPax_FOC': self.viator.get_pax_foc(),
            'intNoPax_UDef1': self.viator.get_pax_udef1(),
            'strPickupKey': pickup_key,
            'strGeneralComment': self.viator.get_general_comments(),
        }

        # Writes booking in RON
        booking_result = self.ron.write_reservation( reservation, key.payment_option)

        """
        To clarify further on the optional Pickup Point.
        Some tours in Respax
        1) do not have any pickup point
        2) have pickups but are not mandatory
        3) have pickups and are mandatory so won't book with out a pickup key.

        Scenarios

        If the Pickup Point is not sent by Viator (as now optional)
        After Trying to make booking with no pickup point (Key)
        This will be successful for scenario 1 & 2 above and return a confirmation.
        if it is mandatory (3) in Respax then it won't book and return the xml Error response below.
        so then if we could resubmitt booking attempt, Picking the first Pickup From the readTourPickups list and Insert - "No Pickup Sent" (in the comments)
        """
        if 'insufficient pickup' in self.ron.error_message.lower():
            # It means pickup is mandatory for this trip on RON
            tour_pickups = self.ron.read_tour_pickups(
                self.viator.get_tour_code(),
                self.viator.get_tour_time_id(),
                self.viator.get_basis_id()
            )
            reservation['strPickupKey'] = tour_pickups[0]['strPickupKey']
            reservation['strGeneralComment'] += ' - No Pickup Sent'
            booking_result = self.ron.write_reservation( reservation, key.payment_option )

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

        self.update_payment_option()

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

    def update_payment_option(self):

        '''

        TRAINING CHC to FULL-AGENT
        TRAINING TW to FULL-LEVY
        TRAINING AET to COMM-AGENT/BAL POB

        if the first strCode found is full-agent set full-agent
            else
        if the first strCode found is bal-agent/levy-pob
            set bal-agent/levy-pob
        else
            set full-agent AND send EMAIL to Support

        '''

        key = self.get_key_object(self.viator.get_api_key())
        today = timezone.now().today()

        if key.last_update_payment:
            expire_date = key.last_update_payment + timedelta(days=settings.UPDATE_PAYMENT_INTERVAL_DAYS)
        else:
            expire_date = today
            key.last_update_payment = today

        if today.date() >= expire_date.date():
            payment_options = self.ron.read_payment_options()
            valid_payment_options = []
            for p in payment_options:
                if p['strCode'] in settings.ALLOWED_PAYMENT_OPTIONS:
                    valid_payment_options.append(p['strCode'])

            if len(valid_payment_options) > 0:
                key.payment_option = valid_payment_options[0]

            else:
                key.payment_option = "full-agent"
                Mailer.send_wrong_payment_option(self.viator.host_id, self.mode)

            key.save()

        return key


    def tour_list_request( self ):
        """
        Receives a xml request from viator, convert the data for
        RON requirements and run an tour list request in RON

        :return: Boolean
        """
        # Logs request in the background (using celery) and mark it as 'pending'
        self.log_request( settings.ID_LOG_STATUS_PENDING, self.viator.get_external_reference() )

        # Gets all required viator data and checks if any is empty
        tour_list_empty_check = self.viator.check_tour_list_data()
        if tour_list_empty_check != True:
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR001'] )
            return self.viator.tour_list_response( '', '', 'VRONERR001', tour_list_empty_check, self.errors['VRONERR001'] )

        # Validates api key
        if not self.validate_api_key( self.viator.get_api_key() ):
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR002'] )
            return self.viator.tour_list_response( '', '', 'VRONERR002', 'ApiKey', self.errors['VRONERR002'] )

        # Logs in RON
        if not self.ron.login( self.viator.get_distributor_id() ):
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR003'] )
            return self.viator.tour_list_response( '', '', 'VRONERR003', 'ResellerId', self.errors['VRONERR003'] )

        self.update_payment_option()

        # Initial settings for the query
        tour_list = []

        # Gets a list of tours for this host/reseller
        tours = self.ron.read_tours()
        if not tours:
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR004'] )
            return self.viator.tour_list_response( '', '', 'VRONERR004', 'SupplierId', self.errors['VRONERR004'] )
        for tour in tours:

            # Reads data from this tour
            tour_info = {}
            tour_code = tour['strTourCode']
            tour_name = tour['strTourName']

            # Gets all options for this tour
            tour_times = self.ron.read_tour_times( tour_code )
            tour_bases = self.ron.read_tour_bases( tour_code )
            tour_web_details = self.ron.read_tour_web_details( tour_code )
            if tour_times and tour_bases and tour_web_details:

                # Stores relevant information from this tour (required for viator response later)
                tour_info['tour'] = {
                    'tour_code': tour_code,
                    'tour_name': tour_name,
                    'country_code': 'AU', #TODO get this from RON
                    'destination_code': 'CNS', #TODO get this from RON
                    'destination_name': 'Cairns', #TODO get this from RON
                    'tour_description': tour_web_details['strCatchPhrase'].encode( 'ascii', 'ignore' )
                }
                tour_info['options'] = []

                # Captures tour options to be stored too
                for tour_time in tour_times:
                    for tour_base in tour_bases:
                        option = {
                            'option_code': tour_base['intBasisID'],
                            'option_name': tour_base['strBasisDesc'],
                            'departure_time': tour_time['dteTourTime']['iso8601'],
                            'basis_id': tour_base['intBasisID'],
                            'sub_basis_id': tour_base['intSubBasisID'],
                            'tour_time_id': tour_time['intTourTimeID'],
                        }
                        tour_info['options'].append( option )
                tour_list.append( tour_info )

        # Nothing found
        if len( tour_list ) == 0:
            self.log_request( settings.ID_LOG_STATUS_ERROR, self.viator.get_external_reference(), self.errors['VRONERR004'] )
            return self.viator.tour_list_response( '', '', 'VRONERR004', 'SupplierProductCode', self.errors['VRONERR004'] )

        # Logs response
        self.log_request( settings.ID_LOG_STATUS_COMPLETE_APPROVED, self.viator.get_external_reference() )

        # Returnx XML formatted response
        return self.viator.tour_list_response( tour_list, self.ron.error_message )

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

        key = self.get_key_object(api_key)
        if key:
            return True
        return False

    def get_key_object(self, api_key):

        """
        returns new Key instance from database

        :return: Boolean
        """

        # Uses base key (set on config) to split the text and identify host id
        base_key = self.config_info[settings.ID_CONFIG_BASE_API_KEY]
        if api_key is not None and base_key in api_key:
            host_id = api_key.replace( base_key, '' )
            self.viator.host_id = host_id
            self.ron.host_id = host_id

            # Searches for key/host_id in the DB
            return get_object_or_false( Key, name = self.ron.host_id )

        return False

