# Box Box Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir uma aplicação Django completa e reproduzível para uma oficina gerenciar usuários, clientes, veículos, ordens de serviço, avarias, diagnósticos, peças, histórico e relatórios.

**Architecture:** Monólito modular Django baseado em Model–Template–View, com regras de negócio concentradas em models e pequenos módulos de serviço. Templates renderizados no servidor, CSS/JavaScript próprios e SQLite como banco padrão tornam a solução fácil de instalar, testar, apresentar e explicar.

**Tech Stack:** Python 3.12+, Django 5.2 LTS, SQLite, HTML5, CSS3, JavaScript puro, ReportLab para PDF e suíte de testes nativa do Django.

**Spec:** `docs/superpowers/specs/2026-10-28-box-box-design.md`

## Global Constraints

- Linguagem principal: Python.
- Framework: Django 5.2 LTS, sem Django REST Framework.
- Banco padrão: SQLite criado por migrations.
- Frontend: Django Templates, CSS e JavaScript puros.
- Aplicação para uma única oficina com perfis Administrador, Atendente e Mecânico.
- Não usar plataformas low-code/no-code.
- Não adicionar Node.js, React, microsserviços ou infraestrutura distribuída.
- Interface escura, limpa e responsiva; vermelho contido como acento e cores semânticas para status.
- Todo fluxo crítico deve ter teste automatizado e instrução de teste manual no README.
- Dados demonstrativos devem ser claramente fictícios e carregados por comando reproduzível.
- Nenhum caminho absoluto ou segredo real deve ser versionado.

## Review Focus

- Criação simultânea de ordens deve manter números `BB-AAAA-NNNN` únicos e sequenciais; teste em Task 5.
- Um mecânico não atribuído deve visualizar a ordem sem conseguir alterar dados técnicos ou status; teste em Task 7.
- Ordens entregues/canceladas devem bloquear alterações comuns e só reabrir por administrador com justificativa; teste em Task 6.
- Clientes, veículos, peças e usuários históricos devem ser desativados sem destruir relacionamentos; testes em Tasks 3, 4 e 8.
- Exportações vazias ou filtradas devem produzir arquivo válido sem erro e sem vazar dados fora do filtro; teste em Task 10.

---

## File Structure

```text
box-box/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── boxbox/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── views.py
│   ├── urls.py
│   ├── context_processors.py
│   ├── management/commands/seed_demo.py
│   └── tests/
├── accounts/
│   ├── forms.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── customers/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── services/
│   ├── models.py
│   ├── forms.py
│   ├── domain.py
│   ├── suggestions.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── reports/
│   ├── filters.py
│   ├── exporters.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── templates/
│   ├── base.html
│   ├── registration/login.html
│   ├── core/
│   ├── accounts/
│   ├── customers/
│   ├── services/
│   └── reports/
├── static/
│   ├── css/app.css
│   ├── js/app.js
│   └── icons/
└── docs/
    ├── requirements.md
    ├── architecture.md
    ├── database.md
    ├── testing.md
    ├── limitations.md
    └── uml/
```

---

### Task 1: Bootstrap reproduzível e autenticação básica

**Files:**
- Create: `manage.py`, `boxbox/settings.py`, `boxbox/urls.py`, `boxbox/wsgi.py`
- Create: `requirements.txt`, `.env.example`, `.gitignore`
- Create: `core/`, `accounts/`, `customers/`, `services/`, `reports/`
- Create: `templates/registration/login.html`, `templates/base.html`
- Test: `core/tests/test_bootstrap.py`

**Interfaces:**
- Produces: projeto Django executável; rota `login`; rota `logout`; nomes de grupos `Administrador`, `Atendente`, `Mecânico`.

- [ ] **Step 1: Escrever testes de bootstrap** verificando carregamento das configurações, redirecionamento de usuário anônimo para login e renderização da tela de login.
- [ ] **Step 2: Executar `python manage.py test core.tests.test_bootstrap -v 2`** e confirmar falha por projeto/rotas inexistentes.
- [ ] **Step 3: Criar projeto, apps, configurações, URLs e templates mínimos**, usando SQLite e diretórios globais de templates/static.
- [ ] **Step 4: Executar migrations e os testes da tarefa**, esperando sucesso.
- [ ] **Step 5: Commitar** com `chore: bootstrap Django project and authentication`.

