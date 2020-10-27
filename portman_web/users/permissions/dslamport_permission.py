from rest_framework import permissions
from dslam.models import DSLAMPort

class DSLAMPortView(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if view.action == 'list': # add query to limit
            allowed_ports = request.user.get_user_dslamports('view_dslam')
            if not allowed_ports:
                return False
            view.queryset = view.queryset.filter(pk__in=allowed_ports)
            return True
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            dslamport_id = obj.pk

        if request.user.has_permission_to_dslamport('view_dslam', dslamport_id):
            return True
        return False

class DSLAMPortEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        actions = ['create', 'update', 'destroy', 'partial_update']
        if view.action not in actions:
            return True
        if request.user.is_superuser:
            return True
        if request.user.has_permission_to_dslamport('edit_dslamport', obj.pk):
            return True
        return False
