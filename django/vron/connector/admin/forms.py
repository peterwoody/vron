"""
Admin FORMS

Form definitions used by views/templates from the admin app
"""

##########################
# Imports
##########################
from django import forms
from django.forms import TextInput
from vron.core.forms import BaseModelForm, BaseForm
from vron.connector.models import Config, Log, Key




#######################
# CONFIG FORMS
#######################
class ConfigForm( BaseModelForm ):
    """
    Form for ADD and EDIT CONFIG
    """

    class Meta:
        model = Config
        fields = [ 'name', 'value' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'value': TextInput( attrs = { 'class': 'form-control' } )
        }





#######################
# KEY FORMS
#######################
class KeyForm( BaseModelForm ):
    """
    Form for ADD and EDIT KEYS
    """

    class Meta:
        model = Key
        fields = [ 'name', 'comments' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'comments': TextInput( attrs = { 'class': 'form-control' } )
        }





#######################
# TEST FORMS
#######################
class TestForm( BaseForm ):
    """
    Form for Testing API request
    """
    xml = forms.CharField( required = True, widget = forms.Textarea( attrs = { 'placeholder':'XML Request', 'class': 'form-control' } ) )
