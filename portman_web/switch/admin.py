from django.contrib import admin

from switch.models import SwitchBrand, SwitchType, Switch

admin.site.register(SwitchBrand)
admin.site.register(SwitchType)
admin.site.register(Switch)

