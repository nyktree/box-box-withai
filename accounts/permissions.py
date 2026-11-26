from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

ROLE_ADMIN = "Administrador"
ROLE_ATTENDANT = "Atendente"
ROLE_MECHANIC = "Mecânico"
ROLES = (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)


def user_has_role(user, role_name):
    return bool(user and user.is_authenticated and (user.is_superuser or user.groups.filter(name=role_name).exists()))


def role_required(*roles):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_superuser and not request.user.groups.filter(name__in=roles).exists():
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapped
    return decorator
