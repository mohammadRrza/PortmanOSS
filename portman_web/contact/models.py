from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import architect
from datetime import datetime
from dslam.models import DSLAM


class ContactType(models.Model):
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class Contact(models.Model):
    # contact_dslam = models.ForeignKey(DSLAM,db_index=True, on_delete=models.CASCADE)
    contact_type = models.ForeignKey(ContactType, db_index=True, on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=256)
    phone = models.CharField(max_length=256)
    mobile_phone = models.CharField(max_length=256)
    contact_email = models.CharField(max_length=256)
    rastin_contact_id = models.CharField(max_length=256)

    def __str__(self):
        return self.contact_name


class PortmapState(models.Model):
    description = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.description


class Province(models.Model):
    provinceId = models.IntegerField(db_index=True, blank=True, null=True)
    provinceName = models.CharField(max_length=256, blank=True, null=True)
    externalId = models.IntegerField(db_index=True, blank=True, null=True)
    shaskam_Url = models.CharField(max_length=256, blank=True, null=True)
    shaskam_Username = models.CharField(max_length=256, blank=True, null=True)
    Shaskam_Password = models.CharField(max_length=256, blank=True, null=True)
    Shaskam_CompanyId = models.IntegerField(db_index=True, blank=True, null=True)
    TCIId = models.IntegerField(db_index=True, blank=True, null=True)

    def __str__(self):
        return self.provinceName


class City(models.Model):
    cityId = models.IntegerField(db_index=True, blank=True, null=True)
    cityName = models.CharField(max_length=256, blank=True, null=True)
    provinceId = models.IntegerField(db_index=True, blank=True, null=True)
    externalId = models.CharField(max_length=256, blank=True, null=True)
    areaCode = models.CharField(max_length=256, blank=True, null=True)
    shaskam_CityId = models.CharField(max_length=256, blank=True, null=True)
    TCIId = models.IntegerField(db_index=True, blank=True, null=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.cityName


class CenterType(models.Model):
    description = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.description


class TelecommunicationCenters(models.Model):
    telecomCenterId = models.IntegerField(max_length=1, blank=True, null=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    active = models.IntegerField(db_index=True, blank=True, null=True)
    areaId = models.IntegerField(db_index=True, blank=True, null=True)
    externalId = models.IntegerField(db_index=True, blank=True, null=True)
    externalTelcoName = models.CharField(max_length=256, blank=True, null=True)
    activeInBitStream = models.BooleanField()
    CRAId = models.IntegerField(max_length=1, blank=True, null=True)
    TCIId = models.IntegerField(db_index=True, blank=True, null=True)
    centerTypeId = models.ForeignKey(CenterType, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Order(models.Model):
    rastin_order_id = models.IntegerField(db_index=True, blank=True, null=True)
    order_contact_id = models.IntegerField(db_index=True, blank=True, null=True)
    ranjePhoneNumber = models.CharField(max_length=256, blank=True, null=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    user_id = models.IntegerField(db_index=True, blank=True, null=True)
    slot_number = models.IntegerField(db_index=True, blank=True, null=True)
    port_number = models.IntegerField(db_index=True, blank=True, null=True)
    telco_row = models.IntegerField(db_index=True, blank=True, null=True)
    telco_column = models.IntegerField(db_index=True, blank=True, null=True)
    telco_connection = models.IntegerField(db_index=True, blank=True, null=True)
    fqdn = models.CharField(max_length=256, blank=True, null=True)
    status = models.ForeignKey(PortmapState, on_delete=models.CASCADE)
    telecom = models.ForeignKey(TelecommunicationCenters, on_delete=models.CASCADE)
    dslam = models.ForeignKey(DSLAM, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.rastin_order_id


class FarzaneganProvider(models.Model):
    provider_name = models.CharField(max_length=250)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)

    def __str__(self):
        return self.provider_name


class FarzaneganProviderData(models.Model):
    provider = models.ForeignKey(FarzaneganProvider, on_delete=models.CASCADE, related_name='provider_total_data')
    created = models.DateTimeField(auto_now_add=True)
    total_traffic = models.IntegerField()
    used_traffic = models.IntegerField()
    remain_traffic = models.IntegerField()
    total_numbers = models.IntegerField()
    used_numbers = models.IntegerField()
    remain_numbers = models.IntegerField()
    total_data_volume = models.FloatField()


class FarzaneganTDLTE(models.Model):
    provider = models.ForeignKey(FarzaneganProvider, on_delete=models.CASCADE, related_name='provider_data')
    date_key = models.DateField()
    provider_number = models.CharField(max_length=32)
    customer_msisdn = models.CharField(max_length=32)
    total_data_volume_income = models.CharField(max_length=32)
    owner_username = models.CharField(max_length=64)


class PishgamanNote(models.Model):
    province = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    telecom_center = models.CharField(max_length=250)
    problem_desc = models.TextField()
    register_time = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=120)
