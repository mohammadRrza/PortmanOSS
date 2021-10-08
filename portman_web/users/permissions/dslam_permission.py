from rest_framework import permissions
class DSLAMView(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if view.action == 'list': # add query to limit
            allowed_dslams = request.user.get_user_dslams('view_dslam')
            if not allowed_dslams:
                return False
            view.queryset = view.queryset.filter(pk__in=allowed_dslams)
            return True
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.type == 'RESELLER':
            return True
        if request.user.has_permission_to_dslam('view_dslam', obj.pk):
            return True
        return False

class DSLAMEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        actions = ['update', 'destroy', 'partial_update']
        if view.action in actions:
            if request.user.type == 'RESELLER':
                return False
        if view.action not in actions:
            return True
        if request.user.is_superuser:
            return True
        if request.user.has_permission_to_dslam('edit_dslam', obj.pk):
            return True
        return False
