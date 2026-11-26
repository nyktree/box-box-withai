from django.contrib.auth.models import User
from django.test import TestCase
from customers.models import Customer, Vehicle
from services.models import CauseSuggestion, Damage, DamageCategory, ServiceOrder
from services.suggestions import get_suggestions

class SuggestionTests(TestCase):
    def test_suggestions_are_ordered_by_priority(self):
        owner = Customer.objects.create(name="Cliente", phone="1")
        vehicle = Vehicle.objects.create(owner=owner, plate="ABC1D23", brand="Toyota", model="Corolla", year=2020)
        user = User.objects.create_user("atendente")
        order = ServiceOrder.objects.create(vehicle=vehicle, attendant=user, complaint="motor aquecendo", entry_mileage=10)
        category = DamageCategory.objects.create(name="Arrefecimento", keywords="superaquecimento,aquecendo")
        low = CauseSuggestion.objects.create(category=category, cause="Sensor", priority=1)
        high = CauseSuggestion.objects.create(category=category, cause="Líquido baixo", priority=10)
        damage = Damage.objects.create(order=order, category=category, title="Superaquecimento", symptom="motor aquecendo")
        self.assertEqual(list(get_suggestions(damage)[:2]), [high, low])
