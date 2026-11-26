from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from customers.models import Customer, Vehicle
from services.models import Part, ServiceOrder, ServicePart

class PartTests(TestCase):
    def test_service_part_snapshots_price_and_rejects_zero_quantity(self):
        owner = Customer.objects.create(name="Cliente", phone="1")
        vehicle = Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020)
        user = User.objects.create_user("atendente")
        order = ServiceOrder.objects.create(vehicle=vehicle, attendant=user, complaint="Revisão", entry_mileage=10)
        part = Part.objects.create(name="Filtro", unit_price=Decimal("35.90"), stock_quantity=5)
        used = ServicePart(order=order, part=part, quantity=0, unit_price=part.unit_price)
        with self.assertRaises(ValidationError): used.full_clean()
        used.quantity = 2; used.full_clean(); used.save()
        self.assertEqual(used.unit_price, Decimal("35.90"))
        self.assertEqual(Part.objects.get(pk=part.pk).stock_quantity, 5)

    def test_authenticated_user_can_open_part_catalog(self):
        user = User.objects.create_user("catalogo", password="test123", is_superuser=True)
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("part_list")).status_code, 200)
