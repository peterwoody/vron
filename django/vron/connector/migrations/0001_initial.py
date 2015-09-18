# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created_date', models.DateTimeField(verbose_name='created date', auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('option_name', models.CharField(verbose_name='option name', max_length=100)),
                ('option_value', models.CharField(verbose_name='option value', max_length=100)),
            ],
            options={
                'default_permissions': [],
                'permissions': (('admin_add_config', 'ADMIN: Can add config option'), ('admin_change_config', 'ADMIN: Can change config option'), ('admin_delete_config', 'ADMIN: Can delete config option'), ('admin_view_config', 'ADMIN: Can view config options')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created_date', models.DateTimeField(verbose_name='created date', auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('external_reference', models.CharField(verbose_name='external reference', max_length=40)),
                ('error_message', models.TextField(blank=True, null=True, verbose_name='error message')),
                ('attempts', models.IntegerField(verbose_name='attempts', default=1)),
            ],
            options={
                'default_permissions': [],
                'permissions': (('admin_view_request', 'ADMIN: Can view requests'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created_date', models.DateTimeField(verbose_name='created date', auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'default_permissions': [],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='log',
            name='log_status',
            field=models.ForeignKey(to='connector.LogStatus'),
            preserve_default=True,
        ),
    ]
