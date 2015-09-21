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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('option_name', models.CharField(max_length=100, verbose_name='option name')),
                ('option_value', models.CharField(max_length=100, verbose_name='option value')),
            ],
            options={
                'permissions': (('admin_add_config', 'ADMIN: Can add config option'), ('admin_change_config', 'ADMIN: Can change config option'), ('admin_delete_config', 'ADMIN: Can delete config option'), ('admin_view_config', 'ADMIN: Can view config options')),
                'default_permissions': [],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('name', models.CharField(max_length=20, verbose_name='name')),
                ('comments', models.CharField(null=True, max_length=255, blank=True, verbose_name='comments')),
            ],
            options={
                'permissions': (('admin_add_config', 'ADMIN: Can add config option'), ('admin_change_config', 'ADMIN: Can change config option'), ('admin_delete_config', 'ADMIN: Can delete config option'), ('admin_view_config', 'ADMIN: Can view config options')),
                'default_permissions': [],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('external_reference', models.CharField(max_length=40, verbose_name='external reference')),
                ('error_message', models.TextField(null=True, blank=True, verbose_name='error message')),
                ('attempts', models.IntegerField(default=1, verbose_name='attempts')),
            ],
            options={
                'permissions': (('admin_view_request', 'ADMIN: Can view logs'),),
                'default_permissions': [],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
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
