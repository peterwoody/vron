"""
CORE FORMS

Here you can include base forms that will be used as parents of application
forms.

Also you can create custom form fields or methods

"""

##########################
# Imports
##########################
from django import forms





##########################
# Class definitions
##########################
class _BaseForm( object ):
    """
    The BASE form.  All forms in the system should extend this class
    """

    def get_required_fields( self, compare_with_html_id = True ):
        """
        Creates a Comma separated list of required fields
        :return: String
        """
        required_fields = []
        for field in self.fields:
            if self.fields[field].required and 'password' not in field:
                if compare_with_html_id:
                    field = 'id_' + field
                required_fields.append( field )

        return ','.join( required_fields )



class BaseModelForm( _BaseForm, forms.ModelForm ):
    """
    Making the Base Model Form use our _BaseForm
    """
    pass



class BaseForm( _BaseForm, forms.Form ):
    """
    Making the Base Form use our _BaseForm
    """
    pass
