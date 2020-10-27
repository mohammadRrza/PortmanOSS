from rest_framework import permissions

class UserManagement(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if view.action == 'retrieve':
            return True
        if request.user.has_permission('management_user'):
            return True
        if request.user == obj and not view.action == 'destroy':
            return True
        return False


class AccessManagement(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.has_permission('management_user'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.has_permission('management_user'):
            return True
        return False

