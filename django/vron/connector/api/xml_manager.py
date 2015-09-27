"""
XML Manager Class

All xml manipulation is done by this class, so that
we can easily replace the third party library used.

We're using http://lxml.de/

"""

##########################
# Imports
##########################
from lxml import etree, objectify
from django.utils.html import strip_spaces_between_tags
import re





##########################
# Class definitions
##########################
class XmlManager( object ):
    """
    All xml manipulation is done by this class, so that
    we can easily replace the third party library used

    """

    def __init__( self, xml_raw = None ):
        """
        Constructor responsible to set class attributes

        :param: String xml_raw
        :return: None
        """
        # Instantiates class attributes
        self.xml_root = None
        self.error_message = None
        self.validated = True

        # Loads raw xml
        if xml_raw is not None:
            self.validated = self.validate_and_load( xml_raw )

    def validate_and_load( self, xml_raw ):
        """
        Validate XML content

        :param: xml_raw
        :return: Mixed - False on failure, lxml root on success
        """

        # Removes space in the beginning and end
        xml_raw = xml_raw.strip()

        # Tests if it's empty
        if xml_raw == '':
            self.error_message = 'The content was empty'
            return False

        # Checks if the xml came URL encoded
        if xml_raw[:5] == 'data=':
            url_encoded = xml_raw.split( '=', 1 )
            xml_raw = url_encoded[1]

        # Removes empty spaces between tags
        xml = strip_spaces_between_tags( xml_raw )
        xml = re.sub( r'^\s+<', '<', xml )

        # Tests if it starts with a tag
        if xml == '' or xml[0] != '<':
            self.error_message = 'Invalid XML - Missing starting tag'
            return False

        # Tries to parse with lxml
        try:
            parser = etree.XMLParser( remove_blank_text = True )
            xml_root = etree.fromstring( bytes( xml, 'utf-8' ), parser )
            self.xml_root = self.cleanup( xml_root )
            return True
        except etree.XMLSyntaxError as error:
            self.error_message = "Malformed xml (" + str( error ) + ")"
            return False

    def cleanup( self, xml_root ):
        """
        Cleanup ixml object

        :param: xml_raw
        :return: Mixed - False on failure, ixml root object on success
        """

        # Removes all namespace texts
        for elem in xml_root.getiterator():
            if not hasattr( elem.tag, 'find' ):
                continue
            i = elem.tag.find( '}' )
            if i >= 0:
                elem.tag = elem.tag[i+1:]
        objectify.deannotate( xml_root, cleanup_namespaces = True )
        return xml_root

    def get_root_element( self ):
        """
        Create root element

        :return: lxml root element
        """
        return self.xml_rooot

    def create_root_element( self, element_name ):
        """
        Create root element

        :param: String element_name
        :return: Boolean
        """
        self.xml_root = etree.Element( element_name, xmlns = "http://toursgds.com/api/01" )
        return True

    def get_tag_name( self, element = None, base_element = None ):
        """
        Returns root tag name

        :param: Mixed String element or lxml element object
        :param: lxml object base_element
        :return: Mixed
        """
        if element is None:
            element = self.xml_root
        if not etree.iselement( element ):
            element = self.get_element( element, base_element )
        return element.tag

    def get_element( self, element_name, base_element = None ):
        """
        Gets the xml element by name (if there are multiple elements, only
        the first one is returned). Use 'get_element_list' for that.

        :param: String element_name
        :param: Lxml element base_element
        :return: Mixed
        """
        if base_element is not None:
            if not etree.iselement( base_element ):
                return None
        else:
            base_element = self.xml_root
        element = base_element.find( element_name )
        if element == 'None':
            return None
        return element

    def create_element( self, element, base_element = None, text = None ):
        """
        Create new child element

        :param: String element
        :param: Lxml element base_element
        :return: Mixed lxml element on success, None on failure
        """
        if base_element is None:
            base_element = self.xml_root
        if etree.iselement( base_element ):
            if etree.iselement( element ):
                base_element.append( element )
            else:
                element = etree.SubElement( base_element, element )
                if text:
                    element.text = str( text )
            return element
        return None

    def get_element_text( self, element, base_element = None ):
        """
        Gets the xml element content by element name

        :param: Mixed String element or lxml element object
        :param: Lxml element base_element
        :return: Mixed
        """
        if etree.iselement( element ):
            return element.text
        element = self.get_element( element, base_element )
        if element is not None:
            return element.text
        return None

    def create_element_text( self, text, element, base_element = None ):
        """
        Sets the content of a tag

        :param: Mixed String element_name or lxml element object
        :param: String text
        :param: Lxml element base_element
        :return: Boolean
        """
        if not etree.iselement( element ):
            element = self.get_element( element, base_element )
            if element is None:
                return False
        element.text = text
        return True

    def get_element_list( self, element_name, base_element = None ):
        """
        Gets a list of xml elements by name

        :param: String element_name
        :param: Lxml element base_element
        :return: Mixed
        """
        if base_element is None:
            base_element = self.xml_root
        elements = base_element.findall( element_name )
        if elements == 'None':
            return None
        return elements

    def return_xml_string( self, element = None ):
        """
        Create root element

        :param: Lxml Object element
        :return: String
        """
        if element is None:
            element = self.xml_root
        return etree.tostring( element, pretty_print = True, xml_declaration = True, encoding = 'UTF-8' )