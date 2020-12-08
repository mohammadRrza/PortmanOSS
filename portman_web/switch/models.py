from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import architect
from datetime import datetime


class SwitchBrand(models.Model):
    title = models.CharField(max_length=256)


class SwitchType(models.Model):
    title = models.CharField(max_length=256)
    Switch_brand = models.ForeignKey(SwitchBrand, on_delete=models.CASCADE)


class Switch(models.Model):
    Switch_brand = models.ForeignKey(SwitchBrand, on_delete=models.CASCADE)
    Switch_type = models.ForeignKey(SwitchType, on_delete=models.CASCADE)
    device_interfaceid = models.IntegerField(null=True, blank=True, default=0)
    host_id = models.IntegerField(null=True, blank=True, default=0)
    device_name = models.CharField(max_length=256, null=True, blank=True)
    device_ip = models.CharField(max_length=256)
    device_fqdn = models.CharField(max_length=256)
