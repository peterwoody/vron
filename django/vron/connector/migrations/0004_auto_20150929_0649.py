# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


#######################
# ACTIONS
#######################
def update_log_status_values( apps, schema_editor ):

    # Get models to use (historical version)
    LogStatus = apps.get_model( "connector", "LogStatus" )

    # Updates log status
    log_status = LogStatus.objects.get( pk = 1 )
    log_status.name = 'Pending'
    log_status.save()

    log_status = LogStatus.objects.get( pk = 2 )
    log_status.name = 'Complete and Accepted'
    log_status.save()

    log_status = LogStatus.objects.get( pk = 3 )
    log_status.name = 'Complete and Rejected'
    log_status.save()

    log_status = LogStatus.objects.get( pk = 4 )
    log_status.name = 'Error on request'
    log_status.save()


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0003_auto_20150922_0406'),
    ]

    operations = [
        migrations.RunPython( update_log_status_values )
    ]
