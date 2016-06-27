# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='last_update_payment',
            field=models.DateTimeField(null=True, verbose_name=b'Last update payment', blank=True),
        ),
    ]
