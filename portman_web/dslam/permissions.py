from rest_framework import permissions

class HasAccessToDslam(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.type == 'ADMIN':
            return True
        elif view.action == 'list' and request.user.type == 'RESELLER':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.type == 'ADMIN':
            return True
        else:
            return False

class HasAccessToDslamPort(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.type == 'RESELLER':
            if request.user.reseller.resellerport_set.filter(
                    port_name=obj.port_name,
                    dslam=obj.dslam,
            ).exists():
                return True
        else:
            return True

class HasAccessToDslamPortSnapshot(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.type == 'RESELLER':
            if request.user.reseller.resellerport_set.filter(
                    port_name=obj.port_name,
                    dslam_id=obj.dslam_id,
            ).exists():
                return True
        else:
            return True

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.type == 'ADMIN'
