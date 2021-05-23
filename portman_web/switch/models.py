from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import architect
from datetime import datetime


class SwitchBrand(models.Model):
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class SwitchType(models.Model):
    title = models.CharField(max_length=256)
    Switch_brand = models.ForeignKey(SwitchBrand, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Switch(models.Model):
    Switch_brand = models.ForeignKey(SwitchBrand, on_delete=models.CASCADE)
    Switch_type = models.ForeignKey(SwitchType, on_delete=models.CASCADE)
    device_interfaceid = models.IntegerField(null=True, blank=True, default=0)
    host_id = models.IntegerField(null=True, blank=True, default=0)
    device_name = models.CharField(max_length=256, null=True, blank=True)
    device_ip = models.CharField(max_length=256)
    device_fqdn = models.CharField(max_length=256)

    def __str__(self):
        return self.device_name

    def get_info(self):
        return dict(
            id=self.host_id, name=self.device_name, ip=self.device_ip, fqdn=self.device_fqdn,
            switch_type=self.Switch_type
        )


class SwitchCommand(models.Model):
    switch_brand = models.ForeignKey(SwitchBrand, on_delete=models.CASCADE)
    switch_type = models.ForeignKey(SwitchType, on_delete=models.CASCADE)
    switch_command_description = models.CharField(max_length=256)
    switch_command_text = models.CharField(max_length=256, verbose_name='name', unique=True)
    show_command = models.BooleanField(default=False, verbose_name='Show command in Switch table')

    def __str__(self):
        return self.switch_type
