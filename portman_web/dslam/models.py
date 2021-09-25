from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import architect
from datetime import datetime


class City(models.Model):
    name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=200)
    abbr = models.CharField(max_length=4, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class CityLocation(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE)
    city_lat = models.CharField(max_length=256)
    city_long = models.CharField(max_length=256)

    def __str__(self):
        return 'city :{0} - lat: {1}, long {2}'.format(self.city.name, self.city_lat, self.city_long)


class Terminal(models.Model):
    name = models.CharField(max_length=256)
    port_count = models.IntegerField()

    def __str__(self):
        return self.name


class TelecomCenter(models.Model):
    mdf_row_orientation_key = (
        ('HORIZONTAL', 'Horizontal'),
        ('VERTICAL', 'Vertical'),
    )
    code = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    english_name = models.CharField(max_length=256, blank=True, null=True)
    prefix_bukht_name = models.CharField(max_length=4)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    mdf_row_orientation = models.CharField(choices=mdf_row_orientation_key, default='Vertical', max_length=10)

    @property
    def get_dslams_count(self):
        return self.dslam_set.count()

    @property
    def get_up_ports_count(self):
        dslams = self.dslam_set.all()
        return DSLAMPort.objects.filter(dslam__in=dslams, admin_status='LOCK').count()

    @property
    def get_down_ports_count(self):
        dslams = self.dslam_set.all()
        return DSLAMPort.objects.filter(dslam__in=dslams, admin_status='LOCK').count()

    @property
    def get_total_ports_count(self):
        dslams = self.dslam_set.all()
        return DSLAMPort.objects.filter(dslam__in=dslams).count()

    def as_json(self):
        return {
            'id': self.id,
            # 'text': self.name+'/'+self.get_cascade_city(self.city),
            # 'text': self.name +' - '+ self.english_name,
            'text': self.name,
            'prefix_bukht_name': self.prefix_bukht_name
        }

    def get_cascade_city(self, obj):
        cities = str(obj.name)
        while True:
            if obj.parent is None:
                break
            obj = City.objects.get(id=obj.parent.id)
            cities = str(obj.name + '-' + obj.english_name) + ' / ' + cities
        return cities

    def __str__(self):
        return self.name


class TelecomCenterLocation(models.Model):
    telecom_center = models.ForeignKey(TelecomCenter, on_delete=models.CASCADE)
    telecom_lat = models.CharField(max_length=256)
    telecom_long = models.CharField(max_length=256)

    def __str__(self):
        return 'telecom :{0} - lat: {1}, long {2}'.format(self.telecom_center.name, self.telecom_lat, self.telecom_long)


class DSLAMType(models.Model):
    name = models.CharField(max_length=256, verbose_name='name')

    def __str__(self):
        return self.name


class DSLAM(models.Model):
    telecom_center = models.ForeignKey(TelecomCenter, verbose_name='Telecom Center', db_index=True,
                                       on_delete=models.CASCADE)
    name = models.CharField(max_length=256, unique=True, db_index=True)
    dslam_number = models.IntegerField(null=True, blank=True, default=0)
    dslam_type = models.ForeignKey(DSLAMType, on_delete=models.CASCADE)
    ip = models.CharField(max_length=15, unique=True)
    version = models.CharField(max_length=256, null=True, blank=True, )
    active = models.BooleanField(default=True)
    status = models.CharField(max_length=256, null=True, blank=True, default='new')
    access_name = models.CharField(max_length=256, null=True, blank=True, default='new',
                                   verbose_name='Access Name (vendor: FiberHome)')
    last_sync = models.DateTimeField(null=True, blank=True)
    last_sync_duration = models.IntegerField(null=True, blank=True)
    uptime = models.CharField(max_length=256, blank=True, null=True)
    hostname = models.CharField(max_length=256, blank=True, null=True)
    conn_type = models.CharField(max_length=32)
    get_snmp_community = models.CharField(max_length=64, null=True, blank=True)
    set_snmp_community = models.CharField(max_length=64, null=True, blank=True)
    snmp_port = models.IntegerField(null=True, blank=True)
    snmp_timeout = models.IntegerField(null=True, blank=True, default=3)
    telnet_username = models.CharField(max_length=64, null=True, blank=True)
    telnet_password = models.CharField(max_length=64, null=True, blank=True)
    slot_count = models.IntegerField(null=True, blank=True, default=17)
    port_count = models.IntegerField(null=True, blank=True, default=72)
    availability_start_time = models.DateTimeField(auto_now_add=True)
    down_seconds = models.BigIntegerField(default=0)
    fqdn = models.CharField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    @property
    def get_ports_count(self):
        return self.dslamport_set.count()

    @property
    def get_slots(self):
        return self.dslamport_set.values_list('slot_number', flat=True).order_by('slot_number').distinct()

    @property
    def get_ports(self):
        return self.dslamport_set.values('port_number', 'slot_number').order_by('slot_number', 'port_number')

    @property
    def get_dslam_availability(self):
        now = datetime.now()
        total = (now - self.availability_start_time).total_seconds() / 1200
        return 100 - (((self.down_seconds / 1200) / total) * 100)

    @property
    def get_up_ports_count(self):
        return self.dslamport_set.filter(admin_status='UNLOCK').count()

    @property
    def get_down_ports_count(self):
        return self.dslamport_set.filter(admin_status='LOCK').count()

    @property
    def get_sync_ports_count(self):
        return self.dslamport_set.filter(oper_status='SYNC').count()

    @property
    def get_nosync_ports_count(self):
        return self.dslamport_set.filter(oper_status='NO-SYNC').count()

    def __unicode__(self):
        return self.name

    def get_info(self):
        return dict(
            id=self.id, name=self.name, ip=self.ip, active=self.active,
            status=self.status, last_sync=self.last_sync, conn_type=self.conn_type,
            get_snmp_community=self.get_snmp_community, set_snmp_community=self.set_snmp_community,
            snmp_port=self.snmp_port,
            telnet_username=str(self.telnet_username), telnet_password=str(self.telnet_password),
            slot_count=self.slot_count,
            port_count=self.port_count, snmp_timeout=self.snmp_timeout, dslam_type=self.dslam_type.name,
            access_name=self.access_name,
            last_sync_duration=self.last_sync_duration, created_at=self.created_at, updated_at=self.updated_at,
            dslam_availability=self.get_dslam_availability,
            hostname=self.hostname, fqdn=self.fqdn, uptime=self.uptime,
        )

    def get_port_index_map(self):
        port_index_map = []
        ports_queryset = DSLAMPort.objects.filter(dslam=self).order_by('updated_at')

        for port_obj in ports_queryset:
            port_index_map.append((port_obj.slot_number, port_obj.port_number, port_obj.port_index, port_obj.port_name))

        return port_index_map


class DSLAMBoard(models.Model):
    dslam = models.ForeignKey(DSLAM, db_index=True, on_delete=models.CASCADE)
    card_number = models.IntegerField()
    status = models.CharField(max_length=64, blank=True, null=True)
    card_type = models.CharField(max_length=64, blank=True, null=True)
    uptime = models.CharField(max_length=64, blank=True, null=True)
    fw_version = models.CharField(max_length=64, blank=True, null=True)
    hw_version = models.CharField(max_length=64, blank=True, null=True)
    serial_number = models.CharField(max_length=64, blank=True, null=True)
    temperature = JSONField(blank=True, null=True)
    mac_address = models.CharField(max_length=20, blank=True, null=True)
    inband_mac_address = models.CharField(max_length=20, blank=True, null=True)
    outband_mac_address = models.CharField(max_length=20, blank=True, null=True)

    @property
    def get_up_ports_count(self):
        return self.dslam.dslamport_set.filter(admin_status='UNLOCK', slot_number=self.card_number).count()

    @property
    def get_down_ports_count(self):
        return self.dslam.dslamport_set.filter(admin_status='LOCK', slot_number=self.card_number).count()

    @property
    def get_total_ports_count(self):
        return self.dslam.dslamport_set.filter(slot_number=self.card_number).count()

    def as_json(self):
        return {
            'id': self.id,
            'card_number': self.card_number,
            'card_status': self.status,
            'card_type': self.card_type,
            'uptime': self.uptime,
            'fw_version': self.fw_version,
            'hw_version': self.hw_version,
            'serial_number': self.serial_number,
            'mac_address': self.mac_address,
            'temperature': self.temperature,
            'inband_mac_address': self.inband_mac_address,
            'outband_mac_address': self.outband_mac_address,
            'up_ports_count': self.get_up_ports_count,
            'down_ports_count': self.get_down_ports_count,
            'total_ports_count': self.get_total_ports_count
        }

    class Meta:
        ordering = ('card_number',)


class DSLAMCart(models.Model):
    telecom_center = models.ForeignKey(TelecomCenter, on_delete=models.CASCADE)
    dslam = models.ForeignKey(DSLAM, on_delete=models.CASCADE)
    priority = models.IntegerField()
    cart_count = models.IntegerField()
    cart_start = models.IntegerField()
    port_count = models.IntegerField()
    port_start = models.IntegerField()


class MDFDSLAM(models.Model):
    status_keys = (
        ('FREE', 'Free'),
        ('BUSY', 'Busy'),
        ('DISABLE', 'Disable'),
        ('VPN', 'VPN'),
        ('FAULTY', 'Faulty'),
        ('RESELLER', 'Reseller'),
    )
    telecom_center_id = models.IntegerField()
    telecom_center_mdf_id = models.IntegerField()
    row_number = models.IntegerField()
    floor_number = models.IntegerField()
    connection_number = models.IntegerField()
    dslam_id = models.IntegerField(db_index=True, blank=True, null=True)
    slot_number = models.IntegerField(db_index=True, blank=True, null=True)
    port_number = models.IntegerField(db_index=True, blank=True, null=True)
    identifier_key = models.CharField(max_length=16, blank=True, null=True)
    status = models.CharField(max_length=50, choices=status_keys, default="FREE")

    @property
    def get_port_count(self):
        return self.dslamportvlan_set.filter(vlan=self).count()

    @property
    def get_reseller(self):
        try:
            reseller = ResellerPort.objects.get(identifier_key=self.identifier_key).reseller
            return {'id': reseller.id, 'name': reseller.name}
        except Exception as ex:
            return None

    @property
    def get_subscriber(self):
        try:
            customer = CustomerPort.objects.get(identifier_key=self.identifier_key)
            return {'id': customer.id, 'username': customer.username}
        except Exception as ex:
            return None

    def __str__(self):
        return '{0}:{1}:{2}:{3}'.format(self.telecom_center_id, self.dslam_id, self.slot_number, self.port_number)


class DSLAMFaultyConfig(models.Model):
    dslam_id = models.IntegerField()
    slot_number_from = models.IntegerField()
    slot_number_to = models.IntegerField()
    port_number_from = models.IntegerField()
    port_number_to = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0}: {1} - {2} :: {3} - {4}'.format(self.dslam_id, self.slot_number_from, self.port_number_from,
                                                    self.slot_number_to, self.port_number_to)


