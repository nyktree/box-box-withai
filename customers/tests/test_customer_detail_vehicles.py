from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ATTENDANT
from customers.models import Customer, Vehicle

class CustomerDetailVehicleTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name=ROLE_ATTENDANT)
        user = User.objects.create_user("atendente", password="x")
        user.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.client.force_login(user)
        self.customer = Customer.objects.create(name="Rafael", phone="1")
        self.other = Customer.objects.create(name="Outro", phone="2")

    def vehicle(self, owner, plate, active=True):
        return Vehicle.objects.create(owner=owner, plate=plate, brand="Toyota", model="Corolla", year=2024, mileage=12000, is_active=active)

    def test_detail_lists_only_active_vehicles_owned_by_customer(self):
        visible = self.vehicle(self.customer, "AAA1A11")
        hidden_other = self.vehicle(self.other, "BBB2B22")
        hidden_archived = self.vehicle(self.customer, "CCC3C33", active=False)
        response = self.client.get(reverse("customer_detail", args=[self.customer.pk]))
        self.assertContains(response, visible.plate)
        self.assertContains(response, "Toyota Corolla")
        self.assertNotContains(response, hidden_other.plate)
        self.assertNotContains(response, hidden_archived.plate)

    def test_detail_shows_empty_state_without_active_vehicles(self):
        response = self.client.get(reverse("customer_detail", args=[self.customer.pk]))
        self.assertContains(response, "Nenhum veículo ativo vinculado")

    def test_new_vehicle_from_customer_preserves_owner(self):
        detail = self.client.get(reverse("customer_detail", args=[self.customer.pk]))
        create_url = f'{reverse("vehicle_create")}?owner={self.customer.pk}'
        self.assertContains(detail, create_url)
        create = self.client.get(create_url)
        self.assertEqual(create.context["form"].initial["owner"], self.customer.pk)
