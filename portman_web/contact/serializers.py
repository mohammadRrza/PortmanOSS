from rest_framework import serializers
from khayyam import JalaliDatetime
from datetime import datetime
from contact.models import Order, PortmapState


class PortStatusSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='description', read_only=True, required=False)

    class Meta:
        model = PortmapState
        fields = ('id', 'description')


class OrderSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        try:
            _request = kwargs.pop('request')
        except:
            _request = None
        super(OrderSerializer, self).__init__(*args, **kwargs)
        self.context['request'] = _request

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)
    port_status_info = PortStatusSerializer(source="status", read_only=True, required=False)

    class Meta:
        model = Order
        fields = ['username', 'ranjePhoneNumber', 'slot_number', 'port_number',
                  'telco_row', 'telco_column', 'telco_connection', 'fqdn', 'port_status_info']
