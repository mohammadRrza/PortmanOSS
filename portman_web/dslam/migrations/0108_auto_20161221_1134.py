# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-21 11:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0107_auto_20161214_1037'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portcommand',
            old_name='cart_ports',
            new_name='card_ports',
        ),
    ]
