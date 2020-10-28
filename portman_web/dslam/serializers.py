from rest_framework import serializers

from dslam.models import DSLAM, TelecomCenter, DSLAMPort, DSLAMStatusSnapshot, DSLAMICMPSnapshot, Vlan, DSLAMPortVlan,\
    DSLAMICMP, DSLAMPortSnapshot, Reseller, ResellerPort, CustomerPort, DSLAMEvent, DSLAMPortEvent, TelecomCenterLocation, DSLAMBulkCommandResult, \
    PortCommand, City, Command, DSLAMType, LineProfile, Terminal, TelecomCenterMDF, DSLAMCommand, DSLAMLocation, CityLocation,\
    MDFDSLAM, DSLAMBoard, DSLAMFaultyConfig, DSLAMPortFaulty, LineProfileExtraSettings, DSLAMCart

from khayyam import JalaliDatetime
from datetime import datetime


class TerminalSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name', read_only=True, required=False)

    class Meta:
        model = Terminal
        fields = ('id', 'name', 'text', 'port_count')


class DSLAMTypeSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name', read_only=True, required=False)

    class Meta:
        model = DSLAMType
        fields = ('id', 'name', 'text')


class CitySerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name', read_only=True, required=False)
    text = serializers.SerializerMethodField('get_cascade_city')

    def get_cascade_city(self, obj):
        cities = str(obj.name)
        while True:
            if obj.parent is None:
                break
            obj = City.objects.get(id=obj.parent.id)
            #cities =  unicode(obj.name + '-' + obj.english_name)+' / '+cities
            cities =  str(obj.name)+' / '+cities
        return cities

    class Meta:
        model = City
        fields = ('id', 'name', 'parent', 'text', 'english_name', 'abbr')


class CityLocationSerializer(serializers.ModelSerializer):
    city_info = CitySerializer(source='city', read_only=True, required=False)

    class Meta:
        model = CityLocation
        fields = ('id', 'city', 'city_info', 'city_lat', 'city_long')


class TelecomCenterSerializer(serializers.ModelSerializer):
    total_ports_count = serializers.IntegerField(
        source='get_total_ports_count', read_only=True, required=False)
    down_ports_count = serializers.IntegerField(
        source='get_down_ports_count', read_only=True, required=False)
    up_ports_count = serializers.IntegerField(
        source='get_up_ports_count', read_only=True, required=False)
    dslams_count = serializers.IntegerField(
        source='get_dslams_count', read_only=True, required=False)

    city_info = CitySerializer(source='city', read_only=True, required=False)
    text = serializers.SerializerMethodField('get_name_of_tc')

    def get_name_of_tc(self, obj):
        #if obj.english_name:
        #    return obj.name +' - '+ obj.english_name
        #else:
        return obj.name

    #text = serializers.CharField(source='name', read_only=True, required=False)
    #text = serializers.SerializerMethodField('get_cascade_city')

    def get_cascade_city(self, obj):
        city_info = CitySerializer(obj.city)
        return city_info.get_cascade_city(obj.city) + ' / ' + obj.name

    class Meta:
        model = TelecomCenter
        fields = ('id', 'name', 'english_name', 'city', 'city_info', 'text','prefix_bukht_name', 'mdf_row_orientation', 'total_ports_count', 'down_ports_count', 'up_ports_count', 'dslams_count')
        read_only_fields = ('id',)


class TelecomCenterLocationSerializer(serializers.ModelSerializer):
    telecom_center_info = TelecomCenterSerializer(source='telecom_center', read_only=True, required=False)

    class Meta:
        model = TelecomCenterLocation
        fields = ('id', 'telecom_center', 'telecom_center_info', 'telecom_lat', 'telecom_long', )