### Task 2: Perfis, grupos e autorização reutilizável

**Files:**
- Create: `accounts/permissions.py`
- Create: `accounts/forms.py`, `accounts/views.py`, `accounts/urls.py`
- Create: `templates/accounts/user_list.html`, `user_form.html`
- Test: `accounts/tests/test_permissions.py`, `accounts/tests/test_user_management.py`

**Interfaces:**
- Produces: `user_has_role(user, role_name) -> bool`; `role_required(*roles)`; CRUD administrativo de usuários com atribuição a exatamente um perfil operacional.

- [ ] **Step 1: Escrever testes de permissões** para administrador, atendente, mecânico, usuário anônimo e usuário sem grupo.
- [ ] **Step 2: Executar os testes** e confirmar falha por helpers inexistentes.
- [ ] **Step 3: Implementar helpers e criação automática dos três grupos** por migration de dados ou comando idempotente.
- [ ] **Step 4: Escrever testes do gerenciamento de usuários**, incluindo bloqueio para não administradores e desativação preservando autoria.
- [ ] **Step 5: Implementar views/forms/templates mínimos de usuários** e executar a suíte da tarefa.
- [ ] **Step 6: Commitar** com `feat: add role-based user management`.

### Task 3: Domínio de clientes

**Files:**
- Create: `customers/models.py`, `customers/forms.py`, `customers/views.py`, `customers/urls.py`
- Create: `templates/customers/customer_list.html`, `customer_form.html`, `customer_detail.html`
- Test: `customers/tests/test_customers.py`

**Interfaces:**
- Produces: model `Customer`; URLs nomeadas `customer_list`, `customer_create`, `customer_update`, `customer_detail`, `customer_deactivate`.

- [ ] **Step 1: Escrever testes do model/formulário** para cadastro válido, nome/telefone obrigatórios e CPF/CNPJ opcional.
- [ ] **Step 2: Executar os testes** e confirmar falha.
- [ ] **Step 3: Implementar `Customer`**, migration e formulários.
- [ ] **Step 4: Escrever testes das views**, busca, permissões e desativação em vez de exclusão quando houver histórico.
- [ ] **Step 5: Implementar views e templates funcionais** e executar os testes.
- [ ] **Step 6: Commitar** com `feat: add customer management`.

### Task 4: Domínio de veículos e histórico-base

**Files:**
- Modify: `customers/models.py`, `customers/forms.py`, `customers/views.py`, `customers/urls.py`
- Create: `templates/customers/vehicle_list.html`, `vehicle_form.html`, `vehicle_detail.html`
- Test: `customers/tests/test_vehicles.py`

**Interfaces:**
- Produces: model `Vehicle`; função `normalize_plate(value: str) -> str`; URLs `vehicle_list`, `vehicle_create`, `vehicle_update`, `vehicle_detail`, `vehicle_deactivate`.
- Consumes: `Customer` da Task 3.

- [ ] **Step 1: Escrever testes** para placa normalizada/única, proprietário obrigatório, quilometragem não negativa e vínculo cliente–veículo.
- [ ] **Step 2: Executar os testes** e confirmar falha.
- [ ] **Step 3: Implementar model, validações, migration e formulário**.
- [ ] **Step 4: Escrever testes de views** para busca por placa/modelo/cliente, acesso por perfil e desativação preservando relacionamento.
- [ ] **Step 5: Implementar listagem, criação, edição e detalhe** com área reservada ao histórico.
- [ ] **Step 6: Commitar** com `feat: add vehicle management`.

### Task 5: Ordens de serviço, numeração e auditoria de status

**Files:**
- Create: `services/models.py`, `services/domain.py`
- Test: `services/tests/test_service_orders.py`, `services/tests/test_order_numbering.py`

