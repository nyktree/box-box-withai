from decimal import Decimal
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC
from customers.models import Customer, Vehicle
from services.models import CauseSuggestion, Damage, DamageCategory, Part, ServiceOrder, ServicePart

class Command(BaseCommand):
    help = "Carrega dados fictícios para demonstração do Box Box."

    def handle(self, *args, **options):
        roles = {name: Group.objects.get_or_create(name=name)[0] for name in (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)}
        users = {}
        for username, role, first in (("admin", ROLE_ADMIN, "Alex"), ("atendente", ROLE_ATTENDANT, "Marina"), ("mecanico", ROLE_MECHANIC, "Carlos")):
            user, _ = User.objects.get_or_create(username=username, defaults={"first_name": first, "email": f"{username}@boxbox.local"})
            user.set_password("boxbox123"); user.is_active = True; user.save(); user.groups.set([roles[role]]); users[username] = user
        customer, _ = Customer.objects.get_or_create(document="123.456.789-00", defaults={"name": "Rafael Mendes", "phone": "(11) 99999-1111", "email": "rafael@example.com"})
        vehicle, _ = Vehicle.objects.get_or_create(plate="BOX2B24", defaults={"owner": customer, "brand": "Toyota", "model": "Corolla", "year": 2021, "mileage": 48320, "color": "Grafite"})
        category, _ = DamageCategory.objects.get_or_create(name="Sistema de arrefecimento", defaults={"keywords": "superaquecimento,aquecendo,temperatura"})
        cause, _ = CauseSuggestion.objects.get_or_create(category=category, cause="Baixo nível do líquido", defaults={"priority": 10, "explanation": "Verificar vazamentos e nível do reservatório."})
        part, _ = Part.objects.get_or_create(name="Válvula termostática", defaults={"code": "VT-001", "stock_quantity": 3, "unit_price": Decimal("189.90")})
        statuses = [ServiceOrder.Status.WAITING_PARTS, ServiceOrder.Status.IN_MAINTENANCE, ServiceOrder.Status.READY]
        for index, status in enumerate(statuses, 1):
            order, created = ServiceOrder.objects.get_or_create(vehicle=vehicle, complaint=f"Atendimento demonstrativo {index}", defaults={"attendant": users["atendente"], "mechanic": users["mecanico"], "entry_mileage": 48320 + index * 100, "status": status, "estimated_value": Decimal("450.00")})
            if created:
                damage = Damage.objects.create(order=order, category=category, title="Temperatura elevada", symptom="Motor apresenta temperatura acima do normal", diagnosis="Verificação do sistema de arrefecimento", confirmed_cause=cause, resolved=status == ServiceOrder.Status.READY)
                ServicePart.objects.create(order=order, damage=damage, part=part, quantity=1, unit_price=part.unit_price)
        self.stdout.write(self.style.SUCCESS("Dados demonstrativos carregados. Login: admin / boxbox123"))
