from django.contrib import admin
from contact.models import ContactType, Contact, Order, PortmapState

admin.site.register(ContactType)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(PortmapState)
