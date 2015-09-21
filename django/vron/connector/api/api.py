"""
API Base

"""

##########################
# Imports
##########################
from lxml import etree, objectify
from django.conf import settings
from vron.core.util import get_object_or_false
from vron.connector.models import Config, Key
from vron.connector.tasks import log_request
import xmlrpc.client





##########################
# Class definitions
##########################
class Api( object ):
    """
    The BASE API class.  All request classes need to extend this class
    """

    def __init__( self, root_element ):
        """
        Constructor responsible set class attributes

        :param: root_element
        :return: None
        """

        # Gets all config from the DB
        config_options = Config.objects.all()
        config = {}
        for config_option in config_options:
            config[config_option.id] = config_option.value

        # Saves class attributes
        self.root_element = self.__prepare_root_element( root_element )
        self.config_info = config
        self.request_status = { 'status': '', 'error': '', 'error_code': '', 'error_message': '', 'error_details': '' }
        self.host_id = None
        self.reseller_id = None
        self.external_reference = None
        self.ron_session_id = None

    def __prepare_root_element( self, root_element ):
        """
        Parses XML root element with ixml
        :return: ixml root element
        """
        # Removes all namespace texts
        for elem in root_element.getiterator():
            if not hasattr( elem.tag, 'find' ):
                continue
            i = elem.tag.find( '}' )
            if i >= 0:
                elem.tag = elem.tag[i+1:]
        objectify.deannotate( root_element, cleanup_namespaces = True )
        return root_element

    def get_element( self, element_name ):
        """
        Gets the xml element by name
        :return: Mixed
        """
        element = self.root_element.find( element_name )
        if element == 'None':
            return None
        return element

    def get_element_text( self, element_name ):
        """
        Gets the xml element content by element name
        :return: Mixed
        """
        element = self.get_element( element_name )
        if element is not None:
            return element.text
        return None

    def validate_api_key( self ):
        """
        Checks if API key is valid
        :return: Boolean
        """

        # Searches for API Key element
        error_message = ''
        self.api_key = self.get_element_text( "ApiKey" )
        if self.api_key is not None:

            # Uses base key (set on config) to split the text and identify host id
            base_key = self.config_info[settings.ID_CONFIG_BASE_API_KEY]
            if base_key in self.api_key:
                self.host_id = self.api_key.replace( base_key, '' )

                # Searches for key/host_id in the DB
                key = get_object_or_false( Key, name =  self.host_id )
                if key:
                    return True
                error_message = 'Invalid api key'

        self.request_status['status'] = 'error'
        self.request_status['error'] = 'ApiKey'
        self.request_status['error_code'] = error_message if error_message else 'ApiKey missing'
        return False

    def log_request( self, log_status_id, error_message = None ):
        """
        Saves request info to the database
        :param: external_reference
        :param: log_status_id
        :param: error_message
        :return: Boolean
        """

        # Sets the external reference code
        self.external_reference = self.get_element_text( "ExternalReference" )

        # sends to the background with celery
        log_request.delay( self.external_reference, log_status_id, error_message )

    def ron_connect( self ):
        """
        Tries to connect to the RON server
        :return: Mixed
        """
        url = self.config_info[settings.ID_CONFIG_RON_TEST_URL]
        if self.ron_session_id:
            url += '&' + self.ron_session_id
        return xmlrpc.client.ServerProxy( url )

    def ron_login( self ):
        """
        Tries to login to the RON api
        :return: Mixed
        """

        # Creates XML-RPC server connection
        ron = self.ron_connect()

        # Gets ResellerId element
        self.reseller_id = self.get_element_text( "ResellerId" )
        if self.reseller_id is None:
            self.request_status['status'] = 'error'
            self.request_status['error'] = 'ResellerId'
            self.request_status['error_code'] = "ResellerId missing"
            return False

        # Calls login method
        try:
            self.ron_session_id = ron.login(
                self.config_info[settings.ID_CONFIG_RON_USERNAME],
                self.config_info[settings.ID_CONFIG_RON_PASSWORD],
                self.reseller_id
            )
            return self.ron_session_id
        except xmlrpc.client.Fault as error:
            self.request_status['status'] = 'error'
            self.request_status['error'] = 'ResellerId'
            self.request_status['error_code'] = 'Invalid Login for RON'
            self.request_status['error_details'] = error.faultString
            return False

    def ron_write_reservation( self, host_id, reservation ):
        """
        Returns a dictionary containing a single associative array of
        extended information for the host including contact information.
        :param: Int host_id
        :param: Dictionary reservation
        :return: Mixed
        """

        # Creates ron XML-RPC server connection
        ron = self.ron_connect()

        # Calls ron method
        try:
            result = ron.writeReservation( self.host_id, -1, reservation, { 'strPaymentOption': 'full-agent' } )
            return result
        except xmlrpc.client.Fault as error:
            return False