# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-05 08:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0088_auto_20161105_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vlan',
            name='reseller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dslam.Reseller'),
        ),
    ]
