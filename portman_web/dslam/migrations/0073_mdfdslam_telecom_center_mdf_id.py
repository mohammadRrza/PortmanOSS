# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 20:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0072_auto_20161004_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='mdfdslam',
            name='telecom_center_mdf_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
