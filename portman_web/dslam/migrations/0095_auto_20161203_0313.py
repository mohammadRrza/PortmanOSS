# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-03 03:13
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0094_auto_20161123_0551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dslambulkcommandresult',
            name='commands',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=200, null=True), size=None),
        ),
        migrations.AlterField(
            model_name='resellerport',
            name='identifier_key',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='resellerport',
            unique_together=set([]),
        ),
    ]
