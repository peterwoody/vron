"""
    String extras. This file defines methods to handle dictionaries.

    To use the template methods defined here you should load this module
    on the desired template using: {% load string_extras %}
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
@register.filter( name = 'get_class' )
def get_class( obj ):
    """
    Returns the type of the given object.
    """
    return obj.__class__.__name__