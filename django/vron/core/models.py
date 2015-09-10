"""
Core model classes.

These are the models shared by all apps
"""

##########################
# Imports
##########################
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import slugify
import itertools
import pytz





##########################
# Classes definitions
##########################
class BaseModel( models.Model ):
    """
    BASE MODEL - The father of all :)
    """

    # Default timestamp fields to be used on all models
    created_date = models.DateTimeField( _( 'created date' ), auto_now_add = True, auto_now = False )
    modified_date = models.DateTimeField( _( 'modified date' ), auto_now = True, auto_now_add = False )

    # META Options
    class Meta:
        abstract = True



class UserManager( BaseUserManager ):
    """
    User Manager - part of custom auth: https://docs.djangoproject.com/en/dev/topics/auth/customizing/
    """

    def create_user( self, email, name = None, password = None, language = 'en', timezone = 'Australia/Sydney' ):
        """
        Creates and saves a User with the given email, name and password.

        :param: email
        :param: name
        :param: password
        :return: User Object
        """

        if not name:
            name = email.split( '@' )[0]

        # Validates and identify user
        if not email:
            raise ValueError( 'Users must have an email address' )
        user = self.model(
            email = self.normalize_email( email ),
            name = name,
        )

        # inserts user
        user.set_password( password )
        user.preferred_language = language
        user.preferred_timezone = timezone
        user.is_superuser = False
        user.is_admin = False
        user.is_active = True
        user.save( using = self._db )

        return user


    def create_superuser( self, email, password, name = None ):
        """
        Creates and saves a superuser with the given email, name and password.

        :param: email
        :param: password
        :param: name
        :return: User Object
        """

        user = self.create_user(email,
            password = password,
            name = name
        )
        user.is_superuser = True
        user.is_admin = True
        user.is_active = True
        user.save( using = self._db )
        return user



class User( AbstractBaseUser, PermissionsMixin, BaseModel ):
    """
    User Model - part of custom auth: https://docs.djangoproject.com/en/dev/topics/auth/customizing/
    """

    TIMEZONES = [(tz, tz) for tz in pytz.common_timezones]

    # Model Attributes
    email = models.EmailField( _( "e-mail" ), max_length = 255, unique = True )
    name = models.CharField( _( "name" ), max_length = 120, blank = False, default = '' )
    slug = models.SlugField( max_length = 200, unique = True )
    is_active = models.BooleanField( _( "is active" ), default = True )
    is_admin = models.BooleanField( _( "is admin" ), default = False )
    preferred_language = models.CharField( _( "Preferred Language" ), max_length = 6, choices = settings.LANGUAGES, default = 'en' )
    preferred_timezone = models.CharField( _( "Timezone" ), max_length = 100, choices = TIMEZONES, null = True, blank = True )

    # META Options
    class Meta:
        default_permissions = []
        permissions = (
            ( "admin_add_user", "ADMIN: Can add user" ),
            ( "admin_change_user", "ADMIN: Can change user" ),
            ( "admin_delete_user", "ADMIN: Can delete user" ),
            ( "admin_view_user", "ADMIN: Can view users" ),
            ( "admin_add_admin_user", "ADMIN: Can add admin user" ),
            ( "admin_change_admin_user", "ADMIN: Can change admin user" ),
            ( "admin_delete_admin_user", "ADMIN: Can delete admin user" ),
            ( "admin_view_admin_user", "ADMIN: Can view admin users" )
        )

    # Manager
    objects = UserManager()

    # Name of field that should be used as username
    USERNAME_FIELD = 'email'

    def get_full_name( self ):
        """ Return the user's full name """
        # The user is identified by their email address
        return self.name if self.name else self.email


    def get_short_name( self ):
        """ Return the user's short name """
        # The user is identified by their email address
        return self.email


    def __str__( self ):
        return self.email


    @property
    def is_staff( self ):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


    def generate_slug( self ):
        # Calculates the slug handling repetition
        max_length = self._meta.get_field( 'slug' ).max_length
        self.slug = orig = slugify( self.name )[:max_length]

        for x in itertools.count(1):
            if not self.__class__.objects.filter( slug = self.slug ).exists():
                break
            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            self.slug = "{0}-{1}".format( orig[ : max_length - len( str( x ) ) - 1 ], x )


    def save( self, *args, **kwargs ):
        if not self.slug:
            self.generate_slug()

        super( User, self ).save( *args, **kwargs )