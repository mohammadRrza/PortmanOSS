# Generated by Django 3.2.8 on 2021-11-07 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0020_centertype_telecommunicationcenters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telecommunicationcenters',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
