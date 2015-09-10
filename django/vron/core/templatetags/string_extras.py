"""
    String extras. This file defines methods to handle dictionaries.

    To use the template methods defined here you should load this module
    on the desired template using: {% load string_extras %}
"""
##########################
# Imports
##########################
from django import template
import re
from django.utils.translation import ugettext as _




##########################
# Instantiate template register
##########################
register = template.Library()




##########################
# Function definitions
##########################
@register.filter( name = 'truncate_smart' )
def truncate_smart( value, limit = 80 ):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}

    :param: value
    :param: limit
    :return: String
    """

    try:
        limit = int( limit )
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Make sure it's unicode
    value = str( value )

    # Return the string itself if length is smaller or equal to the limit
    if len( value ) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    # Break into words and remove the last
    words = value.split( ' ' )[:-1]

    # Join the words and return
    return ' '.join( words )


@register.filter( name = 'str_or_dash' )
def str_or_dash( value ):
    """ Returns a string or a dash if the string is empty.
        :param: value The string to be tested.
        :return: value if value is not empty or "-".
    """
    return value if len( value ) > 0 else "-"


@register.filter( name = 'yes_or_no' )
def yes_or_no( value ):
    """ Returns a string representation of a boolean. True becomes the 
        string "Yes" and False becomes "No".
        :param: value The boolean value to be converted.
        :return: Yes if value is True, No otherwise.
    """
    return "Yes" if value else "No"


@register.filter( name = 'kmi' )
def kmi( value ):
    """ Converts a number into kmi representation.
        (k -> thousand, mi -> million)
    :param value: The number to be converted
    :return: X / 1000 k if the number is greater than 1 thousand. X / 1000000 if the number is greater than 1 million.
    """
    if not value:
        return 0

    temp = int( value )
    MI = 1000000
    K = 1000

    if temp >= MI: # greater than 1 million
        if temp % MI == 0:
            return "{0} mi".format( int( temp / MI ) )
        else:
            return "{0:.1f} mi".format( float( temp / MI ) )
    elif temp >= K: # greater than 1 thousand
        if temp % K == 0:
            return "{0} k".format( int( temp / K ) )
        else:
            return "{0:.1f} k".format( float( temp / K ) )
    else:
        return str( temp )


@register.filter( name = 'remove_contact_info' )
def remove_contact_info( value ):
    """ Removes contact information (e-mail, phone number) on a string.
    :param value: The search string.
    :return: The string with its contact info replaced.
    """
    result = value

    # TODO: match str with spaces between characters
    email_pattern = "[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}"
    phone_pattern = "(00|\+)?(\d{0,3}\-?\d{1})?.?\(?(\d{2,3})\)?.?\d{3,5}.?\d{2}.?\d{2}"

    replaced_email_message = '(' + _( "e-mail address" ) + ')'
    replaced_phone_message = '(' + _( "phone number" ) + ')'

    result = re.sub( email_pattern, replaced_email_message, result )
    result = re.sub( phone_pattern, replaced_phone_message, result )

    return result