"""Agente do Assistente do Cliente.

Ciclo de cada pergunta:
  1. Percebe:  recebe a pergunta escrita pelo cliente.
  2. Decide:   o modelo de machine learning identifica a intenção e a confiança.
  3. Age:      chama a ferramenta ligada àquela intenção, que lê os registros da ordem.
  4. Responde: monta a resposta só com o que está registrado e informa a fonte.

O agente nunca escreve no banco e nunca cria diagnóstico, preço ou prazo: se o dado não
estiver registrado, ele diz isso e indica o contato da oficina.
"""
import csv
import logging
from functools import lru_cache
from pathlib import Path

import joblib
import sklearn
from django.utils import timezone

from services.models import ServiceOrder

from .ml.modelo import INTENCOES, explicar, modelo_final, normalizar

logger = logging.getLogger(__name__)
PASTA_ML = Path(__file__).resolve().parent / "ml"
LIMIAR_PADRAO = 0.6
Status = ServiceOrder.Status

EXPLICACAO_STATUS = {
    Status.OPEN: "a ordem foi aberta e o veículo está na fila para avaliação.",
    Status.WAITING_DIAGNOSIS: "o veículo aguarda o mecânico examinar e identificar a causa do problema.",
    Status.WAITING_PARTS: "o diagnóstico já foi feito e a oficina espera a chegada de peças para continuar o serviço.",
    Status.IN_MAINTENANCE: "o mecânico está trabalhando no veículo neste momento.",
    Status.READY: "o serviço terminou e o veículo já pode ser retirado.",
    Status.DELIVERED: "o veículo já foi entregue ao cliente e a ordem foi encerrada.",
    Status.CANCELLED: "a ordem foi cancelada e o serviço não será realizado.",
}
NAO_SEI = " Para confirmar, fale com a oficina."


