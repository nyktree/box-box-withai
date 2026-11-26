# Estrutura do projeto

Este projeto usa a estrutura padrão do Django e separa o sistema por áreas de
negócio. A ideia central é simples: cada pasta principal contém tudo que pertence
a uma funcionalidade.

## Mapa rápido

```text
box-box/
├── manage.py              # Executa os comandos do Django
├── run-boxbox.bat         # Inicialização fácil no Windows
├── requirements.txt       # Bibliotecas Python necessárias
├── boxbox/                # Configuração central do projeto
├── core/                  # Dashboard e dados de demonstração
├── accounts/              # Usuários e permissões
├── customers/             # Clientes e veículos
├── services/              # Ordens de serviço, avarias e peças
├── reports/               # Relatórios CSV e PDF
├── trash/                 # Lixeira do sistema
├── templates/             # Telas HTML
├── static/                # CSS, JavaScript e imagens
└── docs/                  # Documentação e diagramas
```

## Arquivos da raiz

- `manage.py`: porta de entrada para comandos como `runserver`, `migrate` e
  `test`.
- `run-boxbox.bat`: prepara o ambiente e inicia o projeto no Windows.
- `requirements.txt`: lista Django e ReportLab, as dependências do programa.
- `.env.example`: mostra as configurações opcionais de ambiente.
- `db.sqlite3`: banco local usado durante desenvolvimento e demonstração.
- `README.md`: instruções para instalar, executar e testar.

## Configuração central: `boxbox/`

- `settings.py`: banco, aplicativos instalados, idioma, arquivos estáticos e
  autenticação.
- `urls.py`: liga cada endereço principal à área responsável.
- `wsgi.py` e `asgi.py`: pontos de entrada usados por servidores web.

## Como ler cada área

As áreas Django repetem uma organização previsível:

- `models.py`: estrutura dos dados salvos no banco.
- `forms.py`: campos e validações dos formulários.
- `views.py`: recebe a requisição, chama as regras e escolhe a página de resposta.
- `urls.py`: endereços disponíveis naquela área.
- `admin.py`: registro de dados no painel administrativo do Django.
- `apps.py`: configuração da área.
- `migrations/`: histórico versionado da estrutura do banco; não deve ser editado
  manualmente.
- `tests/`: testes automáticos da área.

### `core/`

Contém o dashboard em `views.py` e o comando
`management/commands/seed_demo.py`, que cria usuários e dados para demonstração.

### `accounts/`

Cuida dos usuários. `permissions.py` define os três perfis — administrador,
atendente e mecânico — e protege as telas conforme cada perfil.

### `customers/`

Cuida de clientes e veículos. Os dois modelos ficam juntos porque todo veículo
pertence a um cliente.

### `services/`

É a área principal do sistema:

- `models.py`: ordens, histórico de status, avarias e peças.
- `domain.py`: regras para mudar o status e reabrir uma ordem.
- `suggestions.py`: sugestões relacionadas às avarias.
- `views.py`: telas e ações do fluxo de atendimento.

Separar as regras de transição em `domain.py` evita misturá-las com HTML e deixa
o fluxo mais fácil de testar e explicar.

### `reports/`

`filters.py` monta a consulta das ordens e `exporters.py` transforma o resultado
em CSV ou PDF. `views.py` apenas conecta as URLs a essas funções.

### `trash/`

Implementa a lixeira sem duplicar essa lógica nas outras áreas. `services.py`
arquiva, restaura ou exclui; `models.py` guarda o histórico dessas ações.

## Interface

`templates/` contém os arquivos HTML. Suas subpastas têm os mesmos nomes das
áreas Python, facilitando encontrar a tela correspondente. `base.html` define a
estrutura comum das páginas.

`static/` contém:

- `css/app.css`: aparência do sistema.
- `js/app.js`: comportamento executado no navegador.
- `img/`: logotipo e ícone.

## Fluxo de uma requisição

Exemplo ao abrir uma ordem de serviço:

1. `boxbox/urls.py` encaminha `/ordens/` para `services/urls.py`.
2. `services/urls.py` escolhe uma função de `services/views.py`.
3. A view usa `forms.py`, `models.py` e, quando necessário, `domain.py`.
4. A resposta é exibida por um arquivo em `templates/services/`.

Essa mesma sequência vale para as outras áreas e é o caminho mais simples para
explicar o projeto.
