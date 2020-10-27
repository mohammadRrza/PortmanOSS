# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-10 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0013_auto_20160709_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='DSLAMType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=256, verbose_name=b'name')),
            ],
        ),
        migrations.RemoveField(
            model_name='dslam',
            name='dslam_type',
        ),
        migrations.AlterField(
            model_name='command',
            name='text',
            field=models.CharField(max_length=256, verbose_name=b'name'),
        ),
    ]
