# Generated by Django 3.1.2 on 2020-12-07 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dslam', '0188_auto_20201207_1353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activeequipmentcategory',
            name='equipment_category',
        ),
        migrations.DeleteModel(
            name='EquipmentCategory',
        ),
        migrations.RemoveField(
            model_name='equipmentlinksinfo',
            name='active_equipment_category',
        ),
        migrations.RemoveField(
            model_name='equipmentlinksinfo',
            name='city',
        ),
        migrations.RemoveField(
            model_name='equipmentlinksinfo',
            name='dslam_type',
        ),
        migrations.RemoveField(
            model_name='equipmentlinksinfo',
            name='passive_equipment_category',
        ),
        migrations.RemoveField(
            model_name='equipmentlinksinfo',
            name='telecom_center',
        ),
        migrations.RemoveField(
            model_name='equipmentlinksinfo',
            name='telecom_center_contract_type',
        ),
        migrations.RemoveField(
            model_name='passiveequipmentcategory',
            name='equipment_category',
        ),
        migrations.RemoveField(
            model_name='passiveequipmentcategory',
            name='terminal',
        ),
        migrations.DeleteModel(
            name='ActiveEquipmentCategory',
        ),
        migrations.DeleteModel(
            name='EquipmentCategoryType',
        ),
        migrations.DeleteModel(
            name='EquipmentlinksInfo',
        ),
        migrations.DeleteModel(
            name='PassiveEquipmentCategory',
        ),
        migrations.DeleteModel(
            name='TelecomContractType',
        ),
    ]
