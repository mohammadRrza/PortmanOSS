from users.models import UserAuditLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def add_audit_log(request, model_name, instance_id, action, description=None):
    return UserAuditLog.objects.create(
        username=request.user.username,
        model_name = model_name,
        instance_id = instance_id,
        action=action,
        description=description,
        ip=get_client_ip(request),
    )
