# Customer Vehicles and Order Folders Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exibir os veículos vinculados no detalhe do cliente e reorganizar ordens em pastas por proprietário, abertas em popup nativo.

**Architecture:** O detalhe do cliente recebe um queryset explícito de veículos ativos. A listagem de ordens continua filtrando no banco e agrupa o resultado no servidor em estruturas por cliente; o template renderiza uma pasta e um `<dialog>` para cada grupo, com JavaScript apenas para abrir e fechar.

**Tech Stack:** Python, Django 5.2, Django Templates, CSS e JavaScript puro.

**Spec:** `docs/superpowers/specs/2026-10-28-customer-vehicles-order-folders-design.md`

## Global Constraints

- Preservar permissões atuais e filtros de soft delete.
- Não criar API ou dependência JavaScript externa.
- Busca e filtro de status devem ser aplicados antes do agrupamento.
- Veículos e ordens arquivados não podem reaparecer.
- O popup deve funcionar em desktop e mobile.

## Review Focus

- Cliente com vários veículos deve exibir somente seus próprios veículos ativos.
- Um cliente não pode receber no popup ordens de outro proprietário.
- Busca por número ou placa deve manter somente as pastas com correspondência.
- Filtro por status deve remover ordens não correspondentes dentro da pasta.
- Mecânico não deve ganhar novas permissões de edição ou arquivamento pelo novo template.

---

### Task 1: Renderizar veículos no detalhe do cliente

**Files:**
- Modify: `customers/views.py`
- Modify: `templates/customers/customer_detail.html`
- Test: `customers/tests/test_customer_detail_vehicles.py`

**Interfaces:**
- Produces: contexto `vehicles: QuerySet[Vehicle]` contendo veículos ativos do cliente.

- [ ] Escrever testes para cliente com veículos ativos, cliente vazio, veículo de outro cliente e veículo arquivado.
- [ ] Executar os testes e confirmar a falha causada pelo placeholder atual.
- [ ] Consultar `customer.vehicles.filter(is_active=True)` com ordenação existente.
- [ ] Renderizar cards com placa, modelo, marca, ano, cor, quilometragem e link para detalhe.
- [ ] Exibir estado vazio somente quando `vehicles` estiver vazio.
- [ ] Executar os testes focados e confirmar aprovação.
- [ ] Commitar `fix: render customer vehicles on detail page`.

### Task 2: Agrupar ordens por proprietário

**Files:**
- Modify: `services/views.py`
- Test: `services/tests/test_order_customer_groups.py`

**Interfaces:**
- Produces: contexto `customer_groups: list[dict]`, cada item com `customer`, `orders`, `order_count` e `vehicle_count`.

- [ ] Escrever testes para dois clientes, várias ordens, busca por placa/número e filtro por status.
- [ ] Executar os testes e confirmar que `customer_groups` ainda não existe.
- [ ] Agrupar o queryset já filtrado por `vehicle.owner_id`, preservando a ordenação das ordens.
- [ ] Contar veículos distintos presentes em cada resultado filtrado.
- [ ] Manter `orders` temporariamente no contexto somente se algum teste legado depender dele; caso contrário, remover.
- [ ] Executar os testes focados e confirmar aprovação.
- [ ] Commitar `feat: group service orders by customer`.

### Task 3: Criar pastas e popup nativo

**Files:**
- Modify: `templates/services/order_list.html`
- Modify: `static/js/app.js`
- Modify: `static/css/app.css`
- Test: `services/tests/test_order_customer_groups.py`

**Interfaces:**
- Consumes: `customer_groups` da Task 2.
- Produces: botões `.customer-folder[data-dialog]` e diálogos `dialog.customer-orders-dialog`.

- [ ] Adicionar teste de renderização para nome, contagem, elemento `<dialog>` e links de ordem.
- [ ] Executar o teste e confirmar falha com a tabela atual.
- [ ] Renderizar grid de pastas por cliente e um diálogo por grupo.
- [ ] Dentro do diálogo, renderizar tabela compacta com ordem, veículo, status, mecânico e ações existentes.
- [ ] Adicionar abertura, fechamento por botão e fechamento por clique externo; Escape permanece nativo.
- [ ] Estilizar pasta, backdrop, cabeçalho e tabela responsiva sem alterar o tema atual.
- [ ] Executar os testes focados e confirmar aprovação.
- [ ] Commitar `feat: open customer order folders in native dialogs`.

### Task 4: Verificação e revisão

**Files:**
- Modify apenas se a verificação revelar defeitos.

- [ ] Executar `python manage.py makemigrations --check --dry-run`.
- [ ] Executar `python manage.py check`.
- [ ] Executar toda a suíte de testes.
- [ ] Verificar no navegador cliente com veículos, pastas, popup, busca e filtro.
- [ ] Verificar viewport móvel e fechamento do popup.
- [ ] Solicitar revisão independente focada em isolamento entre clientes, soft delete e permissões.
- [ ] Aplicar correções e repetir a suíte completa.
