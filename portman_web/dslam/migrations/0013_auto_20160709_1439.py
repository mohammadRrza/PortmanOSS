# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-09 14:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0012_auto_20160709_1137'),
    ]

    operations = [
        migrations.RenameField(
            model_name='command',
            old_name='name',
            new_name='text',
        ),
    ]
