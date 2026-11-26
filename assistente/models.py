import secrets

from django.conf import settings
from django.db import models

from services.models import ServiceOrder


def novo_token():
    # 32 caracteres aleatórios: impossível de adivinhar na prática
    return secrets.token_urlsafe(24)


class LinkCliente(models.Model):
    """Link seguro que dá ao cliente acesso a UMA ordem de serviço, sem login."""
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name="links_cliente")
    token = models.CharField(max_length=64, unique=True, default=novo_token, editable=False)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)
    revogado = models.BooleanField(default=False)

    class Meta:
        ordering = ("-criado_em",)

    def __str__(self):
        return f"Link da ordem {self.order.number}"


class PerguntaCliente(models.Model):
    """Registro de cada pergunta feita ao assistente e de como ele decidiu responder."""
    link = models.ForeignKey(LinkCliente, on_delete=models.CASCADE, related_name="perguntas")
    pergunta = models.CharField(max_length=300)
    intencao = models.CharField(max_length=40)
    confianca = models.FloatField()
    ferramenta = models.CharField(max_length=60, blank=True)
    resposta = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-criado_em",)
