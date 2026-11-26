from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC
from customers.models import Customer, Vehicle
from services.models import ServiceOrder

class ReportPermissionTests(TestCase):
    def setUp(self):
        for role in (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC): Group.objects.get_or_create(name=role)
        self.admin = User.objects.create_user("a", password="x"); self.admin.groups.add(Group.objects.get(name=ROLE_ADMIN))
        self.attendant = User.objects.create_user("t", password="x"); self.attendant.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.mechanic = User.objects.create_user("m", password="x"); self.mechanic.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        self.other = User.objects.create_user("o", password="x"); self.other.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        owner = Customer.objects.create(name="Cliente", phone="1")
        vehicle = Vehicle.objects.create(owner=owner, plate="REP1A23", brand="Toyota", model="Yaris", year=2022)
        self.mine = ServiceOrder.objects.create(vehicle=vehicle, attendant=self.attendant, mechanic=self.mechanic, complaint="Minha")
        self.theirs = ServiceOrder.objects.create(vehicle=vehicle, attendant=self.attendant, mechanic=self.other, complaint="Outra")

    def test_attendant_can_open_reports(self):
        self.client.force_login(self.attendant)
        self.assertEqual(self.client.get(reverse("report_index")).status_code, 200)

    def test_mechanic_sees_only_assigned_orders(self):
        self.client.force_login(self.mechanic)
        response = self.client.get(reverse("report_index"))
        self.assertContains(response, self.mine.number)
        self.assertNotContains(response, self.theirs.number)

    def test_superuser_is_not_scoped_as_mechanic(self):
        root = User.objects.create_superuser("root", "root@example.com", "x")
        root.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        self.client.force_login(root)
        response = self.client.get(reverse("report_index"))
        self.assertContains(response, self.mine.number)
        self.assertContains(response, self.theirs.number)
