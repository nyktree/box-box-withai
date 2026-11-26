from django.db import models


class Customer(models.Model):
    name = models.CharField("nome", max_length=160)
    document = models.CharField("CPF/CNPJ", max_length=18, blank=True)
    phone = models.CharField("telefone", max_length=24)
    email = models.EmailField("e-mail", blank=True)
    address = models.CharField("endereço", max_length=255, blank=True)
    notes = models.TextField("observações", blank=True)
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return self.name


def normalize_plate(value):
    return "".join(ch for ch in (value or "").upper() if ch.isalnum())


class Vehicle(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="vehicles", verbose_name="proprietário")
    plate = models.CharField("placa", max_length=7, unique=True)
    brand = models.CharField("marca", max_length=80)
    model = models.CharField("modelo", max_length=100)
    year = models.PositiveIntegerField("ano")
    color = models.CharField("cor", max_length=40, blank=True)
    mileage = models.PositiveIntegerField("quilometragem", default=0)
    chassis = models.CharField("chassi", max_length=40, blank=True)
    notes = models.TextField("observações", blank=True)
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("plate",)
        verbose_name = "veículo"
        verbose_name_plural = "veículos"

    def save(self, *args, **kwargs):
        self.plate = normalize_plate(self.plate)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plate} · {self.brand} {self.model}"
