from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import architect
from datetime import datetime


class RouterBrand(models.Model):
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class RouterType(models.Model):
    title = models.CharField(max_length=256)
    router_brand = models.ForeignKey(RouterBrand, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Router(models.Model):
    router_brand = models.ForeignKey(RouterBrand, on_delete=models.CASCADE)
    router_type = models.ForeignKey(RouterType, on_delete=models.CASCADE)
    device_interfaceid = models.IntegerField(null=True, blank=True, default=0)
    host_id = models.IntegerField(null=True, blank=True, default=0)
    device_name = models.CharField(max_length=256, null=True, blank=True)
    device_ip = models.CharField(max_length=256)
    device_fqdn = models.CharField(max_length=256)

    def __str__(self):
        return self.device_name

    def get_info(self):
        return dict(
            id=self.id, name=self.device_name, ip=self.device_ip, fqdn=self.device_fqdn
        )
