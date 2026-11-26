from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from customers.models import Customer, Vehicle
from services.models import ServiceOrder

class DashboardTests(TestCase):
    def test_dashboard_shows_real_order_and_status(self):
        user = User.objects.create_user("admin", password="test123", is_superuser=True)
        owner = Customer.objects.create(name="Cliente", phone="1")
        vehicle = Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020)
        order = ServiceOrder.objects.create(vehicle=vehicle, attendant=user, complaint="Revisão", status=ServiceOrder.Status.IN_MAINTENANCE)
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, order.number)
        self.assertContains(response, "Em manutenção")
