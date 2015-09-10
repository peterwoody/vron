"""
Dictionary extras. This file defines methods to handle dictionaries.

To use the template methods defined here you should load this module
on the desired template using: {% load dictionary_extras %}
"""

##########################
# Imports
##########################
from django import template




##########################
# Instantiate template register
##########################
register = template.Library()




##########################
# Function definitions
##########################
@register.filter( name = 'get_key' )
def get_key( dict, key ):
    """
    Returns the value of a key in a dictionary.

    :param key: The key to be catched.
    :return The value for the given key in the dictionary, or empty if not set.
    """
    try:
        return dict[key]
    except KeyError:
        return ''