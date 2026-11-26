from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC
from customers.models import Customer, Vehicle
from services.domain import transition_order
from services.models import Damage, DamageCategory, Part, ServiceOrder, StatusHistory

class FinalReviewRegressionTests(TestCase):
    def setUp(self):
        for role in (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC): Group.objects.get_or_create(name=role)
        self.admin = User.objects.create_user("admin2", password="x"); self.admin.groups.add(Group.objects.get(name=ROLE_ADMIN))
        self.attendant = User.objects.create_user("att2", password="x"); self.attendant.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.mechanic = User.objects.create_user("mec2", password="x"); self.mechanic.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        self.customer = Customer.objects.create(name="Cliente Histórico", phone="1")
        self.vehicle = Vehicle.objects.create(owner=self.customer, plate="REV1E23", brand="Nissan", model="Versa", year=2022)
        self.category = DamageCategory.objects.create(name="Motor")

    def make_order(self, status=ServiceOrder.Status.OPEN):
        return ServiceOrder.objects.create(vehicle=self.vehicle, attendant=self.attendant, mechanic=self.mechanic, complaint="Falha", status=status)

    def test_finalized_order_rejects_edit_damage_and_part_until_admin_reopens(self):
        order = self.make_order(ServiceOrder.Status.DELIVERED)
        self.client.force_login(self.mechanic)
        self.assertEqual(self.client.post(reverse("order_update", args=[order.pk]), {"vehicle": self.vehicle.pk, "entry_mileage": 0, "complaint": "alterada", "estimated_value": 0}).status_code, 403)
        self.assertEqual(self.client.post(reverse("damage_create", args=[order.pk]), {"category": self.category.pk, "title": "x", "symptom": "x", "severity": "LOW"}).status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(reverse("order_reopen", args=[order.pk]), {"justification": "Correção necessária"}).status_code, 302)

    def test_ready_requires_diagnosis_or_technical_note(self):
        order = self.make_order(ServiceOrder.Status.IN_MAINTENANCE)
        with self.assertRaisesMessage(Exception, "diagnóstico"):
            transition_order(order, ServiceOrder.Status.READY, self.mechanic)
        Damage.objects.create(order=order, category=self.category, title="Falha", symptom="x", diagnosis="Componente testado")
        transition_order(order, ServiceOrder.Status.READY, self.mechanic)
        self.assertTrue(StatusHistory.objects.filter(order=order, new_status=ServiceOrder.Status.READY).exists())

    def test_vehicle_detail_renders_service_history(self):
        order = self.make_order(ServiceOrder.Status.DELIVERED)
        Damage.objects.create(order=order, category=self.category, title="Falha histórica", symptom="x", diagnosis="Diagnóstico histórico")
        self.client.force_login(self.admin)
        response = self.client.get(reverse("vehicle_detail", args=[self.vehicle.pk]))
        self.assertContains(response, order.number)
        self.assertContains(response, "Diagnóstico histórico")

    def test_reports_respect_role_scope_and_filters_do_not_leak(self):
        included = self.make_order(ServiceOrder.Status.READY)
        excluded = self.make_order(ServiceOrder.Status.CANCELLED)
        self.client.force_login(self.mechanic)
        self.assertEqual(self.client.get(reverse("report_csv")).status_code, 200)
        self.client.force_login(self.admin)
        response = self.client.get(reverse("report_csv"), {"status": ServiceOrder.Status.READY})
        text = response.content.decode("utf-8-sig")
        self.assertIn(included.number, text)
        self.assertNotIn(excluded.number, text)
