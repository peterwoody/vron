# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0005_log_ron_confirmation_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='key',
            name='last_update_payment',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='key',
            name='payment_option',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Payment options', blank=True),
            preserve_default=True,
        ),
    ]
