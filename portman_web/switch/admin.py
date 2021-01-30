from django.contrib import admin

from switch.models import SwitchBrand, SwitchType, Switch,SwitchCommand

admin.site.register(SwitchBrand)
admin.site.register(SwitchType)
admin.site.register(Switch)
admin.site.register(SwitchCommand)

