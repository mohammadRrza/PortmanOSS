# Generated by Django 3.1.2 on 2020-12-07 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0181_auto_20201207_1213'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
            ],
        ),
    ]
