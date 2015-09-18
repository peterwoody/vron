# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={'default_permissions': [], 'permissions': (('admin_view_request', 'ADMIN: Can view logs'),)},
        ),
    ]
