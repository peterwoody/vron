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
    config.name  = 'RON username'
    config.value = 'jose1647'
    config.save()

    config = Config()
    config.id = 2
    config.name  = 'RON password'
    config.value = '65fferua'
    config.save()

    config = Config()
    config.id = 3
    config.name  = 'RON Test Server'
    config.value = 'https://ron.respax.com.au:30443/section/xmlrpc/server-ron.php?config=train'
    config.save()

    config = Config()
    config.id = 4
    config.name  = 'RON Live Server'
    config.value = 'https://ron.respax.com.au:30443/section/xmlrpc/server-ron.php?config=live'
    config.save()

    config = Config()
    config.id = 5
    config.name  = 'MAX failed attempts'
    config.value = '5'
    config.save()

    config = Config()
    config.id = 6
    config.name  = 'E-mail for Error Notifications'
    config.value = 'humberto.mn@gmail.com'
    config.save()

    config = Config()
    config.id = 7
    config.name  = 'API Key Base String'
    config.value = '8Jkw98HQDKlhG342801shkUi3eD'
    config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0001_initial'),
    ]

    operations = [
        migrations.RunPython( add_initial_config_data )
    ]
