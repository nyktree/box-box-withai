from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from customers.models import Customer, Vehicle, normalize_plate


class VehicleTests(TestCase):
    def test_normalize_plate_removes_punctuation_and_uppercases(self):
        self.assertEqual(normalize_plate("abc-1d23"), "ABC1D23")

    def test_plate_is_unique_and_mileage_non_negative(self):
        owner = Customer.objects.create(name="Maria", phone="11999999999")
        Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020, mileage=100)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Vehicle.objects.create(owner=owner, plate="abc-1d23", brand="Nissan", model="Kicks", year=2021)
        invalid = Vehicle(owner=owner, plate="DEF2E34", brand="Honda", model="Civic", year=2022, mileage=-1)
        with self.assertRaises(ValidationError):
            invalid.full_clean()
