from rest_framework import serializers
from khayyam import JalaliDatetime
from datetime import datetime
from contact.models import Order, PortmapState, Province, City, TelecommunicationCenters, FarzaneganTDLTE


class PortStatusSerializer(serializers.ModelSerializer):
    description = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = PortmapState
        fields = ('id', 'description')


class ProvinceSerializer(serializers.ModelSerializer):
    provinceName = serializers.CharField(source='provinceName', read_only=True, required=False)

    class Meta:
        model = Province
        fields = ('id', 'provinceName')


class CitySerializer(serializers.ModelSerializer):
    cityName = serializers.CharField(source='cityName', read_only=True, required=False)

    class Meta:
        model = City
        fields = ('id', 'cityName')


class TelecommunicationCentersSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = TelecommunicationCenters
        fields = ('id', 'name')


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
    telecomCenter_info = TelecommunicationCentersSerializer(source="telecom", read_only=True, required=False)

    class Meta:
        model = Order
        fields = ['username', 'ranjePhoneNumber', 'slot_number', 'port_number', 'telecomCenter_info',
                  'telco_row', 'telco_column', 'telco_connection', 'fqdn', 'port_status_info']


class DDRPageSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        try:
            _request = kwargs.pop('request')
        except:
            _request = None
        super(DDRPageSerializer, self).__init__(*args, **kwargs)
        self.context['request'] = _request

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

    class Meta:
        model = FarzaneganTDLTE
        fields = ['date_key', 'provider', 'customer_msisdn', 'total_data_volume_income']