class DSLAMPortFaulty(models.Model):
    dslam_faulty_config = models.ForeignKey(DSLAMFaultyConfig, on_delete=models.CASCADE)
    dslam_id = models.IntegerField()
    port_number = models.IntegerField()
    slot_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0}: {1} - {2}'.format(self.dslam_id, self.slot_number, self.port_number)

    class Meta:
        unique_together = ('dslam_id', 'port_number', 'slot_number',)


class DSLAMLocation(models.Model):
    dslam = models.ForeignKey(DSLAM, db_index=True, on_delete=models.CASCADE)
    dslam_lat = models.CharField(max_length=256, blank=True, null=True)
    dslam_long = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return 'DSLAM: {0} -> lat: {1}, long: {2}'.format(self.dslam.name, self.dslam_lat, self.dslam_long)


class DSLAMStatus(models.Model):
    dslam = models.ForeignKey(DSLAM, db_index=True, on_delete=models.CASCADE)
    line_card_temp = JSONField(max_length=2048, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DSLAMStatusSnapshot(models.Model):
    dslam_id = models.IntegerField(null=True, blank=True, db_index=True)
    line_card_temp = JSONField(max_length=2048, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DSLAMICMP(models.Model):
    dslam = models.ForeignKey(DSLAM, db_index=True, on_delete=models.CASCADE)
    avgping = models.CharField(max_length=10, blank=True, null=True)
    jitter = models.CharField(max_length=10, blank=True, null=True)
    maxping = models.CharField(max_length=10, blank=True, null=True)
    minping = models.CharField(max_length=10, blank=True, null=True)
    packet_loss = models.CharField(max_length=10, blank=True, null=True)
    received = models.PositiveIntegerField(blank=True, null=True)
    sent = models.PositiveIntegerField(blank=True, null=True)
    trace_route = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DSLAMICMPSnapshot(models.Model):
    dslam_id = models.IntegerField(null=True, blank=True, db_index=True)
    avgping = models.CharField(max_length=10, blank=True, null=True)
    jitter = models.CharField(max_length=10, blank=True, null=True)
    maxping = models.CharField(max_length=10, blank=True, null=True)
    minping = models.CharField(max_length=10, blank=True, null=True)
    packet_loss = models.CharField(max_length=10, blank=True, null=True)
    received = models.PositiveIntegerField(blank=True, null=True)
    sent = models.PositiveIntegerField(blank=True, null=True)
    trace_route = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DSLAMEvent(models.Model):
    type_keys = (
        ('dslam_connection_error', 'DSLAM Connection Error'),
        ('get_dslam_sysUpTime_error', 'Get DSLAM Uptime Error'),
        ('get_dslam_temperature_error', 'Get DSLAM Temperature Error'),
        ('dslam_ping_error', 'DSLAM Ping Error'),
        ('dslam_trace_route_error', 'DSLAM Trace Route Error'),
    )

    status_keys = (
        ('read', 'Read'),
        ('unread', 'UnRead'),
        ('resolve', 'Resolve'),
    )

    flag_keys = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error')
    )

    dslam = models.ForeignKey(DSLAM, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, choices=type_keys, default='dslam_connection_error')
    flag = models.CharField(max_length=100, choices=flag_keys, default='error')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=status_keys, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)