class TelecomCenterMDFSerializer(serializers.ModelSerializer):
    telecom_center_info = TelecomCenterSerializer(source='telecom_center', read_only=True, required=False)
    terminal_info = TerminalSerializer(source='terminal', read_only=True, required=False)
    reseller_detail = serializers.SerializerMethodField('get_reseller')
    def get_reseller(self, obj):
        if obj.reseller:
            return {'id': obj.reseller.id, 'name': obj.reseller.name}
        else:
            return None

    class Meta:
        model = TelecomCenterMDF
        fields = ('id', 'telecom_center', 'telecom_center_info', 'row_number', 'terminal', 'terminal_info', 'floor_start',
                  'floor_count', 'connection_count', 'floor_counting_status', 'connection_start', 'priority', 'status_of_port', 'connection_counting_status', 'reseller', 'reseller_detail')


class DSLAMSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        try:
            _request = kwargs.pop('request')
        except:
            _request = None
        super(DSLAMSerializer, self).__init__(*args, **kwargs)
        self.context['request'] = _request

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)

    dslam_type_info = DSLAMTypeSerializer(source="dslam_type" ,read_only=True, required=False)
    telecom_center_info = TelecomCenterSerializer(source="telecom_center" ,read_only=True, required=False)
    text = serializers.CharField(source='name', read_only=True, required=False)

    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', required=False, read_only=True)
    updated_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', required=False, read_only=True)
    last_sync = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', required=False, read_only=True)

    total_ports_count = serializers.IntegerField(
        source='get_ports_count', read_only=True, required=False)
    up_ports_count = serializers.IntegerField(
        source='get_up_ports_count', read_only=True, required=False)
    down_ports_count = serializers.IntegerField(
        source='get_down_ports_count', read_only=True, required=False)

    sync_ports_count = serializers.IntegerField(
        source='get_sync_ports_count', read_only=True, required=False)

    nosync_ports_count = serializers.IntegerField(
        source='get_nosync_ports_count', read_only=True, required=False)

    slots = serializers.JSONField(
        source='get_slots', read_only=True, required=False)

    ports = serializers.JSONField(
        source='get_ports', read_only=True, required=False)

    dslam_availability = serializers.IntegerField(
        source='get_dslam_availability', read_only=True, required=False)

    updated_at = serializers.SerializerMethodField('get_updated_persian_date')
    created_at = serializers.SerializerMethodField('get_created_persian_date')
    last_sync = serializers.SerializerMethodField('get_last_sync_persian_date')

    def get_updated_persian_date(self, obj):
        return JalaliDatetime(obj.updated_at).strftime("%Y-%m-%d %H:%M:%S")

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    def get_last_sync_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DSLAM
        fields = (
            'id', 'name', 'telecom_center', 'telecom_center_info', 'dslam_type', 'dslam_type_info', 'ip',
            'active', 'status', 'last_sync', 'conn_type', 'get_snmp_community', 'set_snmp_community', 'slot_count',
            'telnet_username', 'telnet_password', 'snmp_port', 'snmp_timeout', 'created_at', 'updated_at', 'port_count',
            'text', 'total_ports_count', 'up_ports_count', 'down_ports_count', 'last_sync_duration','uptime','version',
            'availability_start_time', 'down_seconds', 'dslam_availability', 'hostname','sync_ports_count', 'nosync_ports_count', 'fqdn', 'slots', 'ports',
        )
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'last_sync',
            'get_ports_count', 'get_up_ports_count', 'get_down_ports_count',
            'last_sync_duration','uptime', 'version',
        )



class DSLAMCartSerializer(serializers.ModelSerializer):
    dslam_info = DSLAMSerializer(source="dslam" ,read_only=True, required=False)
    telecom_center_info = DSLAMSerializer(source="teleccon_center" ,read_only=True, required=False)

    class Meta:
        model = DSLAMCart
        fields = ('id', 'dslam', 'dslam_info', 'priority', 'cart_count', 'cart_start', 'port_count', 'port_start', 'telecom_center', 'telecom_center_info')


class DSLAMLocationSerializer(serializers.ModelSerializer):
    dslam_info = DSLAMSerializer(source="dslam" ,read_only=True, required=False)

    class Meta:
        model = DSLAMLocation
        fields = ('id', 'dslam', 'dslam_info', 'dslam_lat', 'dslam_long')


