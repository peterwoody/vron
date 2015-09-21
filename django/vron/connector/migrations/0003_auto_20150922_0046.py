# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0002_auto_20150922_0000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='config',
            old_name='option_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='config',
            old_name='option_value',
            new_name='value',
        ),
    ]
