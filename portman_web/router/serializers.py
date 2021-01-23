from rest_framework import serializers
from khayyam import JalaliDatetime
from datetime import datetime
from router.models import Router

class RouterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Router
        fields = ['id', 'device_name', 'device_ip', 'device_fqdn']