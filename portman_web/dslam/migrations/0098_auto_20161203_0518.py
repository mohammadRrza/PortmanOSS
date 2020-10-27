# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-03 05:18
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0097_auto_20161203_0332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portcommand',
            name='port_name',
        ),
        migrations.AddField(
            model_name='portcommand',
            name='cart_ports',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True), default=[], size=None),
            preserve_default=False,
        ),
    ]
