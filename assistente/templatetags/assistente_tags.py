from django import template

from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, user_has_role

from services.models import ServiceOrder

from ..ml.modelo import INTENCOES
from ..models import PerguntaCliente

register = template.Library()


@register.inclusion_tag("assistente/painel_ordem.html", takes_context=True)
def painel_assistente(context, order):
    """Painel no detalhe da ordem: link do cliente e últimas perguntas respondidas pela IA."""
    request = context["request"]
    link = order.links_cliente.filter(revogado=False).first()
    return {
        "order": order,
        "link": link,
        "url": request.build_absolute_uri(f"/acompanhar/{link.token}/") if link else "",
        "pode_gerenciar": user_has_role(request.user, ROLE_ADMIN) or user_has_role(request.user, ROLE_ATTENDANT),
        "encerrada": order.status in {"DELIVERED", "CANCELLED"},
        "perguntas": PerguntaCliente.objects.filter(link__order=order).order_by("-criado_em")[:6],
        "csrf_token": context.get("csrf_token"),
    }


@register.filter
def rotulo_status(valor):
    """'WAITING_PARTS' -> 'Aguardando peças'."""
    return dict(ServiceOrder.Status.choices).get(valor, valor)


@register.filter
def nome_intencao(valor):
    """'prazo' -> 'Previsão de entrega'."""
    return INTENCOES.get(valor, valor)
