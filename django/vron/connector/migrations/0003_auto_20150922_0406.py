# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0002_auto_20150922_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='external_reference',
            field=models.CharField(null=True, max_length=40, verbose_name='external reference', blank=True),
            preserve_default=True,
        ),
    ]
