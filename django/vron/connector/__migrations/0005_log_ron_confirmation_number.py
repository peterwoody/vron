# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0004_auto_20150929_0649'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='ron_confirmation_number',
            field=models.IntegerField(verbose_name='confirmation number', blank=True, null=True),
            preserve_default=True,
        ),
    ]
