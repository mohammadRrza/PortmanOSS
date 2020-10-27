# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-06 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0027_auto_20160802_2347'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dslam',
            old_name='snmp_community',
            new_name='get_snmp_community',
        ),
        migrations.AddField(
            model_name='dslam',
            name='set_snmp_community',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='dslam',
            name='telnet_password',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='dslam',
            name='telnet_username',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
