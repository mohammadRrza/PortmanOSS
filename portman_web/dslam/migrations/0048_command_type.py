# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-27 04:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0047_dslamevent_dslamportevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='command',
            name='type',
            field=models.CharField(choices=[(b'dslam', b'dslam'), (b'dslamport', b'dslam port')], default=b'dslamport', max_length=100),
        ),
    ]
