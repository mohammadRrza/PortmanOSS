# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-05 01:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0002_dslamportsnapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='dslamportsnapshot',
            name='admin_status',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='dslamportsnapshot',
            name='line_profile',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='dslamportsnapshot',
            name='oper_status',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='dslamportsnapshot',
            name='port_index',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='dslamportsnapshot',
            name='port_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
