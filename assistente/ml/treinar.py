"""Treina e avalia o modelo de intenção do Assistente do Cliente.

Etapas:
  1. Lê o dataset sintético e o conjunto de teste escrito à mão.
  2. Compara cinco abordagens: regra fixa, árvore de decisão, random forest,
     regressão logística e rede neural (MLP).
  3. Escolhe o limiar de confiança abaixo do qual o assistente não responde.
  4. Salva o modelo final, as métricas e os gráficos da apresentação.

Uso:  python -m assistente.ml.treinar
"""
import json
import time
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split  # noqa: E402
from sklearn.neural_network import MLPClassifier  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from .modelo import INTENCOES, RegraPalavrasChave, modelo_final, vetorizador  # noqa: E402

PASTA = Path(__file__).resolve().parent
DADOS, GRAFICOS = PASTA / "dados", PASTA / "graficos"
SEED = 42
ORDEM = list(INTENCOES)                      # ordem fixa das intenções nos gráficos
NOMES = [INTENCOES[i] for i in ORDEM]

# ---------- estilo dos gráficos (fundo claro, para slides) ----------
COR_DESTAQUE, COR_NEUTRA = "#2a78d6", "#b9bcc3"
COR_SECUNDARIA = "#eb6834"
TEXTO, TEXTO_2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "savefig.facecolor": FUNDO,
    "font.family": "DejaVu Sans", "font.size": 11, "text.color": TEXTO,
    "axes.labelcolor": TEXTO_2, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "axes.edgecolor": GRADE, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlelocation": "left",
})


def abordagens():
    """As cinco abordagens comparadas. Todas recebem o mesmo texto e a mesma divisão de dados."""
    return {
        "Regra fixa (palavras-chave)": RegraPalavrasChave(),
        "Árvore de decisão": Pipeline([("tfidf", vetorizador()),
                                       ("classificador", DecisionTreeClassifier(random_state=SEED))]),
        "Random Forest": Pipeline([("tfidf", vetorizador()),
                                   ("classificador", RandomForestClassifier(n_estimators=300, random_state=SEED,
                                                                            n_jobs=-1))]),
        "Regressão logística": modelo_final(),
        "Rede neural (MLP)": Pipeline([("tfidf", vetorizador()),
                                       ("classificador", MLPClassifier(hidden_layer_sizes=(128,), max_iter=400,
                                                                       early_stopping=True, random_state=SEED))]),
    }


