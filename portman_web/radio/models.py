from django.db import models


class RadioBrand(models.Model):
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class RadioType(models.Model):
    title = models.CharField(max_length=256)
    radio_brand = models.ForeignKey(RadioBrand, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Radio(models.Model):
    radio_brand = models.ForeignKey(RadioBrand, on_delete=models.CASCADE)
    radio_type = models.ForeignKey(RadioType, on_delete=models.CASCADE)
    device_interfaceid = models.IntegerField(null=True, blank=True, default=0)
    host_id = models.IntegerField(null=True, blank=True, default=0)
    device_name = models.CharField(max_length=256, null=True, blank=True)
    device_ip = models.CharField(max_length=256)
    device_fqdn = models.CharField(max_length=256)
    SSH_username = models.CharField(max_length=256)
    SSH_password = models.CharField(max_length=256)
    SSH_port = models.IntegerField(null=True, blank=True, default=0)
    SSH_timeout = models.IntegerField(null=True, blank=True, default=0)
    Latitude = models.FloatField(null=True, blank=True, default=0)
    Longitude = models.FloatField(null=True, blank=True, default=0)
    def __str__(self):
        return self.device_name

    def get_info(self):
        return dict(
            id=self.id, name=self.device_name, ip=self.device_ip, fqdn=self.device_fqdn,
            radio_type=self.radio_type.title, SSH_username=self.SSH_username, SSH_password=self.SSH_password,
            SSH_port=self.SSH_port, SSH_timeout=self.SSH_timeout, Latitude=self.Latitude, Longitude=self.Longitude
        )


class RadioGroup(models.Model):
    radio_brand = models.ForeignKey(RadioBrand, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class RadioCommand(models.Model):
    radio_brand = models.ForeignKey(RadioBrand, on_delete=models.CASCADE)
    radio_type = models.ForeignKey(RadioType, on_delete=models.CASCADE)
    radio_command_description = models.CharField(max_length=256)
    radio_command_text = models.CharField(max_length=256, verbose_name='name', unique=True)
    show_command = models.BooleanField(default=False, verbose_name='Show command in radio table')

    def __str__(self):
        return self.radio_type.title
