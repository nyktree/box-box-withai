from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from customers.models import Customer, Vehicle
from services.models import ServiceOrder

class SeedDemoTests(TestCase):
    def test_seed_is_idempotent_and_creates_demo_data(self):
        call_command("seed_demo")
        counts = (User.objects.count(), Customer.objects.count(), Vehicle.objects.count(), ServiceOrder.objects.count())
        call_command("seed_demo")
        self.assertEqual(counts, (User.objects.count(), Customer.objects.count(), Vehicle.objects.count(), ServiceOrder.objects.count()))
        self.assertTrue(User.objects.filter(username="admin").exists())
        self.assertGreaterEqual(ServiceOrder.objects.count(), 3)
