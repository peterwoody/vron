"""
Class responsible to send-out all system emails

Usage:

Mailer.send_welcome_email( user )

"""

##########################
# Imports
##########################
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.urlresolvers import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext as _





##########################
# Class definitions
##########################
class Mailer( object ):

    @staticmethod
    def send( subject, body, to, from_email = None, cc = None, bcc = None, attachments = None ):
        """
        Send the email using Django's EmailMessage class

        :param: subject
        :param: body
        :param: to
        :param: from_email
        :param: cc
        :param: bcc
        :param: attachments
        :return: String
        """

        if not settings.IS_PROD:
            return True

        email = EmailMessage()
        email.content_subtype = "html"
        email.subject = subject
        email.body = body
        email.to = [to] if isinstance( to, str ) else to
        if from_email:
            email.from_email = from_email
        if cc:
            email.cc = [cc] if isinstance( cc, str ) else cc
        if bcc:
            email.bcc = [bcc] if isinstance( bcc, str ) else bcc
        if attachments:
            for attachment in attachments:
                email.attach( attachment )

        return email.send()


    @staticmethod
    def build_body_from_template( template_path, template_data = None ):
        """
        Returns generated HTML from django template

        :param: template_path
        :param: template_data
        :return: String
        """

        template = get_template( template_path )
        template_data['base_url'] = settings.BASE_URL
        template_data['base_url_secure'] = settings.BASE_URL_SECURE
        context = Context( template_data )
        content = template.render( context )
        return content


    @staticmethod
    def send_welcome_email( user, type = 'user' ):
        """
        Sends welcome email to users

        :param: user
        """
        pass
        """
        if type == 'service-provider':
            bcc = settings.EMAIL_NOTIFICATION_PROVIDER_SIGNUP
            template_file = 'welcome_provider.html'
        else:
            bcc = None
            template_file = 'welcome_user.html'

        template_data = { 'user': user }
        body = Mailer.build_body_from_template( 'emails/' + template_file, template_data )
        return Mailer.send( _( 'Welcome to Wanna Migrate' ), body, user.email, None, None, bcc )
        """