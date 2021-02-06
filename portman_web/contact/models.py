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
    #contact_dslam = models.ForeignKey(DSLAM,db_index=True, on_delete=models.CASCADE)
    contact_type = models.ForeignKey(ContactType,db_index=True, on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=256)
    phone= models.CharField(max_length=256)
    mobile_phone = models.CharField(max_length=256)
    contact_email = models.CharField(max_length=256)
    rastin_contact_id= models.CharField(max_length=256)

    def __str__(self):
        return self.contact_name


class Order(models.Model):
    rastin_order_id = models.IntegerField(db_index=True, blank=True, null=True)
    order_contact_id = models.IntegerField(db_index=True, blank=True, null=True)
    ranjePhoneNumber = models.CharField(max_length=256)
    username = models.CharField(max_length=256)
    slot_number = models.IntegerField(db_index=True, blank=True, null=True)
    port_number = models.IntegerField(db_index=True, blank=True, null=True)
    telco_row = models.IntegerField(db_index=True, blank=True, null=True)
    port_Column = models.IntegerField(db_index=True, blank=True, null=True)
    telco_connection = models.IntegerField(db_index=True, blank=True, null=True)
    fqdn = models.CharField(max_length=256)
    def __str__(self):
        return self.rastin_order_id
