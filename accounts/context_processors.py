from .permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC

def role_capabilities(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    is_admin = user.is_superuser or user.groups.filter(name=ROLE_ADMIN).exists()
    is_attendant = user.groups.filter(name=ROLE_ATTENDANT).exists()
    is_mechanic = user.groups.filter(name=ROLE_MECHANIC).exists()
    can_operate_front_desk = is_admin or is_attendant
    return {
        "is_admin_role": is_admin,
        "is_attendant_role": is_attendant,
        "is_mechanic_role": is_mechanic,
        "can_create_orders": can_operate_front_desk,
        "can_create_customers": can_operate_front_desk,
        "can_create_vehicles": can_operate_front_desk,
        "can_manage_part_catalog": can_operate_front_desk,
    }
