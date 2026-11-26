"""Cria uma ordem completa para demonstrar o Assistente do cliente e mostra o link de acesso.

Uso:  python manage.py demo_assistente
Pode rodar mais de uma vez: reaproveita a mesma ordem de demonstração.
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC
from assistente.models import LinkCliente
from customers.models import Customer, Vehicle
from services.models import Damage, DamageCategory, Part, ServiceOrder, ServicePart, StatusHistory

PLACA = "IAD2B26"
RECLAMACAO = "Carro esquentando quando fica parado no trânsito. A ventoinha parece não ligar."


def usuario(papel):
    user = User.objects.filter(groups__name=papel, is_active=True).first() or \
        User.objects.filter(is_superuser=True).first()
    if not user:
        raise CommandError("Nenhum usuário encontrado. Rode antes: python manage.py seed_demo")
    return user


class Command(BaseCommand):
    help = "Cria a ordem de demonstração do Assistente do cliente (IA) e imprime o link."

    def handle(self, *args, **options):
        atendente = usuario(ROLE_ATTENDANT)
        mecanico = usuario(ROLE_MECHANIC)
        admin = usuario(ROLE_ADMIN)
        agora = timezone.now()

        cliente, _ = Customer.objects.get_or_create(
            document="987.654.321-00", defaults={"name": "Ana Souza", "phone": "(84) 98888-2026",
                                                 "email": "ana.souza@example.com"})
        veiculo, _ = Vehicle.objects.get_or_create(
            plate=PLACA, defaults={"owner": cliente, "brand": "Fiat", "model": "Argo", "year": 2022,
                                   "mileage": 35210, "color": "Branco"})
        ordem = ServiceOrder.objects.filter(vehicle=veiculo, complaint=RECLAMACAO, is_archived=False) \
            .exclude(status__in=[ServiceOrder.Status.DELIVERED, ServiceOrder.Status.CANCELLED]).first()

        if not ordem:
            ordem = ServiceOrder.objects.create(
                vehicle=veiculo, attendant=atendente, mechanic=mecanico, complaint=RECLAMACAO,
                entry_mileage=35210, expected_delivery=timezone.localdate() + timedelta(days=3),
                estimated_value=Decimal("680.00"), status=ServiceOrder.Status.WAITING_PARTS)
            ServiceOrder.objects.filter(pk=ordem.pk).update(opened_at=agora - timedelta(days=2, hours=5))
            etapas = [
                (ServiceOrder.Status.OPEN, ServiceOrder.Status.WAITING_DIAGNOSIS, atendente,
                 agora - timedelta(days=2, hours=4), "Veículo encaminhado para avaliação."),
                (ServiceOrder.Status.WAITING_DIAGNOSIS, ServiceOrder.Status.WAITING_PARTS, mecanico,
                 agora - timedelta(days=1, hours=2), "Peças solicitadas ao fornecedor."),
            ]
            for anterior, novo, autor, quando, nota in etapas:
                item = StatusHistory.objects.create(order=ordem, previous_status=anterior, new_status=novo,
                                                    actor=autor, note=nota)
                StatusHistory.objects.filter(pk=item.pk).update(created_at=quando)

            categoria, _ = DamageCategory.objects.get_or_create(
                name="Sistema de arrefecimento", defaults={"keywords": "superaquecimento,aquecendo,temperatura"})
            avaria = Damage.objects.create(
                order=ordem, category=categoria, title="Eletroventilador sem acionamento",
                symptom="Temperatura sobe com o carro parado; ventoinha não liga.",
                diagnosis="Relé do eletroventilador queimado e sensor de temperatura com leitura instável.",
                severity=Damage.Severity.HIGH)
            for nome, codigo, preco in (("Relé do eletroventilador", "RL-040", "89.90"),
                                        ("Sensor de temperatura", "ST-112", "129.90")):
                peca, _ = Part.objects.get_or_create(name=nome, defaults={"code": codigo, "stock_quantity": 2,
                                                                          "unit_price": Decimal(preco)})
                ServicePart.objects.create(order=ordem, damage=avaria, part=peca, quantity=1,
                                           unit_price=peca.unit_price)
            self.stdout.write(self.style.SUCCESS(f"Ordem de demonstração criada: {ordem.number}"))
        else:
            self.stdout.write(f"Ordem de demonstração já existe: {ordem.number}")

        link = ordem.links_cliente.filter(revogado=False).first() or \
            LinkCliente.objects.create(order=ordem, criado_por=admin)
        self.stdout.write(self.style.SUCCESS(
            f"Link do cliente: http://127.0.0.1:8000/acompanhar/{link.token}/"))
