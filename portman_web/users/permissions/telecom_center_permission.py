from rest_framework import permissions
class TelecomCenterView(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if view.action == 'list': # add query to limit
            allowed_telecom_centers = request.user.get_user_telecom_centers('view_telecom_center')
            if not allowed_telecom_centers:
                return False
            view.queryset = view.queryset.filter(pk__in=allowed_telecom_centers)
            return True
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.type == 'RESELLER':
            return True
        if request.user.has_permission_to_telecom_center('view_telecom_center', obj.pk):
            return True
        return False

class TelecomCenterEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        actions = ['update', 'destroy', 'partial_update']
        if view.action in actions:
            if request.user.type == 'RESELLER':
                return False
        if view.action not in actions:
            return True
        if request.user.is_superuser:
            return True
        if request.user.has_permission_to_telecom_center('edit_telecom_center', obj.pk):
            return True
        return False
