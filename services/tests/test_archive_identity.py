from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ATTENDANT
from customers.models import Customer, Vehicle
from services.models import ServiceOrder

class OrderIdentityAndArchiveTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name=ROLE_ATTENDANT)
        self.attendant = User.objects.create_user("marina", password="x", first_name="Marina")
        self.attendant.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        owner = Customer.objects.create(name="Cliente", phone="1")
        self.vehicle = Vehicle.objects.create(owner=owner, plate="AUT1A23", brand="Nissan", model="Kicks", year=2023)
        self.client.force_login(self.attendant)

    def test_create_page_displays_logged_in_attendant(self):
        response = self.client.get(reverse("order_create"))
        self.assertContains(response, "Marina")
        self.assertContains(response, "ATENDENTE RESPONSÁVEL")

    def test_post_cannot_forge_attendant(self):
        forged = User.objects.create_user("forged")
        response = self.client.post(reverse("order_create"), {"vehicle": self.vehicle.pk, "complaint": "Ruído", "entry_mileage": 10, "estimated_value": 0, "attendant": forged.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ServiceOrder.objects.latest("pk").attendant, self.attendant)

    def test_archived_order_leaves_operational_list(self):
        order = ServiceOrder.objects.create(vehicle=self.vehicle, attendant=self.attendant, complaint="Teste")
        self.client.post(reverse("order_archive", args=[order.pk]))
        order.refresh_from_db()
        self.assertTrue(order.is_archived)
        self.assertNotContains(self.client.get(reverse("order_list")), order.number)
        self.assertEqual(self.client.get(reverse("order_update", args=[order.pk])).status_code, 404)
