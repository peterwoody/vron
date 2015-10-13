"""
RON Communication class

http://wiki.respax.com.au/respax/ron_api

"""

##########################
# Imports
##########################
from django.conf import settings
import xmlrpclib





##########################
# Class definitions
##########################
class Ron( object ):
    """
    Class responsible to send requests to RON
    http://wiki.respax.com.au/respax/ron_api

    """

    def __init__( self, config_info, mode = 'train' ):
        """
        Constructor responsible to set class attributes
        and login to the RON server

        :param: Dictionary config_info
        :param: String mode
        :return: None
        """
        self.config_info = config_info
        self.host_id = ''
        self.ron_session_id = ''
        self.error_message = ''
        if mode == 'live':
            self.url = self.config_info[settings.ID_CONFIG_RON_LIVE_URL]
        else:
            self.url = self.config_info[settings.ID_CONFIG_RON_TEST_URL]

    def connect( self ):
        """
        Tries to connect to the RON server

        :return: Mixed
        """
        if self.ron_session_id:
            self.url += '&' + self.ron_session_id
        return xmlrpclib.ServerProxy( self.url )

    def login( self, reseller_id ):
        """
        Tries to login to the RON api

        :param: host_id
        :return: Boolean
        """

        # Creates XML-RPC server connection
        ron = self.connect()

        # Calls login method
        try:
            self.ron_session_id = ron.login(
                self.config_info[settings.ID_CONFIG_RON_USERNAME],
                self.config_info[settings.ID_CONFIG_RON_PASSWORD],
                reseller_id
            )
            return True
        except xmlrpclib.Fault:
            return False

    def read_tour_pickups( self, tour_code, tour_time_id, basis_id ):
        """
        Returns a list of dictionaries from the host each containing the details of a
        pickup location and time for the specified tour, time and basis combination

        :param: String tour_code
        :param: String tour_time_id
        :param: String basis_id
        :return: List
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            result = ron.readTourPickups( self.host_id, tour_code, tour_time_id, basis_id )
            return result
        except xmlrpclib.Fault:
            return False

    def write_reservation( self, reservation ):
        """
        Returns a dictionary containing a single associative array of
        extended information for the host including contact information.

        :param: Dictionary reservation
        :return: Mixed
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            result = ron.writeReservation( self.host_id, -1, reservation, { 'strPaymentOption': 'full-agent' }, {} )
            return result
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False

    def read_tour_availability( self, tour_code, basis_id, sub_basis_id, tour_date, tour_time_id ):
        """
        Returns a dictionary containing a single associative array of
        extended information for the host including contact information.

        :param: String tour_code
        :param: Int basis_id
        :param: Int sub_basis_id
        :param: String tour_date
        :param: Int tour_time_id
        :return: Mixed
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            result = ron.readTourAvailability( self.host_id, tour_code, basis_id, sub_basis_id, tour_date, tour_time_id )
            return result
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False