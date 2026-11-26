from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from services.models import ServiceOrder
from accounts.permissions import ROLE_ADMIN, ROLE_MECHANIC, user_has_role

def build_order_queryset(params, user):
    qs = ServiceOrder.objects.filter(is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True).select_related("vehicle", "vehicle__owner", "mechanic", "attendant")
    if not user.is_superuser and not user_has_role(user, ROLE_ADMIN) and user_has_role(user, ROLE_MECHANIC):
        qs = qs.filter(mechanic=user)
    status = params.get("status")
    if status:
        if status not in ServiceOrder.Status.values: raise ValidationError("Status inválido.")
        qs = qs.filter(status=status)
    for key, lookup in (("start", "opened_at__date__gte"), ("end", "opened_at__date__lte")):
        value = params.get(key)
        if value:
            parsed = parse_date(value)
            if not parsed: raise ValidationError("Data inválida.")
            qs = qs.filter(**{lookup: parsed})
    if params.get("vehicle"): qs = qs.filter(vehicle__plate__icontains=params["vehicle"])
    if params.get("customer"): qs = qs.filter(vehicle__owner__name__icontains=params["customer"])
    if params.get("mechanic"): qs = qs.filter(mechanic_id=params["mechanic"])
    return qs
