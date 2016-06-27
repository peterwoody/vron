# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0006_auto_20160622_0046'),
    ]

    operations = [
        migrations.AddField(
            model_name='key',
            name='clear_payment_option',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='key',
            name='payment_option',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Payment option', blank=True),
        ),
    ]