class LineProfileSerializer(serializers.ModelSerializer):
    ports_count = serializers.IntegerField(
        source='get_ports_count', read_only=True, required=False)

    text = serializers.CharField(source='name', read_only=True, required=False)
    extra_settings_info = serializers.SerializerMethodField('get_extra_settings')

    def get_extra_settings(self, obj):
        line_profile_id = obj.id
        return LineProfileExtraSettings.objects.filter(line_profile__id=line_profile_id).\
                values('attr_name', 'attr_value')


    class Meta:
        model = LineProfile
        fields = ('id', 'name', 'text', 'template_type', 'channel_mode', 'max_ds_interleaved', 'max_us_interleaved', 'ds_snr_margin', 'us_snr_margin', 'min_ds_transmit_rate', 'max_ds_transmit_rate', 'min_us_transmit_rate', 'max_us_transmit_rate', 'extra_settings_info', 'dslam_type', 'ports_count')


class DSLAMEventSerializer(serializers.ModelSerializer):
    dslam_info = DSLAMSerializer(source="dslam" ,read_only=True, required=False)

    class Meta:
        model = DSLAMEvent
        fields = ('id', 'dslam', 'dslam_info', 'type', 'status', 'message', 'flag', 'created_at')


class DSLAMPortEventSerializer(serializers.ModelSerializer):
    dslam_info = DSLAMSerializer(source="dslam" ,read_only=True, required=False)

    class Meta:
        model = DSLAMPortEvent
        fields = ('id','dslam','dslam_info','slot_number','port_number','type', 'status', 'message', 'flag', 'created_at')
        read_only_fields = ('id','dslam','dslam_info','slot_number','port_number','type', 'message', 'flag', 'created_at')


class DSLAMStatusSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSLAMStatusSnapshot
        fields = ('id', 'dslam_id', 'line_card_temp', 'created_at', 'updated_at')


class CommandSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='text', read_only=True, required=False)
    class Meta:
        model = Command
        fields = ('id', 'text', 'type', 'description', 'name', 'show_command')



class DSLAMPortSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='port_name', read_only=True, required=False)
    dslam_info = DSLAMSerializer(source="dslam", read_only=True, required=False)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', required=False, read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', required=False, read_only=True)

    updated_at = serializers.SerializerMethodField('get_updated_persian_date')
    created_at = serializers.SerializerMethodField('get_created_persian_date')
    reseller = serializers.JSONField(
        source='get_reseller', read_only=True, required=False)
    subscriber = serializers.JSONField(
        source='get_subscriber', read_only=True, required=False)

    def get_updated_persian_date(self, obj):
        return JalaliDatetime(obj.updated_at).strftime("%Y-%m-%d %H:%M:%S")

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DSLAMPort
        fields = ('id', 'dslam', 'dslam_info', 'port_number', 'slot_number', 'created_at', 'updated_at', 'port_index',
                  'port_name', 'admin_status', 'oper_status', 'line_profile', 'upstream_snr',
                  'downstream_snr', 'upstream_attenuation', 'downstream_attenuation', 'upstream_attainable_rate',
                  'downstream_attainable_rate', 'upstream_tx_rate', 'downstream_tx_rate','text', 'selt_value', 'upstream_snr_flag',
                  'downstream_snr_flag', 'upstream_attenuation_flag', 'downstream_attenuation_flag', 'reseller', 'subscriber')



class ResellerSerializer(serializers.ModelSerializer):
    city_info = CitySerializer(source='city', read_only=True, required=False)
    text = serializers.CharField(source='name', read_only=True, required=False)

    class Meta:
        model = Reseller
        fields = ('id', 'name', 'tel', 'fax', 'address', 'city', 'city_info', 'text', 'vpi', 'vci')
        read_only_fields = ('id',)


