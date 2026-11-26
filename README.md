# Box Box com IA

Plataforma web acadêmica para gestão de oficinas mecânicas, com clientes, veículos,
ordens de serviço, avarias, diagnósticos, peças, histórico e relatórios. Esta versão
também inclui um **assistente de IA para o cliente**, que entende perguntas em linguagem
natural e responde com base nos dados registrados na ordem de serviço.

## Inteligência artificial

A IA é usada no acompanhamento da ordem pelo cliente. O fluxo funciona assim:

1. O atendente gera, no detalhe da ordem, um link seguro e exclusivo para o cliente.
2. O cliente abre o link e pergunta, por exemplo, “quando fica pronto?” ou “qual o valor?”.
3. Um modelo local de machine learning identifica a intenção da pergunta.
4. O assistente consulta somente os dados daquela ordem e monta a resposta.
5. A oficina pode consultar o histórico de perguntas, respostas, intenções e confiança.

O classificador combina **TF-IDF e regressão logística** e reconhece nove intenções:
status, prazo, peças, valor, diagnóstico, significado do status, histórico, saudação e
perguntas fora do escopo. Se a confiança for menor que 55%, o assistente pede que a
pergunta seja reformulada.

O projeto **não usa ChatGPT nem outra API de IA generativa**. O modelo roda localmente,
não inventa prazo, preço ou diagnóstico e não altera registros: ele apenas identifica o
assunto e consulta informações já cadastradas pela oficina.

## Tecnologias

Python 3.12+, Django 5.2 LTS, SQLite, scikit-learn, HTML/CSS/JavaScript e ReportLab.

## Instalação

### Forma mais simples no Windows

1. Abra a pasta do projeto.
2. Dê dois cliques em `run-boxbox.bat`.
3. Aguarde a mensagem com `http://127.0.0.1:8000/` e abra esse endereço no navegador.
4. Mantenha a janela preta aberta enquanto estiver usando o sistema. Para parar, pressione `Ctrl+C` ou feche a janela.

Depois de qualquer correção ou atualização do projeto, basta fechar o servidor antigo e executar `run-boxbox.bat` novamente. O inicializador verifica o ambiente, instala dependências, aplica migrations e inicia o Django. Ele **não apaga o banco nem os cadastros existentes**.

### Forma manual

```bash
git clone <URL-DO-REPOSITORIO>
cd box-box
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

Se o servidor já estiver aberto durante uma atualização, pare-o com `Ctrl+C` antes de iniciar novamente.

## Demonstração da IA

Com o servidor em execução, abra outro terminal na pasta do projeto e rode:

```bash
python manage.py demo_assistente
```

O comando cria uma ordem completa de demonstração e mostra no terminal o link de
acompanhamento do cliente. Também é possível entrar como atendente, abrir uma ordem e
usar a opção **Gerar link do cliente**.

No link, experimente perguntas como:

- “Qual é o status do meu carro?”
- “Quando fica pronto?”
- “Quais peças foram usadas?”
- “Quanto vai custar?”
- “Qual foi o diagnóstico?”

O modelo treinado já está incluído no repositório. Não é necessário treiná-lo novamente
para executar o sistema. Detalhes sobre dataset, métricas, API e novo treinamento estão
em [`assistente/README.md`](assistente/README.md).

## Credenciais de demonstração

| Perfil | Usuário | Senha |
|---|---|---|
| Administrador | `admin` | `boxbox123` |
| Atendente | `atendente` | `boxbox123` |
| Mecânico | `mecanico` | `boxbox123` |

Os dados são fictícios e exclusivos para demonstração.

## Testes

```bash
python manage.py test -v 2
python manage.py check
```

Fluxo manual sugerido: entrar como atendente, cadastrar cliente e veículo, abrir uma
ordem e gerar o link do cliente; entrar como mecânico, registrar
avaria/diagnóstico/peça e atualizar o status; fazer perguntas pelo link de acompanhamento;
retornar como atendente para conferir as interações, marcar a entrega e consultar os
relatórios.

## Estrutura

O projeto é organizado por **área do sistema**. Cada pasta principal responde por uma
parte fácil de explicar:

- `boxbox`: configuração geral e rotas principais do Django.
- `core`: página inicial e comando que cria dados de demonstração.
- `assistente`: link do cliente, chat, agente, modelo de IA, dados de treino e métricas.
- `accounts`: usuários, perfis e permissões.
- `customers`: clientes e veículos.
- `services`: ordens de serviço, avarias e peças.
- `reports`: filtros e exportações CSV/PDF.
- `trash`: arquivamento, restauração e exclusão de registros.
- `templates`: páginas HTML, separadas pelas mesmas áreas acima.
- `static`: estilos, JavaScript e imagens.
- `docs`: documentação técnica e diagramas.

Veja a explicação detalhada e o mapa dos arquivos em
[`docs/project-structure.md`](docs/project-structure.md).

## Configuração

As configurações opcionais estão em `.env.example`. O projeto funciona sem arquivo
`.env` em desenvolvimento. Para outra instalação, configure `DJANGO_SECRET_KEY`,
`DJANGO_DEBUG` e `DJANGO_ALLOWED_HOSTS` no ambiente. A IA é local e não exige chave de API.

## Banco

O SQLite é criado por `python manage.py migrate`. As migrations estão versionadas. Não é necessário importar um banco pronto.

## Documentação

Comece por [`docs/project-structure.md`](docs/project-structure.md). Para entender a IA,
consulte [`assistente/README.md`](assistente/README.md). Para detalhes gerais, veja
`docs/requirements.md`, `docs/architecture.md`, `docs/database.md`, `docs/testing.md`,
`docs/limitations.md` e `docs/uml/`.
