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
from wannamigrate.core.forms import BaseForm, BaseModelForm
from wannamigrate.core.models import Country, Language
from wannamigrate.points.models import Question, Answer, CountryPoints, Occupation, OccupationCategory
from wannamigrate.qa.models import Topic, TopicTranslation
from wannamigrate.qa import models as qa
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.utils.translation import ugettext as _





#######################
# LOGIN / LOGOUT / MY ACCOUNT
#######################
class LoginForm( BaseForm ):
    """
    Form for LOGIN to ADMIN
    """
    email = forms.EmailField( widget = forms.TextInput( attrs = { 'placeholder':'E-mail', 'class': 'form-control' } ) )
    password = forms.CharField( widget = forms.PasswordInput( attrs = { 'placeholder': 'Password', 'class': 'form-control' } ) )



class MyAccountForm( BaseModelForm ):
    """
    Form for EDIT MY ACCOUNT
    """

    password = forms.CharField( required = False, label = "Password", widget = forms.PasswordInput( attrs = { 'class' : 'form-control'  } ) )
    confirm_password = forms.CharField( required = False, label = "Confirm Password", widget = forms.PasswordInput( attrs = { 'class' : 'form-control'  } ) )

    class Meta:
        model = get_user_model()
        fields = [ 'name', 'email' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'email': TextInput( attrs = { 'class': 'form-control' } )
        }


    def save( self, commit = True ):
        """
        If passwords are set, they need to be set on a different way

        :return: Dictionary
        """
        user = super( MyAccountForm, self ).save( commit = False )
        password = self.cleaned_data["password"]
        if password:
            user.set_password( password )
        if commit:
            user.save()
        return user


    def clean( self ):
        """
        Extra validation for fields that depends on other fields

        :return: Dictionary
        """
        cleaned_data = super( MyAccountForm, self ).clean()
        password = cleaned_data.get( "password" )
        confirm_password = cleaned_data.get( "confirm_password" )

        if password != confirm_password:
            raise forms.ValidationError( "Passwords do not match." )

        return cleaned_data





#######################
# USERS
#######################
class UserForm( BaseModelForm ):
    """
    Form for ADD and EDIT USERS
    """

    class Meta:
        model = get_user_model()
        fields = [ 'name', 'email', 'is_active' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'email': TextInput( attrs = { 'class': 'form-control' } )
        }

    def save( self, commit = True ):
        """
        Extra processing: Set additional default values for new users

        :return: Dictionary
        """
        user = super( UserForm, self ).save( commit = False )
        user.is_admin = False
        if not user.password:
            plain_password = get_user_model().objects.make_random_password()
            user.set_password( plain_password )
        if commit:
            user.save()
        return user





#######################
# ADMIN USERS
#######################
class AdminUserForm( BaseModelForm ):
    """
    Form for ADD and EDIT ADMIN USERS
    """

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
        if not user.password:
            plain_password = get_user_model().objects.make_random_password()
            user.set_password( plain_password )
        if commit:
            user.save()
            user.groups = self.cleaned_data['groups']
        return user





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





#######################
# IMMIGRATION RULES (QUESTION, ANSWERS AND POINTS)
#######################
class QuestionForm( BaseModelForm ):
    """
    Form for ADD and EDIT Questions
    """

    class Meta:
        model = Question
        fields = [ 'description', 'help_text' ]
        widgets = {
            'description': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
            'help_text': TextInput( attrs = { 'class': 'form-control' } )
        }



class AnswerForm( BaseModelForm ):
    """
    Form for ADD and EDIT Answers
    """

    class Meta:
        model = Answer
        fields = [ 'id', 'description', 'question' ]
        widgets = {
            'description': TextInput( attrs = { 'class': 'form-control' } ),
            'question': HiddenInput(),
            'id': HiddenInput()
        }

    def __init__( self, *args, **kwargs ):
        self.countries = kwargs.pop( "countries" )
        self.points_per_country = kwargs.pop( "points_per_country" )
        super( AnswerForm, self ).__init__( *args, **kwargs )
        countries = self.countries
        points_per_country = self.points_per_country
        answer_id = self.instance.id
        if countries is not None:
            for country in countries:
                name = "points_%s" % ( country.id )
                if country.id in points_per_country and answer_id in points_per_country[country.id]:
                    value = points_per_country[country.id][answer_id]
                else:
                    value = ''
                self.fields[name] = forms.IntegerField( initial = value, widget = TextInput( attrs = { 'class': 'form-control points', 'maxlength': '2', 'style': 'width: 60px; float: left;' } ) )

    def save( self, commit = True ):
        """
        Extra processing

        :return: Dictionary
        """
        answer = super( AnswerForm, self ).save( commit = True )
        for form_element_name in self.cleaned_data:
            if 'points' in form_element_name:

                # data to be saved
                country_id = form_element_name.split( '_' )[-1] # name is similar to 'points_3' where 3 is the country ID
                points = int( self.cleaned_data[form_element_name] )

                # save (update or create)
                CountryPoints.objects.update_or_create(
                    answer_id = answer.id, country_id = country_id, defaults = { 'points': points }
                )

        return answer



