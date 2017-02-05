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
        if not "PHPSESSID" in self.url and self.ron_session_id:
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
            return ron.readTourPickups( self.host_id, tour_code, tour_time_id, basis_id )
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
            return ron.writeReservation( self.host_id, -1, reservation, { 'strPaymentOption': 'full-agent' }, {} )
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False

    def read_tour_availability_range( self, data ):
        """
        Returns a dictionary containing availability information for the
        data required

        :param: Dictionary data
        :return: Dictionary
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            return ron.readTourAvailabilityRange( data )
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False

    def read_tour_times( self, tour_code ):
        """
        Returns a list of times available for the specified tour_code

        :param: String tour_code
        :return: Dictionary
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            return ron.readTourTimes( self.host_id, tour_code )
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False

    def read_tours( self ):
        """
        Returns an array of associative arrays each containing the tour code and tour
        name for all the publicly visible tours from the specified host.

        :return: Dictionary
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            return ron.readTours( self.host_id )
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False

    def read_tour_bases( self, tour_code ):
        """
        Returns a list of bases available for the specified tour_code

        :param: String tour_code
        :return: Dictionary
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            return ron.readTourBases( self.host_id, tour_code )
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False

    def read_tour_web_details( self, tour_code ):
        """
        Returns an associative array of promotional and descriptive information for the tour.
        Due to the size of base 64 encoded images, you can optionally request that image information not
        be returned by sending false as the third parameter.

        :param: String tour_code
        :return: Dictionary
        """

        # Creates ron XML-RPC server connection
        ron = self.connect()

        # Calls ron method
        try:
            return ron.readTourWebDetails( self.host_id, tour_code, False )
        except xmlrpclib.Fault as error:
            self.error_message = error.faultString
            return False

