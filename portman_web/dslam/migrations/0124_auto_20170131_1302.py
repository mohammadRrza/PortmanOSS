# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-31 13:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0123_auto_20170128_1655'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together=set([('vlan_id',)]),
        ),
    ]
