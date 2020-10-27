from rest_framework import permissions
class CommandView(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if view.action == 'list': # add query to limit
            allowed_commands = request.user.get_user_commands('view_command')
            if not allowed_commands:
                return False
            view.queryset = view.queryset.filter(pk__in=allowed_commands)
            return True
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.has_permission_to_command('view_command', obj.pk):
            return True
        return False

class CommandEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        actions = ['create', 'update', 'destroy', 'partial_update']
        if view.action not in actions:
            return True
        if request.user.is_superuser:
            return True
        if request.user.has_permission_to_dslam('edit_command', obj.pk):
            return True
        return False
