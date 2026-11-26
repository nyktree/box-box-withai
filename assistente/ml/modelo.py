"""Peças do modelo de intenção compartilhadas pelo treino e pelo Box Box."""
import re
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

# Intenções que o assistente reconhece, com o nome mostrado nas telas e nos gráficos
INTENCOES = {
    "status": "Status da ordem",
    "prazo": "Previsão de entrega",
    "pecas": "Peças",
    "valor": "Valor",
    "diagnostico": "Diagnóstico",
    "significado_status": "Significado do status",
    "historico": "Histórico",
    "saudacao": "Saudação",
    "fora_escopo": "Fora do escopo",
}


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação: 'Previsão?' e 'previsao' viram a mesma coisa."""
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", texto).strip()


def vetorizador():
    """Transforma a frase em números: palavras (e pares de palavras) + pedaços de 2 a 5 letras.

    Os pedaços de letras deixam o modelo tolerante a erros de digitação ('previsao', 'prevsao').
    """
    return FeatureUnion([
        ("palavras", TfidfVectorizer(preprocessor=normalizar, ngram_range=(1, 2), sublinear_tf=True)),
        ("letras", TfidfVectorizer(preprocessor=normalizar, analyzer="char_wb", ngram_range=(2, 5),
                                   sublinear_tf=True, min_df=2)),
    ])


def modelo_final():
    """Modelo escolhido para o Box Box: TF-IDF + Regressão Logística."""
    return Pipeline([
        ("tfidf", vetorizador()),
        ("classificador", LogisticRegression(C=8.0, max_iter=3000)),
    ])


class RegraPalavrasChave:
    """Linha de base sem aprendizado: conta palavras-chave fixas de cada intenção.

    Segue a mesma interface do scikit-learn (fit/predict) para ser comparada com os modelos.
    """

    PALAVRAS = {
        "status": ["status", "situacao", "andamento", "novidade", "pronto", "etapa", "atualizacao"],
        "prazo": ["quando", "previsao", "prazo", "data", "dias", "demora", "buscar", "pegar"],
        "pecas": ["peca", "pecas", "trocad", "troca", "substitu", "componente"],
        "valor": ["valor", "custa", "custo", "preco", "orcamento", "pagar", "quanto"],
        "diagnostico": ["problema", "defeito", "diagnostico", "causa", "errado", "grave"],
        "significado_status": ["significa", "quer dizer", "entendi"],
        "historico": ["historico", "entrada", "etapas", "deixei", "aconteceu", "desde"],
        "saudacao": ["oi", "ola", "obrigad", "valeu", "bom dia", "boa tarde", "boa noite", "tchau"],
    }

    def fit(self, frases, intencoes):
        return self

    def predict(self, frases):
        saida = []
        for frase in frases:
            texto = " " + normalizar(frase) + " "
            pontos = {intencao: sum(palavra in texto for palavra in lista)
                      for intencao, lista in self.PALAVRAS.items()}
            melhor = max(pontos, key=pontos.get)
            saida.append(melhor if pontos[melhor] > 0 else "fora_escopo")
        return saida


def explicar(modelo, frase, intencao, limite=3):
    """Mostra quais palavras mais pesaram na decisão.

    Tira uma palavra por vez e mede quanto a confiança na intenção escolhida cai.
    Quanto maior a queda, mais aquela palavra foi decisiva.
    """
    palavras = normalizar(frase).split()
    if not palavras:
        return []
    classes = list(modelo.classes_)
    indice = classes.index(intencao)
    base = modelo.predict_proba([" ".join(palavras)])[0][indice]
    variantes = [" ".join(palavras[:i] + palavras[i + 1:]) for i in range(len(palavras))]
    quedas = base - modelo.predict_proba(variantes)[:, indice]
    ranking = sorted(zip(palavras, quedas), key=lambda par: par[1], reverse=True)
    return [{"palavra": p, "peso": round(float(q), 3)} for p, q in ranking[:limite] if q > 0.01]
