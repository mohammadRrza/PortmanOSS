from django.contrib import admin
from contact.models import ContactType, Contact, Order, PortmapState, Province, City, CenterType, FarzaneganProvider

admin.site.register(ContactType)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(PortmapState)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(CenterType)
admin.site.register(FarzaneganProvider)