**Interfaces:**
- Produces: models `ServiceOrder`, `StatusHistory`; enum `ServiceOrder.Status`; `generate_order_number(year: int) -> str`; `transition_order(order, new_status, actor, note='') -> StatusHistory`.
- Consumes: `Vehicle`, usuário Django e helpers de perfil.

- [ ] **Step 1: Escrever testes do model** para campos obrigatórios, valores não negativos e formato `BB-AAAA-NNNN`.
- [ ] **Step 2: Escrever teste transacional de numeração** garantindo unicidade e sequência no mesmo ano e reinício no ano seguinte.
- [ ] **Step 3: Executar os testes** e confirmar falha.
- [ ] **Step 4: Implementar models, constraints, geração transacional e migrations**.
- [ ] **Step 5: Escrever testes da matriz de transições** e criação automática de `StatusHistory`.
- [ ] **Step 6: Implementar `transition_order`** com validação de perfil, atribuição e estado.
- [ ] **Step 7: Executar a suíte da tarefa** e esperar sucesso.
- [ ] **Step 8: Commitar** com `feat: add service order lifecycle`.

### Task 6: Avarias, diagnósticos, sugestões e reabertura controlada

**Files:**
- Modify: `services/models.py`, `services/domain.py`
- Create: `services/suggestions.py`
- Test: `services/tests/test_damages.py`, `services/tests/test_suggestions.py`, `services/tests/test_reopening.py`

**Interfaces:**
- Produces: models `DamageCategory`, `Damage`, `CauseSuggestion`; `get_suggestions(damage: Damage) -> QuerySet[CauseSuggestion]`; `reopen_order(order, actor, justification) -> StatusHistory`.

- [ ] **Step 1: Escrever testes de avarias** para descrição, gravidade, diagnóstico e causa confirmada estruturada/textual.
- [ ] **Step 2: Executar e confirmar falha**.
- [ ] **Step 3: Implementar models e migrations**.
- [ ] **Step 4: Escrever testes de sugestões** verificando categoria, palavras-chave, prioridade e desempate por frequência histórica.
- [ ] **Step 5: Implementar `get_suggestions`** sem IA externa.
- [ ] **Step 6: Escrever testes de bloqueio/reabertura** para ordens entregues e canceladas, incluindo justificativa obrigatória e exclusividade do administrador.
- [ ] **Step 7: Implementar `reopen_order` e bloqueios de domínio**.
- [ ] **Step 8: Executar testes e commitar** com `feat: add damage diagnosis and suggestions`.

### Task 7: Interface operacional das ordens

**Files:**
- Create: `services/forms.py`, `services/views.py`, `services/urls.py`
- Create: `templates/services/order_list.html`, `order_form.html`, `order_detail.html`, `_damage_panel.html`, `_status_timeline.html`
- Test: `services/tests/test_order_views.py`, `services/tests/test_order_permissions.py`

**Interfaces:**
- Produces: URLs `order_list`, `order_create`, `order_detail`, `order_update`, `order_transition`, `damage_create`, `damage_update`.
- Consumes: models e funções de domínio das Tasks 5–6.

- [ ] **Step 1: Escrever testes do fluxo de abertura** por atendente/administrador e bloqueio para mecânico.
- [ ] **Step 2: Implementar forms/views/templates mínimos** para lista, filtros, criação e detalhe.
- [ ] **Step 3: Escrever testes de autorização por objeto**, provando que mecânico não atribuído vê mas não edita, e atribuído edita dados técnicos.
- [ ] **Step 4: Implementar edição, transição e avarias expansíveis** com `<details>` ou JavaScript progressivo acessível.
- [ ] **Step 5: Escrever teste funcional do ciclo completo** da abertura até pronta/entregue.
- [ ] **Step 6: Executar a suíte da tarefa** e corrigir até passar.
- [ ] **Step 7: Commitar** com `feat: add operational service order interface`.

### Task 8: Catálogo de peças e peças utilizadas

**Files:**
- Modify: `services/models.py`, `services/forms.py`, `services/views.py`, `services/urls.py`
- Create: `templates/services/part_list.html`, `part_form.html`, `_service_parts.html`
- Test: `services/tests/test_parts.py`

