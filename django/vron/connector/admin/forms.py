"""
Admin FORMS

Form definitions used by views/templates from the admin app
"""

##########################
# Imports
##########################
from django import forms
from django.forms import TextInput, CheckboxInput
from vron.core.forms import BaseModelForm, BaseForm
from vron.connector.models import Config, Log, Key
from django.conf import settings
from django.core.urlresolvers import reverse





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

    def save(self, commit=True):

        if self.instance.clear_payment_option:
            self.instance.payment_option = None
            self.instance.last_update_payment = None
            self.instance.clear_payment_option = False

        super(KeyForm, self).save()

    class Meta:
        model = Key
        fields = [ 'name', 'comments', 'payment_option', 'last_update_payment', 'clear_payment_option' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'comments': TextInput( attrs = { 'class': 'form-control' } ),
            'payment_option': TextInput( attrs = { 'class': 'form-control', 'disabled': 'disabled' } ),
            'last_update_payment': TextInput( attrs = { 'class': 'form-control', 'disabled': 'disabled' } ),
            'clear_payment_option': CheckboxInput(attrs = { 'class': 'form-control'} ),
        }


#######################
# TEST FORMS
#######################
class TestForm( BaseForm ):
    """
    Form for Testing API request
    """
    url = forms.CharField(
        required = True,
        widget = forms.TextInput( attrs = { 'placeholder':'URL', 'class': 'form-control'} )
    )
    xml = forms.CharField(
        required = True,
        widget = forms.Textarea( attrs = { 'placeholder':'XML Request', 'class': 'form-control' } )
    )
