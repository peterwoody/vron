"""
Admin FORMS

Form definitions used by views/templates from the admin app
"""

##########################
# Imports
##########################
from django import forms
from django.forms import TextInput
from vron.core.forms import BaseModelForm
from vron.connector.models import Config, Log




#######################
# CONFIG FORMS
#######################
class ConfigForm( BaseModelForm ):
    """
    Form for ADD and EDIT CONFIG
    """

    class Meta:
        model = Config
        fields = [ 'option_name', 'option_value' ]
        widgets = {
            'option_name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'option_value': TextInput( attrs = { 'class': 'form-control' } )
        }