def salvar(fig, nome):
    fig.savefig(GRAFICOS / nome, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    dados = pd.read_csv(DADOS / "perguntas_sinteticas.csv")
    manual = pd.read_csv(DADOS / "teste_manual.csv")

    # ---------- 1. divisão dos dados ----------
    # 80% para treinar, 20% para validar. O teste manual nunca é usado no treino.
    x_treino, x_valid, y_treino, y_valid = train_test_split(
        dados.pergunta, dados.intencao, test_size=0.2, stratify=dados.intencao, random_state=SEED)
    print(f"Dataset sintético: {len(dados)} perguntas | treino {len(x_treino)} | validação {len(x_valid)}")
    print(f"Teste manual (frases escritas à mão, fora do gerador): {len(manual)} perguntas\n")

    # ---------- 2. comparação das abordagens ----------
    resultados = []
    for nome, modelo in abordagens().items():
        inicio = time.perf_counter()
        modelo.fit(x_treino, y_treino)
        tempo_treino = time.perf_counter() - inicio
        inicio = time.perf_counter()
        previsto_manual = modelo.predict(manual.pergunta)
        tempo_pred = (time.perf_counter() - inicio) / len(manual) * 1000
        previsto_valid = modelo.predict(x_valid)
        resultados.append({
            "modelo": nome,
            "f1_validacao": f1_score(y_valid, previsto_valid, average="macro"),
            "acuracia_teste_manual": accuracy_score(manual.intencao, previsto_manual),
            "f1_teste_manual": f1_score(manual.intencao, previsto_manual, average="macro"),
            "tempo_treino_s": tempo_treino,
            "tempo_por_pergunta_ms": tempo_pred,
        })
        r = resultados[-1]
        print(f"{nome:30s} F1 validação {r['f1_validacao']:.3f} | F1 teste manual {r['f1_teste_manual']:.3f} | "
              f"treino {r['tempo_treino_s']:.2f}s | {r['tempo_por_pergunta_ms']:.2f} ms/pergunta")
    tabela = pd.DataFrame(resultados)

    # ---------- 3. validação cruzada do modelo escolhido ----------
    escolhido = "Regressão logística"
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    prob_oof = cross_val_predict(modelo_final(), dados.pergunta, dados.intencao, cv=folds, method="predict_proba")
    classes_ordenadas = sorted(dados.intencao.unique())
    pred_oof = np.array(classes_ordenadas)[prob_oof.argmax(1)]
    f1_folds = [f1_score(dados.intencao.iloc[teste], pred_oof[teste], average="macro")
                for _, teste in folds.split(dados.pergunta, dados.intencao)]
    print(f"\nValidação cruzada (5 partes) da {escolhido}: F1 {np.mean(f1_folds):.3f} ± {np.std(f1_folds):.3f}")

    # ---------- 4. modelo final, treinado com todo o dataset sintético ----------
    final = modelo_final().fit(dados.pergunta, dados.intencao)
    prob_manual = final.predict_proba(manual.pergunta)
    pred_manual = final.classes_[prob_manual.argmax(1)]
    conf_manual = prob_manual.max(1)
    acertos = pred_manual == manual.intencao.values

    # ---------- 5. limiar de confiança ----------
    # Abaixo do limiar o assistente diz que não entendeu, em vez de arriscar uma resposta errada.
    limiares = np.round(np.arange(0.0, 0.91, 0.05), 2)
    curva = []
    for limiar in limiares:
        respondidas = conf_manual >= limiar
        curva.append({
            "limiar": float(limiar),
            "cobertura": float(respondidas.mean()),
            "acuracia_respondidas": float(acertos[respondidas].mean()) if respondidas.any() else 1.0,
        })
    # Regra: o maior limiar que ainda responde pelo menos 90% das perguntas
    limiar_escolhido = max(c["limiar"] for c in curva if c["cobertura"] >= 0.90)
    escolha = next(c for c in curva if c["limiar"] == limiar_escolhido)
    print(f"Limiar de confiança: {limiar_escolhido:.2f} -> responde {escolha['cobertura']:.0%} das perguntas "
          f"com {escolha['acuracia_respondidas']:.0%} de acerto")

    import sklearn
    joblib.dump({"modelo": final, "limiar": limiar_escolhido, "versao_sklearn": sklearn.__version__},
                PASTA / "modelo_intencao.joblib")

    erros = manual[~acertos].assign(previsto=pred_manual[~acertos], confianca=conf_manual[~acertos].round(2))
    print("\nErros no teste manual:")
    print(erros.to_string(index=False) if len(erros) else "nenhum")

    metricas = {
        "dataset": {"sintetico": len(dados), "treino": len(x_treino), "validacao": len(x_valid),
                    "teste_manual": len(manual), "por_intencao": dados.intencao.value_counts().to_dict()},
        "comparacao": tabela.round(4).to_dict(orient="records"),
        "modelo_escolhido": escolhido,
        "validacao_cruzada_f1": {"media": round(float(np.mean(f1_folds)), 4),
                                 "desvio": round(float(np.std(f1_folds)), 4)},
        "final_teste_manual": {"acuracia": round(float(acertos.mean()), 4),
                               "f1_macro": round(float(f1_score(manual.intencao, pred_manual, average="macro")), 4)},
        "limiar_confianca": limiar_escolhido,
        "curva_limiar": curva,
        "erros_teste_manual": erros.to_dict(orient="records"),
    }

    # ---------- 6. gráficos ----------
    grafico_dataset(dados)
    grafico_comparacao(tabela, escolhido)
    grafico_matriz(manual.intencao, pred_manual)
    grafico_palavras(final)
    grafico_limiar(curva, limiar_escolhido)
    metricas["curva_aprendizado"] = grafico_aprendizado(dados, manual)

    (PASTA / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nModelo, métricas e gráficos salvos em {PASTA}")


# ---------------------------------------------------------------- gráficos
def grafico_dataset(dados):
    contagem = dados.intencao.value_counts().reindex(ORDEM)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    barras = ax.barh(NOMES[::-1], contagem.values[::-1], color=COR_DESTAQUE, height=0.62)
    ax.bar_label(barras, padding=4, color=TEXTO, fontsize=10)
    ax.set_title(f"Dataset de treino: {len(dados):,} perguntas sintéticas".replace(",", "."))
    ax.set_xlabel("Perguntas por intenção")
    ax.xaxis.grid(True, color=GRADE); ax.set_axisbelow(True); ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, -0.04, "Geradas a partir de modelos de frase com variações reais de digitação "
             "(sem acento, abreviações, letras faltando).", color=TEXTO_2, fontsize=9)
    salvar(fig, "1_dataset.png")


def grafico_comparacao(tabela, escolhido):
    tabela = tabela.sort_values("f1_teste_manual")
    cores = [COR_DESTAQUE if m == escolhido else COR_NEUTRA for m in tabela.modelo]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True, gridspec_kw={"wspace": 0.08})
    b1 = ax1.barh(tabela.modelo, tabela.f1_teste_manual * 100, color=cores, height=0.62)
    ax1.bar_label(b1, labels=[f"{v:.0f}%" for v in tabela.f1_teste_manual * 100], padding=4, fontsize=10)
    ax1.set_xlim(0, 110); ax1.set_title("Qualidade: F1 no teste escrito à mão")
    ax1.set_xlabel("F1 macro (%) — maior é melhor")
    b2 = ax2.barh(tabela.modelo, tabela.tempo_treino_s, color=cores, height=0.62)
    ax2.bar_label(b2, labels=[f"{v:.2f} s" for v in tabela.tempo_treino_s], padding=4, fontsize=10)
    ax2.set_xlim(0, tabela.tempo_treino_s.max() * 1.3); ax2.set_title("Custo: tempo de treino")
    ax2.set_xlabel("Segundos — menor é melhor")
    for ax in (ax1, ax2):
        ax.xaxis.grid(True, color=GRADE); ax.set_axisbelow(True)
        ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    fig.text(0.01, -0.05, f"Em azul, o modelo escolhido ({escolhido}): melhor equilíbrio entre acerto e "
             "velocidade, e devolve uma confiança usada pelo assistente.", color=TEXTO_2, fontsize=9)
    salvar(fig, "2_comparacao_modelos.png")


