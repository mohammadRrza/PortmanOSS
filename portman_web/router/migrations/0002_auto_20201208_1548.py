# Generated by Django 3.1.2 on 2020-12-08 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('router', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='routerbrand',
            name='router_type',
        ),
        migrations.DeleteModel(
            name='Router',
        ),
        migrations.DeleteModel(
            name='RouterBrand',
        ),
        migrations.DeleteModel(
            name='RouterType',
        ),
    ]
