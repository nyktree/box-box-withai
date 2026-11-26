from django.core.exceptions import ValidationError
from django.test import TestCase
from customers.models import Customer


class CustomerModelTests(TestCase):
    def test_customer_requires_name_and_phone(self):
        customer = Customer(name="", phone="")
        with self.assertRaises(ValidationError):
            customer.full_clean()

    def test_customer_can_be_deactivated(self):
        customer = Customer.objects.create(name="João Silva", phone="11999999999")
        customer.is_active = False
        customer.save()
        self.assertFalse(Customer.objects.get(pk=customer.pk).is_active)