# ------------------------------------------------------------------ modelo
@lru_cache(maxsize=1)
def carregar_modelo():
    """Carrega o modelo treinado. Se o arquivo não abrir (ex.: outra versão do scikit-learn),
    treina de novo a partir do dataset, o que leva poucos segundos."""
    try:
        pacote = joblib.load(PASTA_ML / "modelo_intencao.joblib")
        if pacote.get("versao_sklearn") == sklearn.__version__:
            return pacote["modelo"], pacote["limiar"]
        limiar = pacote["limiar"]
        logger.warning("Modelo salvo com outra versão do scikit-learn; treinando de novo.")
    except Exception:  # noqa: BLE001 - qualquer falha de leitura cai no retreino
        limiar = LIMIAR_PADRAO
        logger.warning("Modelo salvo indisponível; treinando a partir do dataset.")
    with open(PASTA_ML / "dados" / "perguntas_sinteticas.csv", encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    modelo = modelo_final().fit([l["pergunta"] for l in linhas], [l["intencao"] for l in linhas])
    return modelo, limiar


def classificar(pergunta):
    """Devolve a intenção, a confiança e as três intenções mais prováveis."""
    modelo, limiar = carregar_modelo()
    probabilidades = modelo.predict_proba([pergunta])[0]
    ordem = probabilidades.argsort()[::-1]
    intencao = modelo.classes_[ordem[0]]
    return {
        "intencao": intencao,
        "confianca": float(probabilidades[ordem[0]]),
        "limiar": limiar,
        "alternativas": [{"intencao": modelo.classes_[i], "nome": INTENCOES[modelo.classes_[i]],
                          "confianca": round(float(probabilidades[i]), 3)} for i in ordem[:3]],
        "palavras": explicar(modelo, pergunta, intencao),
    }


# ------------------------------------------------------------------ formatação
def reais(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def data(valor):
    if hasattr(valor, "hour"):
        return timezone.localtime(valor).strftime("%d/%m/%Y às %H:%M")
    return valor.strftime("%d/%m/%Y")


def ultima_mudanca(order):
    ultima = order.status_history.order_by("-created_at").first()
    return ultima.created_at if ultima else order.opened_at


# ------------------------------------------------------------------ ferramentas
# Cada ferramenta recebe a ordem (já validada pelo link) e a pergunta, e devolve (resposta, fonte).
def consultar_status(order, pergunta):
    texto = (f"Sua ordem {order.number} está com o status “{order.get_status_display()}” desde "
             f"{data(ultima_mudanca(order))}. Isso significa que {EXPLICACAO_STATUS[order.status]}")
    return texto, "status e linha do tempo da ordem"


def consultar_prazo(order, pergunta):
    if order.status == Status.READY:
        texto = "O serviço terminou e o veículo já está pronto para retirada."
    elif order.status == Status.DELIVERED:
        texto = f"O veículo já foi entregue{' em ' + data(order.completed_at) if order.completed_at else ''}."
    elif order.status == Status.CANCELLED:
        texto = "Esta ordem foi cancelada, então não há previsão de entrega."
    elif order.expected_delivery:
        texto = f"A previsão de entrega registrada é {data(order.expected_delivery)}."
        if order.status == Status.WAITING_PARTS:
            texto += " Como a ordem aguarda peças, a data depende da chegada delas."
    else:
        texto = ("Ainda não há previsão de entrega registrada. A oficina define a data depois do diagnóstico."
                 + NAO_SEI)
    return texto, "previsão de entrega da ordem"


def listar_pecas(order, pergunta):
    usadas = list(order.used_parts.select_related("part"))
    if not usadas:
        texto = "Nenhuma peça foi registrada nesta ordem até agora."
    else:
        itens = "; ".join(f"{u.quantity}× {u.part.name} ({reais(u.total)})" for u in usadas)
        texto = f"Peças registradas na sua ordem: {itens}."
    if order.status == Status.WAITING_PARTS:
        texto += " No momento a oficina aguarda a chegada de peças."
    return texto, "peças registradas na ordem"


def consultar_valores(order, pergunta):
    if order.final_value is not None:
        texto = f"O valor final registrado é {reais(order.final_value)}."
    elif order.estimated_value:
        texto = f"O valor estimado registrado é {reais(order.estimated_value)}. O valor final ainda não foi lançado."
    else:
        texto = "Ainda não há orçamento registrado para esta ordem." + NAO_SEI
    return texto, "valores da ordem"


def consultar_diagnostico(order, pergunta):
    avarias = list(order.damages.all())
    if not avarias:
        return ("O mecânico ainda não registrou avarias nesta ordem, então o diagnóstico está pendente."
                + NAO_SEI), "avarias da ordem"
    partes = []
    for avaria in avarias:
        diagnostico = avaria.diagnosis.strip().rstrip(".") or "diagnóstico ainda pendente"
        partes.append(f"{avaria.title} (gravidade {avaria.get_severity_display().lower()}): {diagnostico}")
    return "Registrado pelo mecânico: " + "; ".join(partes) + ".", "avarias e diagnóstico da ordem"


def explicar_status(order, pergunta):
    texto = normalizar(pergunta).replace(" pra ", " para ")
    for valor, nome in Status.choices:
        if normalizar(nome) in texto:
            return f"“{nome}” quer dizer que {EXPLICACAO_STATUS[valor]}", "tabela de status do Box Box"
    return (f"O status atual da sua ordem é “{order.get_status_display()}”: {EXPLICACAO_STATUS[order.status]}",
            "status da ordem")


def consultar_historico(order, pergunta):
    eventos = [f"{data(order.opened_at)}: ordem aberta"]
    eventos += [f"{data(h.created_at)}: {Status(h.new_status).label}" for h in order.status_history.all()
                if h.new_status in Status.values]
    return "Histórico da sua ordem — " + "; ".join(eventos) + ".", "linha do tempo da ordem"


def cumprimentar(order, pergunta):
    if any(p in pergunta.lower() for p in ("obrigad", "valeu", "obg", "agrade")):
        return "Por nada! Se surgir outra dúvida sobre a sua ordem, é só perguntar.", "—"
    primeiro_nome = order.vehicle.owner.name.split()[0]
    return (f"Olá, {primeiro_nome}! Posso responder sobre status, previsão de entrega, peças, valores, "
            "diagnóstico e histórico da sua ordem.", "—")


def fora_do_escopo(order, pergunta):
    return ("Essa pergunta foge do que eu posso responder com os registros da sua ordem. "
            "Para esse assunto, fale diretamente com a oficina."), "—"


FERRAMENTAS = {
    "status": consultar_status,
    "prazo": consultar_prazo,
    "pecas": listar_pecas,
    "valor": consultar_valores,
    "diagnostico": consultar_diagnostico,
    "significado_status": explicar_status,
    "historico": consultar_historico,
    "saudacao": cumprimentar,
    "fora_escopo": fora_do_escopo,
}


def responder(order, pergunta):
    """Executa o ciclo completo do agente para uma pergunta."""
    decisao = classificar(pergunta)
    if decisao["confianca"] < decisao["limiar"]:
        ferramenta = None
        resposta = ("Não entendi bem a sua pergunta. Posso responder sobre status, previsão de entrega, peças, "
                    "valores, diagnóstico e histórico da sua ordem. Tente reformular ou fale com a oficina.")
        fonte = "—"
    else:
        funcao = FERRAMENTAS[decisao["intencao"]]
        ferramenta = funcao.__name__
        resposta, fonte = funcao(order, pergunta)
    return {
        **decisao,
        "nome_intencao": INTENCOES[decisao["intencao"]],
        "respondeu": ferramenta is not None,
        "ferramenta": ferramenta,
        "resposta": resposta,
        "fonte": fonte,
    }
