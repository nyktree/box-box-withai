from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ATTENDANT
from customers.models import Customer, Vehicle
from services.models import ServiceOrder

class OrderCustomerGroupTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name=ROLE_ATTENDANT)
        self.user = User.objects.create_user("group-attendant", password="x")
        self.user.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.client.force_login(self.user)
        self.rafael = Customer.objects.create(name="Rafael", phone="1")
        self.marina = Customer.objects.create(name="Marina", phone="2")
        self.car_a = Vehicle.objects.create(owner=self.rafael, plate="RAF1A11", brand="Toyota", model="Corolla", year=2024)
        self.car_b = Vehicle.objects.create(owner=self.rafael, plate="RAF2B22", brand="Nissan", model="Kicks", year=2023)
        self.car_c = Vehicle.objects.create(owner=self.marina, plate="MAR3C33", brand="Honda", model="Civic", year=2022)
        self.ready = ServiceOrder.objects.create(vehicle=self.car_a, attendant=self.user, mechanic=self.user, complaint="A", status=ServiceOrder.Status.READY)
        self.open = ServiceOrder.objects.create(vehicle=self.car_b, attendant=self.user, mechanic=self.user, complaint="B", status=ServiceOrder.Status.OPEN)
        self.other = ServiceOrder.objects.create(vehicle=self.car_c, attendant=self.user, mechanic=self.user, complaint="C", status=ServiceOrder.Status.OPEN)

    def test_orders_are_grouped_by_owner(self):
        response = self.client.get(reverse("order_list"))
        groups = response.context["customer_groups"]
        self.assertEqual([group["customer"] for group in groups], [self.marina, self.rafael])
        rafael = next(group for group in groups if group["customer"] == self.rafael)
        self.assertEqual(rafael["order_count"], 2)
        self.assertEqual(rafael["vehicle_count"], 2)
        self.assertEqual(set(rafael["orders"]), {self.ready, self.open})

    def test_search_and_status_are_applied_before_grouping(self):
        response = self.client.get(reverse("order_list"), {"q": self.car_a.plate, "status": ServiceOrder.Status.READY})
        groups = response.context["customer_groups"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["customer"], self.rafael)
        self.assertEqual(groups[0]["orders"], [self.ready])
        self.assertEqual(groups[0]["vehicle_count"], 1)

    def test_page_renders_customer_folder_and_native_dialog(self):
        response = self.client.get(reverse("order_list"))
        self.assertContains(response, 'class="customer-folder"')
        self.assertContains(response, 'class="customer-orders-dialog"')
        self.assertContains(response, "Rafael")
        self.assertContains(response, self.ready.number)
        self.assertContains(response, reverse("order_detail", args=[self.ready.pk]))
        self.assertContains(response, 'aria-labelledby="customer-orders-title-')
        self.assertContains(response, "ordens ·")
        self.assertNotContains(response, "ordemens")
