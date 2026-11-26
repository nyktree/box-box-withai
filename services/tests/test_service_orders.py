from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC
from customers.models import Customer, Vehicle
from services.domain import transition_order
from services.models import ServiceOrder, StatusHistory


class ServiceOrderTests(TestCase):
    def setUp(self):
        for role in (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC): Group.objects.get_or_create(name=role)
        self.attendant = User.objects.create_user("atendente")
        self.attendant.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.mechanic = User.objects.create_user("mecanico")
        self.mechanic.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        owner = Customer.objects.create(name="Cliente", phone="11999999999")
        self.vehicle = Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020)

    def test_order_number_and_status_history(self):
        order = ServiceOrder.objects.create(vehicle=self.vehicle, attendant=self.attendant, complaint="Ruído", entry_mileage=100)
        self.assertRegex(order.number, r"^BB-\d{4}-\d{4}$")
        transition_order(order, ServiceOrder.Status.WAITING_DIAGNOSIS, self.attendant)
        self.assertEqual(StatusHistory.objects.filter(order=order).count(), 1)

    def test_invalid_transition_is_rejected(self):
        order = ServiceOrder.objects.create(vehicle=self.vehicle, attendant=self.attendant, complaint="Ruído", entry_mileage=100)
        with self.assertRaises(ValidationError):
            transition_order(order, ServiceOrder.Status.DELIVERED, self.attendant)

    def test_admin_permissions_override_other_group_restrictions(self):
        admin = User.objects.create_user("multi-role-admin")
        admin.groups.add(
            Group.objects.get(name=ROLE_ADMIN),
            Group.objects.get(name=ROLE_ATTENDANT),
            Group.objects.get(name=ROLE_MECHANIC),
        )
        order = ServiceOrder.objects.create(vehicle=self.vehicle, attendant=self.attendant, mechanic=self.mechanic, complaint="Ruído")
        transition_order(order, ServiceOrder.Status.WAITING_DIAGNOSIS, admin)
        order.refresh_from_db()
        transition_order(order, ServiceOrder.Status.IN_MAINTENANCE, admin)
        order.refresh_from_db()
        self.assertEqual(order.status, ServiceOrder.Status.IN_MAINTENANCE)