**Interfaces:**
- Produces: models `Part`, `DamagePartSuggestion`, `ServicePart`; CRUD administrativo de peças; adição/remoção de peças em ordens editáveis.

- [ ] **Step 1: Escrever testes** para quantidade positiva, snapshot de valor unitário e ausência de movimentação automática de estoque.
- [ ] **Step 2: Executar e confirmar falha**.
- [ ] **Step 3: Implementar models, constraints e migrations**.
- [ ] **Step 4: Escrever testes de views/permissões**, incluindo desativação de peça já utilizada e bloqueio em ordem finalizada.
- [ ] **Step 5: Implementar forms/views/templates** e indicação textual de estoque informativo.
- [ ] **Step 6: Executar testes e commitar** com `feat: add parts and service usage`.

### Task 9: Dashboard e histórico consolidado do veículo

**Files:**
- Create: `core/views.py`, `core/urls.py`, `templates/core/dashboard.html`
- Modify: `customers/views.py`, `templates/customers/vehicle_detail.html`
- Test: `core/tests/test_dashboard.py`, `customers/tests/test_vehicle_history.py`

**Interfaces:**
- Produces: rota `dashboard`; consulta consolidada do histórico por veículo.

- [ ] **Step 1: Escrever testes do dashboard** para contagens reais, ordens por status e busca por placa/cliente/número.
- [ ] **Step 2: Implementar consultas e template operacional**, evitando métricas decorativas.
- [ ] **Step 3: Escrever testes do histórico** verificando ordem cronológica, avarias, diagnóstico, peças, quilometragem e valores.
- [ ] **Step 4: Implementar histórico no detalhe do veículo**.
- [ ] **Step 5: Executar testes e commitar** com `feat: add workshop dashboard and vehicle history`.

### Task 10: Relatórios CSV e PDF

**Files:**
- Create: `reports/filters.py`, `reports/exporters.py`, `reports/views.py`, `reports/urls.py`
- Create: `templates/reports/index.html`
- Test: `reports/tests/test_reports.py`, `reports/tests/test_exporters.py`

**Interfaces:**
- Produces: `build_order_queryset(params, user) -> QuerySet[ServiceOrder]`; `export_orders_csv(queryset) -> HttpResponse`; `export_orders_pdf(queryset) -> HttpResponse`.

- [ ] **Step 1: Escrever testes de filtros** por período, status, cliente, veículo e responsável.
- [ ] **Step 2: Implementar `build_order_queryset` e página de relatório**.
- [ ] **Step 3: Escrever testes CSV/PDF** para conjunto vazio, caracteres acentuados, filtros e tipos de conteúdo válidos.
- [ ] **Step 4: Implementar exportadores**, usando `csv` padrão e ReportLab.
- [ ] **Step 5: Executar testes e commitar** com `feat: add filtered CSV and PDF reports`.

### Task 11: Sistema visual responsivo e acessibilidade

**Files:**
- Modify: todos os templates existentes
- Create: `static/css/app.css`, `static/js/app.js`, `static/icons/*.svg`
- Test: `core/tests/test_ui_contracts.py`

**Interfaces:**
- Produces: layout lateral/compacto, tokens CSS, componentes visuais de status, tabelas responsivas, feedback e comportamento de expansão.

- [ ] **Step 1: Escrever testes de contratos HTML** para landmarks, labels, foco, classes semânticas de status e ausência de botões sem nome acessível.
- [ ] **Step 2: Implementar tokens e componentes visuais**, usando grafite, vermelho contido, bordas finas e raio discreto.
- [ ] **Step 3: Implementar responsividade**, menu mobile, tabelas adaptáveis e alvos mínimos de 44px.
- [ ] **Step 4: Implementar JavaScript progressivo** para menu e feedback, com fallback e `prefers-reduced-motion`.
- [ ] **Step 5: Verificar no navegador em desktop e mobile**, corrigindo overflow, contraste, estados vazios e console.
- [ ] **Step 6: Executar testes e commitar** com `feat: apply Box Box responsive design system`.

### Task 12: Dados demonstrativos e fluxo de aceitação

