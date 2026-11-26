from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ATTENDANT, ROLE_MECHANIC
from customers.models import Customer, Vehicle
from services.models import ServiceOrder

class OrderViewTests(TestCase):
    def setUp(self):
        for role in (ROLE_ATTENDANT, ROLE_MECHANIC): Group.objects.get_or_create(name=role)
        self.attendant = User.objects.create_user("atendente"); self.attendant.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.mechanic = User.objects.create_user("mecanico"); self.mechanic.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        self.other = User.objects.create_user("outro"); self.other.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        owner = Customer.objects.create(name="Cliente", phone="1")
        vehicle = Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020)
        self.order = ServiceOrder.objects.create(vehicle=vehicle, attendant=self.attendant, mechanic=self.mechanic, complaint="Ruído")

    def test_attendant_opens_order_list(self):
        self.client.force_login(self.attendant)
        self.assertEqual(self.client.get(reverse("order_list")).status_code, 200)

    def test_unassigned_mechanic_cannot_update_order(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("order_update", args=[self.order.pk])).status_code, 403)

    def test_mechanic_only_sees_edit_for_assigned_order(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("order_list"))
        self.assertNotContains(response, reverse("order_update", args=[self.order.pk]))
        response = self.client.get(reverse("order_detail", args=[self.order.pk]))
        self.assertNotContains(response, reverse("order_update", args=[self.order.pk]))
        self.assertNotContains(response, reverse("order_transition", args=[self.order.pk]))

        self.client.force_login(self.mechanic)
        self.assertContains(self.client.get(reverse("order_list")), reverse("order_update", args=[self.order.pk]))
        detail = self.client.get(reverse("order_detail", args=[self.order.pk]))
        self.assertContains(detail, reverse("order_update", args=[self.order.pk]))
        self.assertContains(detail, reverse("order_transition", args=[self.order.pk]))