def grafico_matriz(real, previsto):
    matriz = confusion_matrix(real, previsto, labels=ORDEM)
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    ax.imshow(matriz, cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
        "azul", ["#f4f8fd", "#86b6ef", "#1c5cab"]), vmin=0, vmax=matriz.max())
    for i in range(len(ORDEM)):
        for j in range(len(ORDEM)):
            if matriz[i, j]:
                ax.text(j, i, matriz[i, j], ha="center", va="center", fontsize=11,
                        color="white" if matriz[i, j] > matriz.max() * 0.55 else TEXTO)
    ax.set_xticks(range(len(ORDEM)), NOMES, rotation=40, ha="right")
    ax.set_yticks(range(len(ORDEM)), NOMES)
    ax.set_xlabel("Intenção prevista pelo modelo"); ax.set_ylabel("Intenção real")
    ax.set_title(f"Matriz de confusão — teste escrito à mão ({len(real)} perguntas)")
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    fig.text(0.01, -0.12, "A diagonal são os acertos; fora dela, as confusões do modelo.", color=TEXTO_2, fontsize=9)
    salvar(fig, "3_matriz_confusao.png")


def grafico_palavras(final):
    """Palavras com maior peso positivo em cada intenção (parte de palavras do TF-IDF)."""
    palavras_vec = final.named_steps["tfidf"].transformer_list[0][1]
    n_palavras = len(palavras_vec.vocabulary_)
    vocab = np.array(palavras_vec.get_feature_names_out())
    coef = final.named_steps["classificador"].coef_[:, :n_palavras]
    classes = list(final.classes_)
    fig, eixos = plt.subplots(3, 3, figsize=(12, 8.4), gridspec_kw={"hspace": 0.55, "wspace": 0.55})
    for ax, intencao in zip(eixos.flat, ORDEM):
        pesos = coef[classes.index(intencao)]
        top = np.argsort(pesos)[-5:]
        ax.barh(vocab[top], pesos[top], color=COR_DESTAQUE, height=0.6)
        ax.set_title(INTENCOES[intencao], fontsize=11)
        ax.tick_params(axis="y", length=0, labelsize=10); ax.tick_params(axis="x", labelsize=8)
        ax.spines["left"].set_visible(False); ax.xaxis.grid(True, color=GRADE); ax.set_axisbelow(True)
    fig.suptitle("O que o modelo aprendeu: palavras que mais puxam para cada intenção", x=0.01, ha="left",
                 fontweight="bold", fontsize=13)
    fig.text(0.01, 0.02, "Pesos da regressão logística (quanto maior, mais a palavra indica aquela intenção).",
             color=TEXTO_2, fontsize=9)
    salvar(fig, "4_palavras_importantes.png")


