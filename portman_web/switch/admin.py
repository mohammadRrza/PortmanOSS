from django.contrib import admin

from switch.models import SwitchBrand, SwitchType, Switch, SwitchCommand, SwitchGroup


class SwitchAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'device_name', 'device_ip', 'device_fqdn',
    )
    list_filter = (
        'device_name', 'device_ip', 'device_fqdn',
    )

    ordering = (
        'device_name', 'device_ip', 'device_fqdn',

    )
    search_fields = ('device_name', 'device_ip', 'device_fqdn',)


admin.site.register(SwitchBrand)
admin.site.register(SwitchType)
admin.site.register(Switch, SwitchAdmin)
admin.site.register(SwitchCommand)
admin.site.register(SwitchGroup)

