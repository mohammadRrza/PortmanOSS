# Generated by Django 3.2.8 on 2021-11-06 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0015_auto_20211106_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortmapStates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contact.portmapstates'),
            preserve_default=False,
        ),
    ]
