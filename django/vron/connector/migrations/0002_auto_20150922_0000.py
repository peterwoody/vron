# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


#######################
# ACTIONS
#######################
def add_initial_config_data( apps, schema_editor ):

    # Get models to use (historical version)
    LogStatus = apps.get_model( "connector", "LogStatus" )
    Config = apps.get_model( "connector", "Config" )

    # Insert log status
    log_status = LogStatus()
    log_status.id = 1
    log_status.name = 'Received'
    log_status.save()

    log_status = LogStatus()
    log_status.id = 2
    log_status.name = 'Complete'
    log_status.save()

    log_status = LogStatus()
    log_status.id = 3
    log_status.name = 'Error on parsing VIATOR data'
    log_status.save()

    log_status = LogStatus()
    log_status.id = 4
    log_status.name = 'Error on RON call'
    log_status.save()

    # Insert basic config
    config = Config()
    config.id = 1
    config.option_name  = 'RON username'
    config.option_value = 'jose1647'
    config.save()

    config = Config()
    config.id = 2
    config.option_name  = 'RON password'
    config.option_value = '65fferua'
    config.save()

    config = Config()
    config.id = 3
    config.option_name  = 'MAX failed attempts'
    config.option_value = '5'
    config.save()

    config = Config()
    config.id = 4
    config.option_name  = 'E-mail for Error Notifications'
    config.option_value = 'humberto.mn@gmail.com'
    config.save()

    config = Config()
    config.id = 5
    config.option_name  = 'API Key Base String'
    config.option_value = '8Jkw98HQDKlhG342801shkUi3eD'
    config.save()

class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0001_initial'),
    ]

    operations = [
        migrations.RunPython( add_initial_config_data )
    ]
