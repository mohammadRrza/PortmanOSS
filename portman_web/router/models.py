from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import architect
from datetime import datetime

class RouterType(models.Model):
    title = models.CharField(max_length=256)


class RouterBrand(models.Model):
    title = models.CharField(max_length=256)
    router_type = models.ForeignKey(RouterType, on_delete=models.CASCADE)


class Router(models.Model):
    router_type = models.ForeignKey(RouterType, on_delete=models.CASCADE)
    router_brand = models.ForeignKey(RouterBrand, on_delete=models.CASCADE)
    device_interfaceid = models.IntegerField(null=True, blank=True, default=0)
    host_id = models.IntegerField(null=True, blank=True, default=0)
    device_name = models.CharField(max_length=256, null=True, blank=True)
    device_ip = models.CharField(max_length=256)
    device_fqdn = models.CharField(max_length=256)
