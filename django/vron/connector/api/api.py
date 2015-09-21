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





##########################
# Class definitions
##########################
class Api( object ):
    """
    The BASE API class.  All request classes need to extend this class
    """

    def __init__( self, xml_root ):
        """
        Constructor responsible set class attributes

        :param: xml_root
        :return: None
        """

        # Removes all namespace texts
        for elem in xml_root.getiterator():
            if not hasattr( elem.tag, 'find' ):
                continue
            i = elem.tag.find( '}' )
            if i >= 0:
                elem.tag = elem.tag[i+1:]
        objectify.deannotate( xml_root, cleanup_namespaces = True )

        # Gets all config from the DB
        config_options = Config.objects.all()
        config = {}
        for config_option in config_options:
            config[config_option.id] = config_option.value

        # Saves class attributes
        self.xml_root = xml_root
        self.config_info = config
        self.host_id = ''
        self.external_reference = ''

    def validate_api_key( self ):
        """
        Checks if API key is valid
        :return: Boolean
        """

        # Searches for API Key element
        self.api_key = self.xml_root.find( "ApiKey" )
        if self.api_key != 'None':
            self.api_key = self.api_key.text

            # Uses base key (set on config) to split the text and identify host id
            base_key = self.config_info[settings.ID_CONFIG_BASE_API_KEY]
            if base_key in self.api_key:
                self.host_id = self.api_key.replace( base_key, '' )

                # Searches for key/host_id in the DB
                return get_object_or_false( Key, name =  self.host_id )

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
        self.external_reference = self.xml_root.find( "ExternalReference" )
        if self.external_reference == 'None':
            self.external_reference = ''
        else:
            self.external_reference = self.external_reference.text

        # sends to the background with celery
        log_request.delay( self.external_reference, log_status_id, error_message )

    def login_ron( self ):
        """
        Tries to login to the RON api
        :return: Mixed
        """

        # sends login request to RON
        #@TODO
        return True