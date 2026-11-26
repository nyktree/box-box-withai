from django.contrib.auth.models import User
from django.test import TestCase
from customers.models import Customer, Vehicle
from reports.exporters import export_orders_csv, export_orders_pdf
from services.models import ServiceOrder

class ReportExporterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("admin")
        owner = Customer.objects.create(name="José da Silva", phone="1")
        vehicle = Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020)
        ServiceOrder.objects.create(vehicle=vehicle, attendant=self.user, complaint="Revisão")

    def test_csv_contains_order_and_utf8_name(self):
        response = export_orders_csv(ServiceOrder.objects.all())
        text = response.content.decode("utf-8-sig")
        self.assertIn("José da Silva", text)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")

    def test_empty_pdf_is_valid(self):
        response = export_orders_pdf(ServiceOrder.objects.none())
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertEqual(response["Content-Type"], "application/pdf")
