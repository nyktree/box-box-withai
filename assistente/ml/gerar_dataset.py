"""Gera o dataset sintético de perguntas de clientes usado no treino do assistente.

Cada linha do CSV tem uma pergunta e a intenção dela. O treino usa essas
perguntas para ensinar o modelo a reconhecer o que o cliente quer saber.

Uso:  python -m assistente.ml.gerar_dataset
"""
import csv
import random
import unicodedata
from pathlib import Path

SEED = 42
POR_INTENCAO = 260
PASTA = Path(__file__).resolve().parent / "dados"

# Peças de vocabulário reutilizadas pelos modelos de frase
# Sempre usadas depois de "o", "do" ou "no" nos modelos de frase
CARRO = ["carro", "meu carro", "veículo", "meu veículo", "corolla", "meu gol", "onix", "hb20", "carrinho",
         "carro da minha esposa", "carro do meu pai", "meu fiat"]
ABERTURA = ["", "", "", "oi, ", "olá, ", "bom dia, ", "boa tarde, ", "por favor, ", "ei, ", "opa, ", "então, ",
            "moço, ", "com licença, ", "e aí, "]
FECHO = ["", "", "", "?", "?", "??", " por favor", " obrigado", " pfv", " aí", " me fala", " rapidinho"]

# Modelos de frase por intenção. {c} = carro
MODELOS = {
    "saudacao": [
        "oi", "olá", "bom dia", "boa tarde", "boa noite", "tudo bem", "obrigado", "valeu", "muito obrigado",
        "obrigada pela ajuda", "beleza, valeu", "show, obrigado", "ok entendi", "entendi, obrigado", "tchau",
        "até mais", "perfeito", "certo, obrigado", "olá, tudo bem?", "oi, alguém aí?", "ok", "blz",
        "agradeço", "valeu pela informação", "tá bom então", "entendido",
    ],
    "status": [
        "qual é o status do {c}", "como está o {c}", "como tá o {c}", "em que pé está o serviço",
        "qual a situação do {c}", "já começaram a mexer no {c}", "o {c} ainda está na fila",
        "o serviço do {c} já começou", "alguma novidade sobre o {c}", "como anda o conserto",
        "o que está acontecendo com o {c} agora", "em que etapa está o {c}", "já está pronto",
        "o {c} já ficou pronto", "posso saber o andamento", "qual o andamento do serviço",
        "o mecânico já está trabalhando no {c}", "tem novidade da minha ordem", "status da ordem",
        "o {c} está parado aí", "já terminaram o {c}", "está em manutenção ainda",
        "quero saber como está o conserto do {c}", "atualização do {c}", "tem alguma atualização",
        "qual é o status", "qual o status", "status", "como está", "como tá", "como ficou o {c}",
        "e o {c}, como está", "situação atual",
    ],
    "prazo": [
        "quando fica pronto", "qual a previsão de entrega", "quando posso buscar o {c}",
        "que dia o {c} fica pronto", "tem previsão para terminar", "vai demorar muito",
        "quanto tempo ainda falta", "até quando fica pronto", "consigo pegar o {c} amanhã",
        "quando vocês entregam o {c}", "qual a data de entrega", "fica pronto essa semana",
        "dá pra buscar hoje", "em quantos dias termina", "quando vou ter o {c} de volta",
        "tem prazo pra ficar pronto", "o {c} sai até sexta", "qual o prazo do conserto",
        "falta muito pra terminar", "que horas posso passar pra pegar", "previsão de quando fica pronto",
        "demora quantos dias", "quando libera o {c}", "data prevista de entrega",
    ],
    "pecas": [
        "o que foi trocado", "quais peças foram trocadas", "trocaram alguma peça",
        "que peça vocês colocaram no {c}", "quais peças vão usar", "precisou trocar alguma coisa",
        "o que vocês substituíram no {c}", "lista das peças", "quais peças entraram no serviço",
        "a peça já chegou", "qual peça está faltando", "que peça vocês estão esperando",
        "trocaram a correia", "colocaram peça original", "quantas peças foram trocadas",
        "o que foi substituído", "teve troca de peça", "quais componentes foram trocados",
        "que material vai ser usado", "qual peça foi pedida", "chegou a peça do {c}",
    ],
    "valor": [
        "quanto vai custar", "qual o valor do conserto", "quanto vou pagar", "qual o orçamento",
        "quanto deu o serviço", "qual o preço", "quanto ficou", "valor total do {c}",
        "quanto custa o conserto do {c}", "já tem o valor final", "qual o valor estimado",
        "vai ficar caro", "quanto está o orçamento do {c}", "me passa o valor", "quanto vai sair",
        "qual o total a pagar", "o preço mudou", "quanto ficou a conta", "quanto é a mão de obra mais peças",
        "qual o custo do serviço", "valor do orçamento", "quanto eu devo",
    ],
    "diagnostico": [
        "o que o {c} tem", "qual o problema do {c}", "o que deu no {c}", "descobriram o defeito",
        "qual foi o diagnóstico", "o que está errado com o {c}", "acharam o problema",
        "por que o {c} esquentava", "qual a causa do barulho", "o que causou o defeito",
        "qual o defeito encontrado", "o mecânico descobriu o que é", "o que foi encontrado no {c}",
        "o problema era grave", "é coisa séria", "qual a avaria", "o que vocês encontraram",
        "por que o {c} estava falhando", "qual a origem do problema", "explica o defeito do {c}",
        "o que quebrou", "é o motor", "o problema é na suspensão",
    ],
    "significado_status": [
        "o que significa aguardando peças", "o que quer dizer em manutenção",
        "o que é aguardando diagnóstico", "o que significa pronta para entrega",
        "não entendi o status", "o que significa esse status", "o que quer dizer aberta",
        "aguardando peças quer dizer o quê", "explica o que é em manutenção",
        "o que significa ordem aberta", "status pronta pra entrega significa que já posso buscar",
        "o que é esse aguardando", "não entendi o que significa aguardando diagnóstico",
        "esse status quer dizer o que", "o que significa entregue", "o que significa cancelada",
        "me explica o status", "como assim aguardando peças", "o que é diagnóstico pendente",
    ],
    "historico": [
        "quando o {c} deu entrada", "que dia eu deixei o {c}", "o que já foi feito até agora",
        "mostra o histórico da ordem", "quais etapas já passaram", "quando mudou o status",
        "desde quando está aguardando peças", "quando começou o conserto", "quando abriram a ordem",
        "linha do tempo do serviço", "o que aconteceu desde que deixei o {c}", "histórico do atendimento",
        "quando foi feito o diagnóstico", "há quanto tempo o {c} está aí", "quando entrou em manutenção",
        "quais foram as atualizações", "me mostra tudo que aconteceu", "que dia foi aberta a ordem",
        "já passou por quais etapas",
    ],
    "fora_escopo": [
        "vocês fazem alinhamento", "qual o horário de funcionamento", "aceitam cartão",
        "posso parcelar", "tem desconto", "quero agendar uma revisão", "onde fica a oficina",
        "vocês abrem sábado", "tem estacionamento", "qual o telefone da oficina",
        "quero falar com o gerente", "vocês vendem pneu", "quanto custa uma troca de óleo",
        "fazem funilaria", "vocês trabalham com carro elétrico", "tem lava jato aí",
        "me recomenda um seguro", "qual a melhor gasolina", "quem ganhou o jogo ontem",
        "me conta uma piada", "qual o status do carro do meu vizinho", "quero cancelar o serviço",
        "posso mudar o mecânico", "vocês emitem nota fiscal", "quero reclamar do atendimento",
        "tem garantia o serviço", "vocês buscam o carro em casa", "dá pra trocar o óleo também",
        "tem vaga de emprego", "aceita pix",
    ],
}

