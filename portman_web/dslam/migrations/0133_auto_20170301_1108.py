# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-01 11:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0132_auto_20170227_1734'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerport',
            old_name='family',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='customerport',
            old_name='name',
            new_name='lastname',
        ),
    ]
