# Assistente do cliente (IA)

Agente que responde às dúvidas do cliente sobre a própria ordem de serviço, usando um
modelo de machine learning treinado pelo grupo para entender a pergunta.

## Como funciona

1. **Link seguro.** No detalhe da ordem, o atendente clica em *Gerar link do cliente*.
   O link dá acesso a uma única ordem, pode ser cancelado e expira na entrega.
2. **Percepção.** O cliente escreve a pergunta na página `/acompanhar/<token>/`.
3. **Decisão (machine learning).** O modelo (TF-IDF + Regressão Logística) classifica a
   pergunta em uma de 9 intenções e devolve a confiança. Abaixo de 55% o agente não arrisca:
   pede para reformular.
4. **Ação.** Cada intenção aciona uma ferramenta que só **lê** os registros da ordem
   (`consultar_status`, `consultar_prazo`, `listar_pecas`, `consultar_valores`,
   `consultar_diagnostico`, `explicar_status`, `consultar_historico`).
5. **Resposta.** O texto sai só do que está registrado, com a fonte. Sem prazo, preço ou
   diagnóstico registrado, o agente diz que não tem a informação.
6. **Registro.** Cada pergunta, intenção, confiança e resposta fica salva e aparece no
   detalhe da ordem para a oficina.

## Rodar a demonstração (Windows)

```bat
run-boxbox.bat
```

Em outro terminal, na pasta do projeto:

```bat
.venv\Scripts\python.exe manage.py demo_assistente
```

O comando cria a ordem de demonstração (Fiat Argo da cliente Ana Souza) e imprime o link
do cliente. Login da oficina: `marina` / `boxbox123` (atendente) ou `admin` / `boxbox123`.

## Treinar de novo e refazer os gráficos

```bat
.venv\Scripts\python.exe -m pip install -r assistente\ml\requirements-treino.txt
.venv\Scripts\python.exe -m assistente.ml.gerar_dataset
.venv\Scripts\python.exe -m assistente.ml.treinar
```

Saídas em `assistente/ml/`: `modelo_intencao.joblib`, `metricas.json` e `graficos/*.png`.

## API (Postman)

| Método | Rota | Corpo | Retorno |
|---|---|---|---|
| POST | `/assistente/api/classificar/` | `{"pergunta": "quando fica pronto?"}` | intenção, confiança, alternativas, palavras decisivas |
| GET | `/assistente/api/metricas/` | — | métricas do último treino |
| POST | `/acompanhar/<token>/perguntar/` | `{"pergunta": "..."}` | resposta completa do agente (pede o token CSRF da página) |

## Dados e resultados do treino

- **Treino:** 2.340 perguntas sintéticas (260 por intenção), geradas com variações reais de
  digitação: sem acento, abreviações ("vc", "pq", "tá"), letras faltando.
- **Teste:** 90 perguntas escritas à mão, fora do gerador, que o modelo nunca viu.
- **Comparação (F1 no teste escrito à mão):** regra fixa 52%, árvore de decisão 65%,
  Random Forest 83%, rede neural (MLP) 91%, regressão logística 91%.
- **Escolha:** regressão logística. Empata com a rede neural no acerto, treina cerca de
  6 vezes mais rápido e devolve uma confiança usada pelo agente.
- **Limitação conhecida:** perguntas fora do escopo que usam palavras de dentro dele
  ("quanto custa pra alinhar?") podem ser confundidas com *Valor*.