class LineProfile(models.Model):
    name = models.CharField(max_length=256, unique=True)
    dslam_type = models.CharField(max_length=256)
    template_type = models.CharField(max_length=256, blank=True, null=True)
    channel_mode = models.CharField(max_length=256, blank=True, null=True)
    max_ds_interleaved = models.CharField(max_length=256, blank=True, null=True)
    max_us_interleaved = models.CharField(max_length=256, blank=True, null=True)
    ds_snr_margin = models.CharField(max_length=256, blank=True, null=True)
    us_snr_margin = models.CharField(max_length=256, blank=True, null=True)
    min_ds_transmit_rate = models.CharField(max_length=256, blank=True, null=True)
    max_ds_transmit_rate = models.CharField(max_length=256, blank=True, null=True)
    min_us_transmit_rate = models.CharField(max_length=256, blank=True, null=True)
    max_us_transmit_rate = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def get_ports_count(self):
        return DSLAMPort.objects.filter(line_profile=self.name).count()


class LineProfileExtraSettings(models.Model):
    line_profile = models.ForeignKey(LineProfile, db_index=True, on_delete=models.CASCADE)
    attr_name = models.CharField(max_length=256)
    attr_value = models.CharField(max_length=256)


class DSLAMPort(models.Model):
    attenuation_flag_keys = (
        ('outstanding', 'Outstanding'),
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('bad', 'Bad')
    )

    snr_flag_keys = (
        ('outstanding', 'Outstanding'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'fair'),
        ('bad', 'Bad')
    )

    dslam = models.ForeignKey(DSLAM, db_index=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slot_number = models.PositiveSmallIntegerField(blank=True, null=True)
    port_number = models.PositiveIntegerField(blank=True, null=True)
    port_index = models.CharField(max_length=256, db_index=True, blank=True, null=True)
    port_name = models.CharField(max_length=256, db_index=True, blank=True, null=True)
    admin_status = models.CharField(max_length=64, blank=True, null=True)
    oper_status = models.CharField(max_length=64, blank=True, null=True)
    line_profile = models.CharField(max_length=120, blank=True, null=True)
    selt_value = models.CharField(max_length=64, blank=True, null=True)
    uptime = models.CharField(max_length=256, blank=True, null=True)

    upstream_snr = models.FloatField(blank=True, null=True)  # ATU-C SNR
    downstream_snr = models.FloatField(blank=True, null=True)  # ATU-R SNR

    upstream_attenuation = models.FloatField(blank=True, null=True)  # ATU-C Atn
    downstream_attenuation = models.FloatField(blank=True, null=True)  # ATU-R Atn

    upstream_attainable_rate = models.FloatField(blank=True, null=True)  # ATU-C Attain Rate
    downstream_attainable_rate = models.FloatField(blank=True, null=True)  # ATU-R Attain Rate

    upstream_tx_rate = models.FloatField(blank=True, null=True)  # ATU-C Actu tx rate
    downstream_tx_rate = models.FloatField(blank=True, null=True)  # ATU-R Actu tx rate

    upstream_snr_flag = models.CharField(max_length=100, choices=snr_flag_keys, blank=True, null=True)
    downstream_snr_flag = models.CharField(max_length=100, choices=snr_flag_keys, blank=True, null=True)

    upstream_attenuation_flag = models.CharField(max_length=100, choices=attenuation_flag_keys, blank=True, null=True)
    downstream_attenuation_flag = models.CharField(max_length=100, choices=attenuation_flag_keys, blank=True, null=True)

    vpi = models.IntegerField(blank=True, null=True)
    vci = models.IntegerField(blank=True, null=True)

    # upstream_cur_status = models.CharField(max_length=128, blank=True, null=True)
    # downstream_cur_status = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.dslam.name, self.port_name)

    @property
    def dslam_name(self):
        return self.dslam.name

    @property
    def get_reseller(self):
        try:
            reseller = ResellerPort.objects.get(dslam_id=self.dslam__id, port_number=self.port_number,
                                                slot_number=self.slot_number).reseller
            return {'id': reseller.id, 'name': reseller.name}
        except Exception as ex:
            print(ex)
            return None

    @property
    def get_subscriber(self):
        try:
            customer = CustomerPort.objects.get(dslam_id=self.dslam__id, port_number=self.port_number,
                                                slot_number=self.slot_number)
            return {'id': customer.id, 'username': customer.username}
        except Exception as ex:
            print(ex)
            return None


# @architect.install('partition', type='range', subtype='integer', constraint='1000000', column='id')
class DSLAMPortSnapshot(models.Model):
    attenuation_flag_keys = (
        ('outstanding', 'Outstanding'),
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('bad', 'Bad')
    )
    snr_flag_keys = (
        ('outstanding', 'Outstanding'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'fair'),
        ('bad', 'Bad')
    )
    dslam_id = models.IntegerField(null=True, blank=True, db_index=True)
    slot_number = models.PositiveSmallIntegerField(blank=True, null=True)
    port_number = models.PositiveIntegerField(blank=True, null=True)

    snp_date = models.DateTimeField(auto_now_add=True, db_index=True)

    port_index = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    port_name = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    admin_status = models.CharField(max_length=64, blank=True, null=True)
    oper_status = models.CharField(max_length=64, blank=True, null=True)
    uptime = models.CharField(max_length=256, db_index=True, blank=True, null=True)
    line_profile = models.CharField(max_length=256, blank=True, null=True)
    vlan = models.CharField(max_length=256, blank=True, null=True)

    upstream_snr = models.FloatField(blank=True, null=True)  # ATU-C SNR
    downstream_snr = models.FloatField(blank=True, null=True)  # ATU-R SNR
    upstream_attenuation = models.FloatField(blank=True, null=True)  # ATU-C Atn
    downstream_attenuation = models.FloatField(blank=True, null=True)  # ATU-R Atn
    upstream_attainable_rate = models.FloatField(blank=True, null=True)  # ATU-C Attain Rate
    downstream_attainable_rate = models.FloatField(blank=True, null=True)  # ATU-R Attain Rate
    upstream_tx_rate = models.FloatField(blank=True, null=True)  # ATU-C Actu tx rate
    downstream_tx_rate = models.FloatField(blank=True, null=True)  # ATU-R Actu tx rate
    upstream_snr_flag = models.CharField(max_length=100, choices=snr_flag_keys, default='good', null=True, blank=True)
    downstream_snr_flag = models.CharField(max_length=100, choices=snr_flag_keys, default='good', null=True, blank=True)
    upstream_attenuation_flag = models.CharField(max_length=100, choices=attenuation_flag_keys, default='good',
                                                 null=True, blank=True)
    downstream_attenuation_flag = models.CharField(max_length=100, choices=attenuation_flag_keys, default='good',
                                                   null=True, blank=True)


class DSLAMPortMac(models.Model):
    port = models.ForeignKey(DSLAMPort, db_index=True, on_delete=models.CASCADE)
    mac_address = models.CharField(max_length=20)


class DSLAMPortEvent(models.Model):
    type_keys = (
        ('no_such_object', 'No Such Object'),
    )

    status_keys = (
        ('read', 'Read'),
        ('unread', 'UnRead'),
        ('resolve', 'Resolve'),
    )

    flag_keys = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error')
    )
    dslam = models.ForeignKey(DSLAM, on_delete=models.CASCADE)
    slot_number = models.PositiveSmallIntegerField()
    port_number = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=100, choices=type_keys, default='no_such_object')
    flag = models.CharField(max_length=100, choices=flag_keys, default='error')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=status_keys, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)