**Files:**
- Create: `core/management/commands/seed_demo.py`
- Test: `core/tests/test_seed_demo.py`, `core/tests/test_acceptance_flow.py`

**Interfaces:**
- Produces: comando idempotente `python manage.py seed_demo`; credenciais acadêmicas fictícias documentáveis.

- [ ] **Step 1: Escrever teste de idempotência do seed** e presença dos três usuários/perfis, clientes, veículos, peças e ordens em diferentes estados.
- [ ] **Step 2: Implementar o comando de seed** com dados coerentes e fictícios.
- [ ] **Step 3: Escrever teste de aceitação ponta a ponta no cliente Django** cobrindo login, cliente, veículo, ordem, avaria, diagnóstico, peça, status, histórico e relatório.
- [ ] **Step 4: Executar seed duas vezes e toda a suíte**, esperando ausência de duplicações e sucesso.
- [ ] **Step 5: Commitar** com `test: add demo data and acceptance workflow`.

### Task 13: Documentação técnica, UML e README reproduzível

**Files:**
- Create/Modify: `README.md`
- Create: `docs/requirements.md`, `docs/architecture.md`, `docs/database.md`, `docs/testing.md`, `docs/limitations.md`
- Create: `docs/uml/use-cases.puml`, `class-diagram.puml`, `service-order-sequence.puml`, `service-order-activity.puml`
- Test: `core/tests/test_documentation_contract.py`

**Interfaces:**
- Produces: documentação suficiente para instalação, apresentação acadêmica e explicação do sistema.

- [ ] **Step 1: Escrever teste documental** verificando arquivos obrigatórios e comandos essenciais no README.
- [ ] **Step 2: Documentar requisitos funcionais/não funcionais, arquitetura, metodologia, banco, padrões, testes e limitações**.
- [ ] **Step 3: Criar diagramas PlantUML** de casos de uso, classes, sequência e atividade.
- [ ] **Step 4: Escrever README completo** com clonagem, ambiente virtual, dependências, migrations, seed, execução, testes, credenciais e estrutura.
- [ ] **Step 5: Executar o teste documental e revisar links/caminhos**.
- [ ] **Step 6: Commitar** com `docs: add academic and technical documentation`.

### Task 14: Verificação limpa de implantação e entrega

**Files:**
- Modify: arquivos encontrados durante a verificação, somente quando necessário.

**Interfaces:**
- Consumes: aplicação completa e README.
- Produces: evidência de instalação limpa, testes aprovados e aplicação navegável.

- [ ] **Step 1: Criar um ambiente virtual limpo fora do projeto** e seguir exclusivamente o README.
- [ ] **Step 2: Instalar `requirements.txt`, executar migrations e seed**, registrando qualquer instrução ausente.
- [ ] **Step 3: Executar `python manage.py check --deploy`**, distinguindo avisos aceitáveis de desenvolvimento de erros reais.
- [ ] **Step 4: Executar `python manage.py test -v 2`** e exigir zero falhas/erros.
- [ ] **Step 5: Iniciar servidor e verificar no navegador** login, dashboard, fluxo principal, exportações e layouts desktop/mobile.
- [ ] **Step 6: Corrigir somente problemas comprovados, repetir toda a verificação e registrar resultados em `docs/testing.md`**.
- [ ] **Step 7: Solicitar revisão final independente do branch**.
- [ ] **Step 8: Commitar** com `chore: verify clean installation and release readiness`.

---

## Self-Review

- **Cobertura da especificação:** todos os perfis, cadastros, estados, auditoria, sugestões, histórico, relatórios, responsividade, testes, seed, documentação e implantação limpa possuem tarefa responsável.
- **Granularidade:** cada tarefa entrega um subsistema testável e possui ciclo explícito de falha, implementação, verificação e commit.
- **Consistência:** nomes públicos de models, helpers, rotas e funções são definidos uma vez e consumidos nas tarefas seguintes.
- **Review Focus:** concorrência na numeração, autorização por objeto, estados finais, preservação histórica e exportações vazias estão associados a testes específicos.
- **Proporção:** o plano define interfaces e provas, deixando corpos de implementação para a execução.