class VlanSerializer(serializers.ModelSerializer):
    ports_count = serializers.IntegerField(
        source='get_port_count', read_only=True, required=False)
    dslam_count = serializers.IntegerField(
        source='get_dslam_count', read_only=True, required=False)

    reseller_info = ResellerSerializer(source='reseller', read_only=True, required=False)
    text = serializers.CharField(source='vlan_id', read_only=True, required=False)
    class Meta:
        model = Vlan
        fields = ('id', 'vlan_id', 'vlan_name', 'text','reseller', 'reseller_info', 'ports_count', 'dslam_count')
        read_only_fields = ('id', 'text', 'reseller_info', 'ports_count', 'dslam_count')


class ResellerPortSerializer(serializers.ModelSerializer):
    reseller_info = ResellerSerializer(source="reseller" ,read_only=True, required=False)

    class Meta:
        model = ResellerPort
        fields = ('id', 'reseller', 'reseller_info', 'identifier_key', 'telecom_center_id', 'dslam_id', 'dslam_fqdn', 'dslam_slot', 'dslam_port')


class CustomerPortSerializer(serializers.ModelSerializer):
    dslam_info = DSLAMSerializer(source='dslam', read_only=True, required=False)
    class Meta:
        model = CustomerPort
        fields = ('id', 'identifier_key', 'firstname', 'lastname', 'username', 'email', 'tel', 'mobile', 'national_code', 'dslam_info', 'telecom_center_id')
        read_only_fields = ('dslam_info', )


class PortCommandSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_persian_date')

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = PortCommand
        depth = 2
        fields = ('id', 'dslam', 'card_ports', 'command', 'value', 'created_at')


class DSLAMCommandSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_persian_date')

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DSLAMCommand
        depth = 2
        fields = ('id', 'dslam', 'command', 'value', 'created_at')


class DSLAMPortVlanSerializer(serializers.ModelSerializer):
    vlan_info = VlanSerializer(source='dslam', read_only=True, required=False)

    class Meta:
        model = DSLAMPortVlan
        fields = ('port', 'vlan', 'vlan_info', 'created_at')


class MDFDSLAMSerializer(serializers.ModelSerializer):
    dslam_name = serializers.SerializerMethodField('get_dslamname')
    port_detail = serializers.SerializerMethodField('get_port_id')
    reseller = serializers.JSONField(
        source='get_reseller', read_only=True, required=False)
    subscriber = serializers.JSONField(
        source='get_subscriber', read_only=True, required=False)


    def get_port_id(self, obj):
        try:
            port = DSLAMPort.objects.get(dslam__id=obj.dslam_id, slot_number=obj.slot_number, port_number=obj.port_number)
            return {'id': port.id, 'port_name': port.port_name}
        except Exception as ex:
            print(ex)
            return None

    def get_dslamname(self, obj):
        if not obj.dslam_id:
            return None
        try:
            return DSLAM.objects.get(id=obj.dslam_id).name
        except:
            return None


    class Meta:
        model = MDFDSLAM
        fields = ('id', 'row_number', 'floor_number', 'connection_number', 'dslam_id', 'slot_number', 'port_number', 'identifier_key', 'telecom_center_mdf_id', 'dslam_name', 'status', 'reseller', 'subscriber', 'port_detail', )
        read_only_fields = ('id', 'row_number', 'floor_number', 'connection_number', 'dslam_id', 'slot_number', 'port_number', 'identifier_key', 'telecom_center_mdf_id', 'dslam_name', 'reseller', 'subscriber')


class DSLAMBulkCommandResultSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_persian_date')

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DSLAMBulkCommandResult
        fields = ('id', 'title', 'error_file', 'success_file', 'result_file', 'created_at')

class DSLAMFaultyConfigSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_persian_date')
    updated_at = serializers.SerializerMethodField('get_created_persian_date')

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DSLAMFaultyConfig
        fields = ('id', 'slot_number_from', 'slot_number_to', 'port_number_from', 'port_number_to', 'created_at', 'updated_at', 'dslam_id')

class DSLAMPortFaultySerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField('get_created_persian_date')

    def get_created_persian_date(self, obj):
        return JalaliDatetime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DSLAMPortFaulty
        fields = ('id', 'slot_number', 'port_number', 'created_at', 'dslam_id')
