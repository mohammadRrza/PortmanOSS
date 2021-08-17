from django.contrib import admin

from router.models import RouterBrand, RouterType, Router, RouterCommand, RouterGroup

class RouterAdmin(admin.ModelAdmin):
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


class RouterCommandAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = (
        'router_command_description', 'router_type'
    )
    list_filter = (
        'router_command_description', 'router_type'
    )

    ordering = (
        'router_command_description', 'router_type'

    )
    search_fields = ('router_command_description', 'router_type')


admin.site.register(RouterBrand)
admin.site.register(RouterType)
admin.site.register(RouterGroup)
admin.site.register(Router, RouterAdmin)
admin.site.register(RouterCommand, RouterCommandAdmin)
