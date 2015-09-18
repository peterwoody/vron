"""
Tasks for the connector app, including celery tasks

"""

##########################
# Imports
##########################
from __future__ import absolute_import
from celery import shared_task
from django.db.models import F
from vron.connector.models import Log





##########################
# Celery Tasks
##########################
@shared_task
def log_request( external_reference, log_status_id, error_message ):

    log, created = Log.objects.get_or_create(
        external_reference = external_reference,
        defaults = {
            'external_reference': external_reference,
            'log_status_id': log_status_id,
            'error_message': error_message,
            'attempts': 0,
        }
    )
    if not created:
        log.attempts = F( 'attempts' ) + 1
        log.save()