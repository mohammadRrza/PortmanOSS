from django.contrib import admin

from radio.models import RadioBrand, RadioType, Radio, RadioCommand, RadioGroup

class RadioAdmin(admin.ModelAdmin):
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


class RadioCommandAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'radio_command_description', 'radio_type'
    )
    list_filter = (
        'radio_command_description', 'radio_type'
    )

    ordering = (
        'radio_command_description', 'radio_type'

    )
    search_fields = ('radio_command_description', 'radio_type')


admin.site.register(RadioBrand)
admin.site.register(RadioType)
admin.site.register(RadioGroup)
admin.site.register(Radio, RadioAdmin)
admin.site.register(RadioCommand, RadioCommandAdmin)
