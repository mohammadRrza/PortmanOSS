# Generated by Django 3.2.8 on 2021-11-07 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0023_telecommunicationcenters_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telecommunicationcenters',
            name='activeInBitStream',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
