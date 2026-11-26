import json
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from accounts.permissions import ROLE_ATTENDANT, ROLE_MECHANIC
from assistente import agente
from assistente.models import LinkCliente, PerguntaCliente
from customers.models import Customer, Vehicle
from services.models import Damage, DamageCategory, Part, ServiceOrder, ServicePart


class ModeloTests(TestCase):
    def test_classifica_intencoes_basicas(self):
        casos = {
            "quando fica pronto meu carro?": "prazo",
            "quanto vai custar o conserto": "valor",
            "o que foi trocado": "pecas",
            "o que significa aguardando peças": "significado_status",
            "vocês aceitam pix?": "fora_escopo",
        }
        for frase, esperado in casos.items():
            self.assertEqual(agente.classificar(frase)["intencao"], esperado, frase)

    def test_confianca_e_alternativas(self):
        decisao = agente.classificar("qual a previsao de entrega")
        self.assertGreaterEqual(decisao["confianca"], decisao["limiar"])
        self.assertEqual(len(decisao["alternativas"]), 3)


class AssistenteTests(TestCase):
    def setUp(self):
        for papel in (ROLE_ATTENDANT, ROLE_MECHANIC):
            Group.objects.get_or_create(name=papel)
        self.atendente = User.objects.create_user("marina", password="x")
        self.atendente.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.mecanico = User.objects.create_user("carlos", password="x")
        self.mecanico.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        dono = Customer.objects.create(name="Ana Souza", phone="1")
        veiculo = Vehicle.objects.create(owner=dono, plate="TST1A23", brand="Fiat", model="Argo", year=2022)
        self.ordem = ServiceOrder.objects.create(vehicle=veiculo, attendant=self.atendente, mechanic=self.mecanico,
                                                 complaint="Esquentando", estimated_value=Decimal("680.00"),
                                                 status=ServiceOrder.Status.WAITING_PARTS)
        categoria = DamageCategory.objects.create(name="Arrefecimento")
        avaria = Damage.objects.create(order=self.ordem, category=categoria, title="Ventoinha",
                                       symptom="Não liga", diagnosis="Relé queimado")
        peca = Part.objects.create(name="Relé", unit_price=Decimal("89.90"))
        ServicePart.objects.create(order=self.ordem, damage=avaria, part=peca, quantity=1, unit_price=peca.unit_price)
        self.link = LinkCliente.objects.create(order=self.ordem, criado_por=self.atendente)
        self.url = reverse("cliente_perguntar", args=[self.link.token])

    def perguntar(self, texto):
        return self.client.post(self.url, json.dumps({"pergunta": texto}), content_type="application/json")

    def test_pagina_do_cliente_abre_sem_login(self):
        resposta = self.client.get(reverse("cliente_acompanhar", args=[self.link.token]))
        self.assertContains(resposta, self.ordem.number)
        self.assertContains(resposta, "Aguardando peças")

    def test_responde_com_dados_registrados_e_registra_a_pergunta(self):
        dados = self.perguntar("o que foi trocado no carro?").json()
        self.assertEqual(dados["intencao"], "pecas")
        self.assertIn("Relé", dados["resposta"])
        self.assertEqual(PerguntaCliente.objects.count(), 1)

    def test_nao_inventa_prazo(self):
        dados = self.perguntar("quando fica pronto?").json()
        self.assertIn("Ainda não há previsão", dados["resposta"])

    def test_valor_vem_da_ordem(self):
        self.assertIn("R$ 680,00", self.perguntar("quanto vai custar?").json()["resposta"])

    def test_link_errado_ou_cancelado_nao_acessa(self):
        self.assertEqual(self.client.get(reverse("cliente_acompanhar", args=["token-falso"])).status_code, 404)
        self.link.revogado = True
        self.link.save()
        self.assertEqual(self.perguntar("qual o status?").status_code, 404)

    def test_link_expira_na_entrega(self):
        ServiceOrder.objects.filter(pk=self.ordem.pk).update(status=ServiceOrder.Status.DELIVERED)
        self.assertEqual(self.client.get(reverse("cliente_acompanhar", args=[self.link.token])).status_code, 404)

    def test_pergunta_vazia_ou_longa_e_recusada(self):
        self.assertEqual(self.perguntar("").status_code, 400)
        self.assertEqual(self.perguntar("a" * 301).status_code, 400)

    def test_mecanico_nao_gera_link(self):
        self.client.force_login(self.mecanico)
        resposta = self.client.post(reverse("assistente_gerar_link", args=[self.ordem.pk]))
        self.assertEqual(resposta.status_code, 403)

    def test_atendente_gera_novo_link_e_cancela_o_anterior(self):
        self.client.force_login(self.atendente)
        self.client.post(reverse("assistente_gerar_link", args=[self.ordem.pk]))
        self.link.refresh_from_db()
        self.assertTrue(self.link.revogado)
        self.assertEqual(self.ordem.links_cliente.filter(revogado=False).count(), 1)

    def test_detalhe_da_ordem_mostra_painel(self):
        self.client.force_login(self.atendente)
        resposta = self.client.get(reverse("order_detail", args=[self.ordem.pk]))
        self.assertContains(resposta, "Assistente do cliente")
        self.assertContains(resposta, self.link.token)

    def test_api_classificar(self):
        resposta = self.client.post(reverse("assistente_api_classificar"), json.dumps({"pergunta": "qual o valor?"}),
                                    content_type="application/json")
        self.assertEqual(resposta.json()["intencao"], "valor")
