# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-15 12:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0153_auto_20170314_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='dslamport',
            name='vci',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dslamport',
            name='vpi',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
