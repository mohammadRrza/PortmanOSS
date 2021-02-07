from rest_framework import serializers
from khayyam import JalaliDatetime
from datetime import datetime
from contact.models import Order

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
    class Meta:
        model = Order
        fields = ['rastin_order_id', 'order_contact_id','username','ranjePhoneNumber', 'slot_number', 'port_number', 'telco_row', 'telco_column', 'telco_connection', 'fqdn']