class Reseller(models.Model):
    name = models.CharField(max_length=256)
    tel = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=1000, blank=True, null=True)
    vpi = models.IntegerField(null=True)
    vci = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class TelecomCenterMDF(models.Model):
    counting_status_flag = (
        ('ODD', 'odd'),
        ('EVEN', 'even'),
        ('STANDARD', 'standard')
    )

    status_keys = (
        ('FREE', 'Free'),
        ('BUSY', 'Busy'),
        ('DISABLE', 'Disable'),
        ('VPN', 'VPN'),
        ('FAULTY', 'Faulty'),
        ('RESELLER', 'Reseller'),
    )

    telecom_center = models.ForeignKey(TelecomCenter, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)
    row_number = models.IntegerField()
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)

    floor_start = models.IntegerField()
    floor_count = models.IntegerField()
    floor_counting_status = models.CharField(max_length=8, choices=counting_status_flag, default='STANDARD')

    connection_count = models.IntegerField()
    connection_start = models.IntegerField(default=1)
    connection_counting_status = models.CharField(choices=counting_status_flag, default='STANDARD', max_length=8)
    status_of_port = models.CharField(choices=status_keys, default='FREE', max_length=8)
    reseller = models.ForeignKey(Reseller, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)


class ResellerPort(models.Model):
    KEYS = (
        ('DISABLE', 'Disable'),
        ('ENABLE', 'Enable'),
    )
    reseller = models.ForeignKey(Reseller, db_index=True, on_delete=models.CASCADE)
    telecom_center_id = models.IntegerField(db_index=True)
    identifier_key = models.CharField(max_length=16, unique=True)
    status = models.CharField(max_length=100, choices=KEYS, default='ENABLE')
    dslam_id = models.IntegerField(null=True)
    dslam_fqdn = models.CharField(max_length=1024, null=True, blank=True)
    dslam_slot = models.IntegerField(null=True)
    dslam_port = models.IntegerField(null=True)

    def __str__(self):
        return '{0}: {1}'.format(self.reseller.name, self.identifier_key)


