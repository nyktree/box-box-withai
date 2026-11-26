from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from customers.models import Vehicle


class OrderSequence(models.Model):
    year = models.PositiveIntegerField(unique=True)
    next_number = models.PositiveIntegerField(default=1)


class ServiceOrder(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Aberta"
        WAITING_DIAGNOSIS = "WAITING_DIAGNOSIS", "Aguardando diagnóstico"
        WAITING_PARTS = "WAITING_PARTS", "Aguardando peças"
        IN_MAINTENANCE = "IN_MAINTENANCE", "Em manutenção"
        READY = "READY", "Pronta para entrega"
        DELIVERED = "DELIVERED", "Entregue"
        CANCELLED = "CANCELLED", "Cancelada"

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="service_orders")
    mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assigned_orders", null=True, blank=True)
    attendant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="opened_orders")
    number = models.CharField(max_length=16, unique=True, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)
    entry_mileage = models.PositiveIntegerField(default=0)
    complaint = models.TextField()
    notes = models.TextField(blank=True)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)])
    final_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    completed_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("-opened_at",)

    def save(self, *args, **kwargs):
        if not self.number:
            year = timezone.localdate().year
            with transaction.atomic():
                sequence, _ = OrderSequence.objects.get_or_create(year=year)
                sequence = OrderSequence.objects.select_for_update().get(pk=sequence.pk)
                current = sequence.next_number
                sequence.next_number = current + 1
                sequence.save(update_fields=["next_number"])
                self.number = f"BB-{year}-{current:04d}"
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    def __str__(self): return self.number


class StatusHistory(models.Model):
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name="status_history")
    previous_status = models.CharField(max_length=32)
    new_status = models.CharField(max_length=32)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("created_at",)


class DamageCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    keywords = models.TextField(blank=True)
    def __str__(self): return self.name


class CauseSuggestion(models.Model):
    category = models.ForeignKey(DamageCategory, on_delete=models.CASCADE, related_name="suggestions")
    cause = models.CharField(max_length=200)
    explanation = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    def __str__(self): return self.cause


class Damage(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Baixa"; MEDIUM = "MEDIUM", "Média"; HIGH = "HIGH", "Alta"; CRITICAL = "CRITICAL", "Crítica"
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name="damages")
    category = models.ForeignKey(DamageCategory, on_delete=models.PROTECT, related_name="damages")
    title = models.CharField(max_length=140)
    symptom = models.TextField()
    diagnosis = models.TextField(blank=True)
    confirmed_cause = models.ForeignKey(CauseSuggestion, on_delete=models.SET_NULL, null=True, blank=True, related_name="confirmed_damages")
    custom_cause = models.CharField(max_length=255, blank=True)
    severity = models.CharField(max_length=16, choices=Severity.choices, default=Severity.MEDIUM)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Part(models.Model):
    name = models.CharField(max_length=140)
    code = models.CharField(max_length=60, blank=True, unique=True, null=True)
    description = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name


class DamagePartSuggestion(models.Model):
    category = models.ForeignKey(DamageCategory, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    class Meta: unique_together = (("category", "part"),)


class ServicePart(models.Model):
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name="used_parts")
    damage = models.ForeignKey(Damage, on_delete=models.SET_NULL, null=True, blank=True, related_name="used_parts")
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    @property
    def total(self): return self.quantity * self.unit_price
