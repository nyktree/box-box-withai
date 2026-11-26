from django.contrib.auth.models import Group, User
from django.test import TestCase
from accounts.permissions import ROLE_ADMIN
from customers.models import Customer, Vehicle
from services.domain import reopen_order
from services.models import ServiceOrder

class ReopeningTests(TestCase):
    def test_admin_reopens_delivered_order_with_justification(self):
        Group.objects.get_or_create(name=ROLE_ADMIN)
        admin = User.objects.create_user("admin"); admin.groups.add(Group.objects.get(name=ROLE_ADMIN))
        owner = Customer.objects.create(name="Cliente", phone="1")
        vehicle = Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020)
        order = ServiceOrder.objects.create(vehicle=vehicle, attendant=admin, complaint="Revisão", status=ServiceOrder.Status.DELIVERED)
        history = reopen_order(order, admin, "Retorno para correção")
        order.refresh_from_db()
        self.assertEqual(order.status, ServiceOrder.Status.WAITING_DIAGNOSIS)
        self.assertEqual(history.note, "Retorno para correção")
