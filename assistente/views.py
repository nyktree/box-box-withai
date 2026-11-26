import json
from datetime import timedelta
from pathlib import Path

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, role_required
from services.models import ServiceOrder

from . import agente
from .models import LinkCliente, PerguntaCliente

LIMITE_PERGUNTAS = 30          # por link, a cada 10 minutos
TAMANHO_MAXIMO = 300
ENCERRADAS = {ServiceOrder.Status.DELIVERED, ServiceOrder.Status.CANCELLED}


def _link_valido(token):
    """Só aceita link ativo de ordem não arquivada e não encerrada (o link expira na entrega)."""
    link = (LinkCliente.objects.select_related("order", "order__vehicle", "order__vehicle__owner")
            .filter(token=token, revogado=False).first())
    if not link or link.order.is_archived or link.order.status in ENCERRADAS:
        return None
    return link


# ------------------------------------------------------------------ oficina
@require_POST
@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def gerar_link(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk, is_archived=False)
    if order.status in ENCERRADAS:
        messages.error(request, "Ordens encerradas não recebem link de acompanhamento.")
    else:
        order.links_cliente.filter(revogado=False).update(revogado=True)   # só um link ativo por ordem
        LinkCliente.objects.create(order=order, criado_por=request.user)
        messages.success(request, "Link do cliente gerado. Copie e envie por WhatsApp ou e-mail.")
    return redirect("order_detail", pk=pk)


@require_POST
@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def revogar_link(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk)
    order.links_cliente.filter(revogado=False).update(revogado=True)
    messages.success(request, "Link do cliente cancelado.")
    return redirect("order_detail", pk=pk)


# ------------------------------------------------------------------ cliente
def acompanhar(request, token):
    link = _link_valido(token)
    if not link:
        return render(request, "assistente/link_invalido.html", status=404)
    order = link.order
    return render(request, "assistente/cliente.html", {
        "order": order,
        "token": token,
        "primeiro_nome": order.vehicle.owner.name.split()[0],
        "historico": order.status_history.all(),
        "pecas": order.used_parts.select_related("part"),
        "valor": order.final_value if order.final_value is not None else order.estimated_value,
        "valor_final": order.final_value is not None,
    })


@require_POST
def perguntar(request, token):
    link = _link_valido(token)
    if not link:
        raise Http404
    try:
        pergunta = json.loads(request.body or "{}").get("pergunta", "")
    except (json.JSONDecodeError, AttributeError):
        pergunta = request.POST.get("pergunta", "")
    pergunta = str(pergunta).strip()
    if not pergunta or len(pergunta) > TAMANHO_MAXIMO:
        return JsonResponse({"erro": f"Escreva uma pergunta de até {TAMANHO_MAXIMO} caracteres."}, status=400)
    recentes = link.perguntas.filter(criado_em__gte=timezone.now() - timedelta(minutes=10)).count()
    if recentes >= LIMITE_PERGUNTAS:
        return JsonResponse({"erro": "Muitas perguntas em pouco tempo. Aguarde alguns minutos."}, status=429)

    resultado = agente.responder(link.order, pergunta)
    PerguntaCliente.objects.create(link=link, pergunta=pergunta, intencao=resultado["intencao"],
                                   confianca=resultado["confianca"], ferramenta=resultado["ferramenta"] or "",
                                   resposta=resultado["resposta"])
    return JsonResponse(resultado, json_dumps_params={"ensure_ascii": False})


# ------------------------------------------------------------------ API (testes no Postman)
@csrf_exempt
@require_POST
def api_classificar(request):
    """Classifica uma frase sem acessar nenhuma ordem. Corpo: {"pergunta": "..."}."""
    try:
        pergunta = str(json.loads(request.body or "{}").get("pergunta", "")).strip()
    except json.JSONDecodeError:
        return JsonResponse({"erro": "JSON inválido."}, status=400)
    if not pergunta or len(pergunta) > TAMANHO_MAXIMO:
        return JsonResponse({"erro": f"Envie 'pergunta' com até {TAMANHO_MAXIMO} caracteres."}, status=400)
    decisao = agente.classificar(pergunta)
    decisao["nome_intencao"] = agente.INTENCOES[decisao["intencao"]]
    decisao["respondera"] = decisao["confianca"] >= decisao["limiar"]
    return JsonResponse(decisao, json_dumps_params={"ensure_ascii": False})


@require_GET
def api_metricas(request):
    """Métricas do último treino (as mesmas dos gráficos)."""
    caminho = Path(agente.PASTA_ML) / "metricas.json"
    return JsonResponse(json.loads(caminho.read_text(encoding="utf-8")), json_dumps_params={"ensure_ascii": False})
