from django.contrib import admin

from router.models import RouterBrand, RouterType, Router,RouterCommand

admin.site.register(RouterBrand)
admin.site.register(RouterType)
admin.site.register(Router)
admin.site.register(RouterCommand)