class BaseAnswerFormSet( BaseInlineFormSet ):
    """
    Formset for answers / country points
    """

    def __init__( self, *args, **kwargs ):

        self.countries = kwargs.pop( "countries" )
        self.points_per_country = kwargs.pop( "points_per_country" )
        super( BaseAnswerFormSet, self ).__init__( *args, **kwargs )

    def _construct_form( self, *args, **kwargs ):
        # inject extra values in each form on the formset
        kwargs['countries'] = self.countries
        kwargs['points_per_country'] = self.points_per_country
        return super( BaseAnswerFormSet, self )._construct_form( *args, **kwargs )





#######################
# OCCUPATIONS
#######################
class OccupationForm( BaseModelForm ):
    """
    Form for ADD and EDIT ADMIN USERS
    """

    countries = ModelMultipleChoiceField(
        required = True, label = "Countries",
        queryset = Country.objects.filter( immigration_enabled = True ).order_by( 'name' ),
        widget = SelectMultiple( attrs = { 'class': 'form-control', 'style': 'height: 200px;' } )
    )

    occupation_category = ModelChoiceField(
        required = False, label = "Category",
        queryset = OccupationCategory.objects.order_by( 'name' ),
        widget = Select( attrs = { 'class': 'form-control' } )
    )

    class Meta:
        model = Occupation
        fields = [ 'name', 'occupation_category', 'countries' ]
        widgets = {
            'name': TextInput( attrs = { 'class': 'form-control', 'autofocus': 'true' } ),
        }





###################################
# Q&A Forms
###################################
class AddPostForm( BaseModelForm ):
    """
    Form to create a Question or a BlogPost.
    """
    pass


class AddAnswerForm( BaseModelForm ):
    """
        Form to create an Answer or a Comment.
    """
    pass


class EditQuestionForm( BaseModelForm ):
    """
    Form to edit qa post on admin.
    """
    class Meta:
        """ Meta class describing the model and the fields required on this form. """
        model = qa.Question
        fields = [ "title", "is_anonymous", "related_topics" ]

    # Initalizing the form
    def __init__( self, *args, **kwargs ):
        super( EditQuestionForm, self ).__init__( *args, **kwargs )

        # Overrides the choices to the related_topics field.
        self.fields[ "title" ].widget = forms.Textarea()
        self.fields[ "title" ].widget.attrs[ "placeholder" ] = _( "Type your question here..." )

        # Set the class of the is_anonymous widget
        self.fields[ "is_anonymous" ].widget.attrs[ "class" ] = "checkbox"

        # Get topics relative to the language passed.
        self.fields[ "related_topics" ].choices = TopicTranslation.objects.filter( language = self.instance.language ).values_list( "topic_id", "name" )
        self.fields[ "related_topics" ].required = True
        self.fields[ "related_topics" ].widget.attrs[ "placeholder" ] = _( "Ex: Brazil, Canada, Student visa, Work visa, General immigration" ) + "..."
        # Set the class of the is_anonymous widget
        self.fields[ "is_anonymous" ].widget.attrs[ "class" ] = "checkbox"

    def clean( self, *args, **kwargs ):
        cleaned_data = super( EditQuestionForm, self ).clean( *args, **kwargs )

        # The user should select at least Canada or Australia as topic.
        if "related_topics" in cleaned_data:
            # country_topic_selected = Topic.objects.filter( id__in = cleaned_data[ "related_topics" ] ).exclude( country__isnull = True ).exists()
            immigration_enabled_countries = Country.objects.filter( immigration_enabled = True ).values_list( "id", flat = True )
            immigration_enabled_topic_selected = Topic.objects.filter( id__in = cleaned_data[ "related_topics" ], country__id__in = immigration_enabled_countries  ).exists()
            if not immigration_enabled_topic_selected:
                self.add_error( 'related_topics', _( "You need to select at least one of these countries: Australia, Canada." ) )

        return cleaned_data

    def save( self, commit = True ):
        """
            Saves the post info taking care of add the related topics to it.
            :param: commit Indicates wether to save the model or not
        """
        instance = super( EditQuestionForm, self ).save( commit )
        for topic in self.cleaned_data['related_topics']:
            instance.related_topics.add( topic )

        return instance



class EditBlogPostForm( BaseModelForm ):
    """
    Form to edit qa post on admin.
    """
    class Meta:
        """ Meta class describing the model and the fields required on this form. """
        model = qa.BlogPost
        fields = [ "title", "body", "is_anonymous" ]

    # Initalizing the form
    def __init__( self, *args, **kwargs ):
        super( EditBlogPostForm, self ).__init__( *args, **kwargs )

        # Overrides the choices to the related_topics field.
        self.fields[ "title" ].widget = forms.Textarea()
        self.fields[ "title" ].widget.attrs[ "placeholder" ] = _( "BlogPost title..." )

        # Set the class of the is_anonymous widget
        self.fields[ "is_anonymous" ].widget.attrs[ "class" ] = "checkbox"



# Topics
class AddTopicForm( BaseModelForm ):
    """
    Form to create or edit a Topic.
    """
    
    class Meta:
        """ Meta class describing the model and the fields required on this form. """
        model = Topic
        fields = [ "name", "country", "related_goals" ]


class AddTopicTranslationForm( BaseModelForm ):
    """
    Form to create or edit a Topic Translation.
    """

    class Meta:
        """ Meta class describing the model and the fields required on this form. """
        model = TopicTranslation
        fields = [ "name", "topic", "language" ]