def grafico_limiar(curva, limiar):
    df = pd.DataFrame(curva)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(df.limiar, df.acuracia_respondidas * 100, color=COR_DESTAQUE, lw=2, marker="o", ms=5,
            label="Acerto nas perguntas respondidas")
    ax.plot(df.limiar, df.cobertura * 100, color=COR_SECUNDARIA, lw=2, marker="o", ms=5,
            label="Perguntas respondidas (cobertura)")
    ax.axvline(limiar, color=TEXTO_2, lw=1, ls="--")
    ax.annotate(f"limiar escolhido: {limiar:.2f}", (limiar, 62), xytext=(8, 0), textcoords="offset points",
                color=TEXTO, fontsize=10)
    ax.set_ylim(55, 102); ax.set_xlabel("Confiança mínima para responder"); ax.set_ylabel("%")
    ax.yaxis.grid(True, color=GRADE); ax.set_axisbelow(True)
    ax.set_title("Quando o assistente prefere dizer “não entendi”")
    ax.legend(frameon=False, loc="lower left")
    fig.text(0.01, -0.04, "Abaixo do limiar, o assistente pede para reformular ou indica o contato da oficina.",
             color=TEXTO_2, fontsize=9)
    salvar(fig, "5_limiar_confianca.png")


def grafico_aprendizado(dados, manual):
    """Treina com cada vez mais exemplos e mede no teste manual: mostra o modelo aprendendo."""
    tamanhos = [20, 45, 90, 180, 360, 720, 1440, len(dados)]
    pontos = []
    for n in tamanhos:
        notas = []
        for rep in range(3):
            amostra = dados.groupby("intencao").sample(n=max(2, n // len(ORDEM)), random_state=SEED + rep) \
                if n < len(dados) else dados
            modelo = clone(modelo_final()).fit(amostra.pergunta, amostra.intencao)
            notas.append(f1_score(manual.intencao, modelo.predict(manual.pergunta), average="macro"))
            if n == len(dados):
                break
        pontos.append({"exemplos": len(amostra), "f1": float(np.mean(notas))})
    df = pd.DataFrame(pontos)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(df.exemplos, df.f1 * 100, color=COR_DESTAQUE, lw=2, marker="o", ms=6)
    for _, linha in df.iloc[[0, 3, -1]].iterrows():
        ax.annotate(f"{linha.f1 * 100:.0f}%", (linha.exemplos, linha.f1 * 100), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=10)
    ax.set_xscale("log"); ax.set_xticks(df.exemplos, [f"{x}" for x in df.exemplos])
    ax.minorticks_off(); ax.set_ylim(0, 105)
    ax.set_xlabel("Perguntas usadas no treino (escala logarítmica)"); ax.set_ylabel("F1 no teste manual (%)")
    ax.yaxis.grid(True, color=GRADE); ax.set_axisbelow(True)
    ax.set_title("Curva de aprendizado: mais exemplos, mais acerto")
    salvar(fig, "6_curva_aprendizado.png")
    return pontos


if __name__ == "__main__":
    main()
