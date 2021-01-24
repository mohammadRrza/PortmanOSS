from rest_framework import serializers
from khayyam import JalaliDatetime
from datetime import datetime
from switch.models import Switch

class SwitchSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        try:
            _request = kwargs.pop('request')
        except:
            _request = None
        super(SwitchSerializer, self).__init__(*args, **kwargs)
        self.context['request'] = _request

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)
    class Meta:
        model = Switch
        fields = ['id', 'device_name', 'device_ip', 'device_fqdn']