class Vlan(models.Model):
    vlan_id = models.CharField(max_length=256)
    vlan_name = models.CharField(max_length=256)
    reseller = models.ForeignKey(Reseller, blank=True, null=True, on_delete=models.CASCADE)

    @property
    def get_port_count(self):
        return self.dslamportvlan_set.filter(vlan=self).count()

    @property
    def get_dslam_count(self):
        return self.dslamportvlan_set.filter(vlan=self) \
            .values_list('port__dslam_id', flat=True) \
            .order_by('port__dslam_id').distinct().count()

    class Meta:
        unique_together = ('vlan_id', 'vlan_name')

    def __str__(self):
        return "{0}-{1}".format(self.vlan_id, self.vlan_name)


class DSLAMPortVlan(models.Model):
    port = models.ForeignKey(DSLAMPort, db_index=True, on_delete=models.CASCADE)
    vlan = models.ForeignKey(Vlan, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('port', 'vlan',)


class CustomerPort(models.Model):
    telecom_center_id = models.IntegerField(db_index=True)
    identifier_key = models.CharField(max_length=16, unique=True)
    lastname = models.CharField(max_length=256, db_index=True, blank=True, null=True)
    firstname = models.CharField(max_length=256, db_index=True, blank=True, null=True)
    username = models.CharField(max_length=256, db_index=True, unique=True)
    email = models.EmailField(max_length=256, db_index=True, blank=True, null=True)
    tel = models.CharField(max_length=15, db_index=True, blank=True, null=True)
    mobile = models.CharField(max_length=11, db_index=True, blank=True, null=True)
    national_code = models.CharField(max_length=10, db_index=True, blank=True, null=True)

    def __str__(self):
        return '{0}: {1} {1}'.format(self.identifier_key, self.firstname, self.lastname)


class Command(models.Model):
    KEYS = (('dslam', 'dslam'), ('slot', 'slot'), ('port', 'port'))
    text = models.CharField(max_length=256, verbose_name='name', unique=True)
    type = models.CharField(max_length=100, choices=KEYS, default='dslamport')
    show_command = models.BooleanField(default=False, verbose_name='Show command in port table')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text


class DSLAMTypeCommand(models.Model):
    command = models.ForeignKey(Command, on_delete=models.CASCADE)
    dslam_type = models.ForeignKey(DSLAMType, on_delete=models.CASCADE)
    command_template = models.CharField(max_length=256, blank=True, null=True)


class PortCommand(models.Model):
    dslam = models.ForeignKey(DSLAM, db_index=True, on_delete=models.CASCADE)
    card_ports = JSONField(blank=True, null=True)
    command = models.ForeignKey(Command, db_index=True, on_delete=models.CASCADE)
    value = JSONField(blank=True, null=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0} - {1} : {2} => {3}'.format(self.dslam.name, self.card_ports, self.command.text, self.value)

    class Meta:
        ordering = ('-created_at',)


class DSLAMCommand(models.Model):
    dslam = models.ForeignKey(DSLAM, db_index=True, on_delete=models.CASCADE)
    command = models.ForeignKey(Command, db_index=True, on_delete=models.CASCADE)
    value = JSONField(blank=True, null=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0} : {1} => {2}'.format(self.dslam.name, self.command.text, self.value)

    class Meta:
        ordering = ('-created_at',)


class DSLAMBulkCommandResult(models.Model):
    title = models.CharField(max_length=256)
    success_file = models.FileField(upload_to='bulk_command_result/')
    error_file = models.FileField(upload_to='bulk_command_result/')
    commands = ArrayField(models.CharField(max_length=1024, blank=True, null=True))
    result_file = models.FileField(upload_to='bulk_command_result/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TelecomContractType(models.Model):
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class EquipmentCategoryType(models.Model):
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class EquipmentCategory(models.Model):
    title = models.CharField(max_length=256)
    equipment_category_type = models.ForeignKey(EquipmentCategoryType, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ActiveEquipmentCategory(models.Model):
    line_card_status_description = models.CharField(max_length=1000)
    port_rental_invoice_description = models.CharField(max_length=1000)
    assigned_gateways = models.IntegerField(null=True, blank=True, default=0)
    total_active_ports = models.IntegerField(null=True, blank=True, default=0)
    active_ports_assigned_percentage = models.IntegerField(null=True, blank=True, default=0)
    equipment_category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE)
    dslam_type = models.ForeignKey(DSLAMType, on_delete=models.CASCADE)
    telecom_center = models.ForeignKey(TelecomCenter, on_delete=models.CASCADE)


class PassiveEquipmentCategory(models.Model):
    passive_description = models.CharField(max_length=1000)
    passive_computing_port = models.IntegerField(null=True, blank=True, default=0)
    declared_passive_port = models.IntegerField(null=True, blank=True, default=0)
    passive_port_differences = models.IntegerField(null=True, blank=True, default=0)
    MDF_terminals_number = models.IntegerField(null=True, blank=True, default=0)
    pap_cruise_terminals_number = models.IntegerField(null=True, blank=True, default=0)
    equipment_category = models.ForeignKey(EquipmentCategoryType, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    equipment_mount_location = models.CharField(max_length=259)
    rack_space = models.CharField(max_length=259)
    cooling_status = models.BooleanField(default=False)
    equipment_category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE)
    telecom_center = models.ForeignKey(TelecomCenter, on_delete=models.CASCADE)


class Rented_port(models.Model):
    agent_name = models.CharField(max_length=256, null=True, blank=True)
    city_name = models.CharField(max_length=256, null=True, blank=True)
    telecom_name = models.CharField(max_length=256, null=True, blank=True)
    dslam_number = models.IntegerField(max_length=256, null=True, blank=True)
    card = models.IntegerField(max_length=256, null=True, blank=True)
    port = models.IntegerField(max_length=256, null=True, blank=True)
    telco_row = models.IntegerField(max_length=256, null=True, blank=True)
    telco_column = models.IntegerField(max_length=256, null=True, blank=True)
    telco_connection = models.IntegerField(max_length=256, null=True, blank=True)
    fqdn = models.CharField(max_length=256, null=True, blank=True)


class PowerEquipmentCategory(models.Model):
    routers_switches_converters_consumption = models.IntegerField(null=True, blank=True, default=0)
    server_cache_ventilation_fan_consumption = models.IntegerField(null=True, blank=True, default=0)
    dc_amperage_consumption = models.IntegerField(null=True, blank=True, default=0)
    dc_fuse_approved = models.CharField(max_length=259)
    dc_fuse_Invoiced = models.CharField(max_length=259)
    dc_amperage_difference = models.CharField(max_length=259)
    three_phase_ac_fuse_approved = models.CharField(max_length=259)
    phase_ac_fuse_approved = models.CharField(max_length=259)
    ac_fuse_Invoiced = models.CharField(max_length=259)
    ac_amperage_difference = models.CharField(max_length=259)
    ac_dc_converter = models.CharField(max_length=259)
    amperage_status_description = models.CharField(max_length=1000)
    equipment_category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE)
    telecom_center = models.ForeignKey(TelecomCenter, on_delete=models.CASCADE)


class EquipmentlinksInfo(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    telecom_center = models.ForeignKey(TelecomCenter, on_delete=models.CASCADE)
    telecom_center_contract_type = models.ForeignKey(TelecomContractType, on_delete=models.CASCADE)
    equipment_category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE)
    reseller_name = models.CharField(max_length=256)
    dslam_type = models.ForeignKey(DSLAMType, on_delete=models.CASCADE)


class CapacityType(models.Model):
    title = models.CharField(max_length=256)

    def __str__(self):
        return self.title


class CraPrice(models.Model):
    Capacity = models.ForeignKey(CapacityType, on_delete=models.CASCADE)
    infrastructure_price = models.IntegerField(null=True, blank=True, default=0)
    infrastructure_price = models.IntegerField(null=True, blank=True, default=0)
    non_interurban_infrastructure_price = models.IntegerField(null=True, blank=True, default=0)
    non_urban_infrastructure_price = models.IntegerField(null=True, blank=True, default=0)


class LocationType(models.Model):
    title = models.CharField(max_length=256)


class Location(models.Model):
    title = models.CharField(max_length=256)
    location_type = models.ForeignKey(LocationType, on_delete=models.CASCADE)


class RouterType(models.Model):
    title = models.CharField(max_length=256)


class RouterBrand(models.Model):
    title = models.CharField(max_length=256)
    router_type = models.ForeignKey(RouterType, on_delete=models.CASCADE)


class Router(models.Model):
    router_type = models.ForeignKey(RouterType, on_delete=models.CASCADE)
    router_brand = models.ForeignKey(RouterBrand, on_delete=models.CASCADE)
    device_interfaceid = models.IntegerField(null=True, blank=True, default=0)
    host_id = models.IntegerField(null=True, blank=True, default=0)
    device_name = models.CharField(max_length=256, null=True, blank=True)
    device_ip = models.CharField(max_length=256)
    device_fqdn = models.CharField(max_length=256)


class SwitchType(models.Model):
    title = models.CharField(max_length=256)


class SwitchBrand(models.Model):
    title = models.CharField(max_length=256)
    Switch_type = models.ForeignKey(SwitchType, on_delete=models.CASCADE)


class Switch(models.Model):
    Switch_type = models.ForeignKey(SwitchType, on_delete=models.CASCADE)
    Switch_brand = models.ForeignKey(SwitchBrand, on_delete=models.CASCADE)
    device_interfaceid = models.IntegerField(null=True, blank=True, default=0)
    host_id = models.IntegerField(null=True, blank=True, default=0)
    device_name = models.CharField(max_length=256, null=True, blank=True)
    device_ip = models.CharField(max_length=256)
    device_fqdn = models.CharField(max_length=256)


class TestModel(models.Model):
    agent_name = models.CharField(max_length=256, null=True, blank=True)
    city_name = models.CharField(max_length=256, null=True, blank=True)
    telecom_name = models.CharField(max_length=256, null=True, blank=True)
    dslam_number = models.IntegerField(max_length=256, null=True, blank=True)
    card = models.IntegerField(max_length=256, null=True, blank=True)
    port = models.IntegerField(max_length=256, null=True, blank=True)
    telco_row = models.IntegerField(max_length=256, null=True, blank=True)
    telco_column = models.IntegerField(max_length=256, null=True, blank=True)
    telco_connection = models.IntegerField(max_length=256, null=True, blank=True)
