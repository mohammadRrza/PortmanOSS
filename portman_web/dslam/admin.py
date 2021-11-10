from django.contrib import admin

from dslam.models import DSLAM, DSLAMPort, DSLAMPortSnapshot, Command, PortCommand, CityLocation, DSLAMPortVlan, \
    DSLAMType, TelecomCenter, City, ResellerPort, CustomerPort, Terminal, DSLAMLocation, TelecomCenterLocation, \
    Reseller, MDFDSLAM, DSLAMTypeCommand, \
    TelecomContractType, EquipmentCategoryType, EquipmentCategory, ActiveEquipmentCategory, PassiveEquipmentCategory, \
    PowerEquipmentCategory, EquipmentlinksInfo, \
    CapacityType, CraPrice,TelecomCenterMDF

from dslam.admin_views import *


class DSLAMTypeCommandInline(admin.TabularInline):
    model = DSLAMTypeCommand
    extra = 1


class CommandAdmin(admin.ModelAdmin):
    inlines = [DSLAMTypeCommandInline, ]


class TelecomCenterAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'prefix_bukht_name',
    )
    search_fields = ('code', 'name', 'prefix_bukht_name')


class DSLAMAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'id', 'dslam_name_link', 'dslam_type', 'ip', 'active', 'status',
        'last_sync_formated', 'last_sync_duration', 'conn_type', 'get_snmp_community', 'set_snmp_community',
        'telnet_username', 'telnet_password', 'updated_at_formated', 'created_at_formated'
    )
    list_filter = (
        'dslam_type', 'active', 'status', 'conn_type'
    )

    ordering = (
        'name', 'dslam_type', 'ip', 'active', 'status', 'last_sync', 'conn_type',
        'snmp_port'
    )
    search_fields = ('name', 'ip',)

    def created_at_formated(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    created_at_formated.admin_other_field = 'created_at'
    created_at_formated.short_description = 'CREATED AT'

    def updated_at_formated(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')

    updated_at_formated.admin_other_field = 'updated_at'
    updated_at_formated.short_description = 'UPDATED AT'

    def last_sync_formated(self, obj):
        if not obj.last_sync:
            return ''

        return obj.last_sync.strftime('%Y-%m-%d %H:%M:%S')

    last_sync_formated.admin_other_field = 'last_sync'
    last_sync_formated.short_description = 'LAST SYNC'

    def dslam_name_link(self, obj):
        return '<a href="/admin/dslam-report?dslam_id=%s">%s</a>' % (obj.id, obj.name)

    dslam_name_link.allow_tags = True
    dslam_name_link.short_description = 'NAME'


class DSLAMPortAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = (
        'id', 'created_at_formated', 'updated_at_formated', 'dslam_name', 'slot_number', 'port_name_link',
        'port_index', 'admin_status', 'oper_status', 'line_profile'
    )

    list_filter = (
        'dslam__name', 'created_at', 'updated_at', 'admin_status', 'oper_status', 'line_profile'
    )

    ordering = (
        '-updated_at', '-id', 'dslam__name', 'slot_number', 'port_number', 'port_name', 'port_index', 'admin_status',
        'oper_status'
    )

    def created_at_formated(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    created_at_formated.admin_other_field = 'created_at'
    created_at_formated.short_description = 'CREATED AT'

    def updated_at_formated(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')

    updated_at_formated.admin_other_field = 'updated_at'
    updated_at_formated.short_description = 'UPDATED AT'

    def port_name_link(self, obj):
        return '<a href="/admin/port-report?dslam_id=%s&port_id=%s">%s</a>' % (obj.dslam.id, obj.id, obj.port_name)

    port_name_link.allow_tags = True
    port_name_link.short_description = 'NAME'


class DSLAMPortSnapshotAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = (
        'snp_date_formated', 'slot_number', 'port_number', 'port_index', 'port_name', 'line_profile',
        'admin_status', 'oper_status', 'upstream_snr', 'downstream_snr',
        'upstream_tx_rate', 'downstream_tx_rate', 'upstream_attenuation',
        'downstream_attenuation', 'upstream_attainable_rate',
        'downstream_attainable_rate'
    )

    ordering = ('-snp_date',)

    def snp_date_formated(self, obj):
        return obj.snp_date.strftime('%Y-%m-%d %H:%M:%S')

    snp_date_formated.admin_other_field = 'snp_date'
    snp_date_formated.short_description = 'SNP DATE'


admin.site.register_view('dslam-report', view=view_dslam_report)
admin.site.register_view('port-report', view=view_port_status_report)

admin.site.register(DSLAM, DSLAMAdmin)
admin.site.register(DSLAMPort, DSLAMPortAdmin)
admin.site.register(DSLAMPortSnapshot, DSLAMPortSnapshotAdmin)
admin.site.register(Command, CommandAdmin)
admin.site.register(PortCommand)
admin.site.register(City)
admin.site.register(TelecomCenter, TelecomCenterAdmin)
admin.site.register(DSLAMType)
admin.site.register(ResellerPort)
admin.site.register(CustomerPort)
admin.site.register(Terminal)
admin.site.register(DSLAMLocation)
admin.site.register(TelecomCenterLocation)
admin.site.register(CityLocation)
admin.site.register(DSLAMPortVlan)
admin.site.register(Reseller)
admin.site.register(MDFDSLAM)
admin.site.register(TelecomContractType)
admin.site.register(EquipmentCategoryType)
admin.site.register(EquipmentCategory)
admin.site.register(ActiveEquipmentCategory)
admin.site.register(PassiveEquipmentCategory)
admin.site.register(PowerEquipmentCategory)
admin.site.register(EquipmentlinksInfo)
admin.site.register(CapacityType)
admin.site.register(CraPrice)
admin.site.register(TelecomCenterMDF)
