# Generated by Django 3.2.8 on 2021-11-08 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0027_order_telecom'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='telecom',
        ),
    ]
