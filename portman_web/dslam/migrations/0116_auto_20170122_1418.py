# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-22 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0115_auto_20170122_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dslam',
            name='down_seconds',
            field=models.BigIntegerField(default=0),
        ),
    ]
