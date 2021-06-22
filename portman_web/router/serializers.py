from rest_framework import serializers
from khayyam import JalaliDatetime
from datetime import datetime
from router.models import Router, RouterCommand

class RouterSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        try:
            _request = kwargs.pop('request')
        except:
            _request = None
        super(RouterSerializer, self).__init__(*args, **kwargs)
        self.context['request'] = _request

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)
    class Meta:
        model = Router
        fields = ['id', 'device_name', 'device_ip', 'device_fqdn']


class RouterCommandSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        try:
            _request = kwargs.pop('request')
        except:
            _request = None
        super(RouterCommandSerializer, self).__init__(*args, **kwargs)
        self.context['request'] = _request

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = RouterCommand
        fields = ['id', 'router_command_description', 'router_command_text']