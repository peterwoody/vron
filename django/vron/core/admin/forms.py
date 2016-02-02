"""
Admin FORMS

Form definitions used by views/templates from the admin app
"""

##########################
# Imports
##########################
from django import forms
from django.forms import TextInput, SelectMultiple, HiddenInput, Select, ModelMultipleChoiceField, ModelChoiceField
from django.forms.models import BaseInlineFormSet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from vron.core.forms import BaseForm, BaseModelForm
from django.utils.translation import ugettext as _





#######################
# ADMIN USERS
#######################
class AdminUserForm( BaseModelForm ):
    """
    Form for ADD and EDIT ADMIN USERS
    """

    password = forms.CharField( required = False, label = "Password", widget = forms.PasswordInput( attrs = { 'class' : 'form-control'  } ) )
    confirm_password = forms.CharField( required = False, label = "Confirm Password", widget = forms.PasswordInput( attrs = { 'class' : 'form-control'  } ) )

    class Meta:
        model = get_user_model()
        fields = [ 'name', 'email', 'is_superuser', 'is_active', 'groups' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'email': TextInput( attrs = { 'class': 'form-control' } ),
            'groups': SelectMultiple( attrs = { 'class': 'form-control', 'style': 'height: 150px;' } )
        }

    def save( self, commit = True ):
        """
        Extra processing: Set additional default values for new users

        :return: Dictionary
        """
        user = super( AdminUserForm, self ).save( commit = False )
        user.is_admin = True
        password = self.cleaned_data["password"]
        if password:
            user.set_password( password )
        if commit:
            user.save()
            user.groups = self.cleaned_data['groups']
        return user

    def clean( self ):
        """
        Extra validation for fields that depends on other fields

        :return: Dictionary
        """
        cleaned_data = super( AdminUserForm, self ).clean()
        password = cleaned_data.get( "password" )
        confirm_password = cleaned_data.get( "confirm_password" )
        email = cleaned_data.get( "email" )

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError( "Passwords do not match." )
        else:
            try:
                user_exists = get_user_model().objects.get( email = email )
            except get_user_model().DoesNotExist:
                user_exists = False
            if not user_exists:
                raise forms.ValidationError( "You need to create a password." )
        return cleaned_data



#######################
# GROUPS AND PERMISSIONS
#######################
class GroupForm( BaseModelForm ):
    """
    Form for ADD and EDIT ADMIN USERS
    """

    class Meta:
        model = Group
        fields = [ 'name', 'permissions' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'permissions': SelectMultiple( attrs = { 'class': 'form-control', 'style': 'height: 200px;' } )
        }