# Erros e abreviações comuns em mensagens de celular
ABREVIACOES = [("você", "vc"), ("vocês", "vcs"), ("que ", "q "), ("está", "tá"), ("para", "pra"),
               ("porque", "pq"), ("também", "tb"), ("quando", "qnd"), ("por favor", "pfv"), ("obrigado", "obg")]


def sem_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def bagunca(texto, rnd):
    """Simula o jeito real de digitar: sem acento, abreviação, letra trocada, caixa alta."""
    if rnd.random() < 0.35:
        texto = sem_acentos(texto)
    for longo, curto in ABREVIACOES:
        if longo in texto and rnd.random() < 0.4:
            texto = texto.replace(longo, curto)
    if rnd.random() < 0.15 and len(texto) > 6:
        i = rnd.randrange(1, len(texto) - 1)
        texto = texto[:i] + texto[i + 1:]                     # letra esquecida
    if rnd.random() < 0.08:
        texto = texto.upper()
    elif rnd.random() < 0.3:
        texto = texto.capitalize()
    return texto


def gerar(rnd):
    linhas = []
    for intencao, modelos in MODELOS.items():
        vistas = set()
        tentativas = 0
        while len(vistas) < POR_INTENCAO and tentativas < POR_INTENCAO * 40:
            tentativas += 1
            frase = rnd.choice(modelos).format(c=rnd.choice(CARRO))
            if intencao != "saudacao":
                frase = rnd.choice(ABERTURA) + frase + rnd.choice(FECHO)
            frase = bagunca(frase, rnd).strip()
            if frase.lower() not in vistas:
                vistas.add(frase.lower())
                linhas.append((frase, intencao))
    rnd.shuffle(linhas)
    return linhas


def main():
    rnd = random.Random(SEED)
    PASTA.mkdir(parents=True, exist_ok=True)
    linhas = gerar(rnd)
    with open(PASTA / "perguntas_sinteticas.csv", "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["pergunta", "intencao"])
        escritor.writerows(linhas)
    print(f"{len(linhas)} perguntas salvas em {PASTA / 'perguntas_sinteticas.csv'}")


if __name__ == "__main__":
    main()
