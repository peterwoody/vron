#################
# Imports
#################
from __future__ import absolute_import
from celery import shared_task
from vron.core.models import User
from vron.core.mailer import Mailer





##########################
# Celery Tasks
##########################
@shared_task
def send_welcome_email( user, type = 'user' ):
    pass
    """
    # sets user language
    preferred_language = user.preferred_language
    if not preferred_language:
        preferred_language = 'en'
    translation.activate( preferred_language )

    # sends email
    return Mailer.send_welcome_email( user, type )
    """