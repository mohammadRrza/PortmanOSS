# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-07 15:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0140_auto_20170307_1212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='command',
            name='command_template',
        ),
    ]
