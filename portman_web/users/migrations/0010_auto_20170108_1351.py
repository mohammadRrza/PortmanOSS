# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-08 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20161231_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='codename',
            field=models.CharField(max_length=256, verbose_name='code name'),
        ),
        migrations.AlterField(
            model_name='permission',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='permission',
            name='title',
            field=models.CharField(max_length=256),
        ),
    ]
