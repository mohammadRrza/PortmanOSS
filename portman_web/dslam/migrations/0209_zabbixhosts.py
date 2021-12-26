# Generated by Django 3.2.8 on 2021-12-26 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0208_merge_0201_auto_20210915_1225_0207_testmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZabbixHosts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_id', models.IntegerField()),
                ('device_group', models.CharField(max_length=255)),
                ('device_ip', models.CharField(max_length=255)),
                ('device_fqdn', models.CharField(max_length=255)),
                ('last_updated', models.DateField()),
                ('device_type', models.CharField(max_length=255)),
                ('device_brand', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'zabbix_hosts',
                'managed': False,
            },
        ),
    ]
