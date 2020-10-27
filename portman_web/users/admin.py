from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from users.models import Permission, PermissionProfile, PermissionProfilePermission, \
    UserPermissionProfile, UserPermissionProfileObject

User = get_user_model()


class MyUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    form = MyUserForm
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('type', 'tel', 'reseller')}),
    )


class UserPermissionProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'permission_profile')


class PermissionProfilePermissionInline(admin.TabularInline):
    model = PermissionProfilePermission

class PermissionProfileAdmin(admin.ModelAdmin):
    inlines = [PermissionProfilePermissionInline,]

admin.site.register(Permission)
admin.site.register(PermissionProfile, PermissionProfileAdmin)
admin.site.register(PermissionProfilePermission)
admin.site.register(UserPermissionProfile, UserPermissionProfileAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(UserPermissionProfileObject)

