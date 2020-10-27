# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-23 15:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0116_auto_20170122_1418'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vlan',
            old_name='vid',
            new_name='vlan_id',
        ),
        migrations.RenameField(
            model_name='vlan',
            old_name='vname',
            new_name='vlan_name',
        ),
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together=set([('vlan_id', 'vlan_name', 'reseller')]),
        ),
    ]
