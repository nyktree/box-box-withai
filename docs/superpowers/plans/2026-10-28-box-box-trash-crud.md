# Box Box Trash and CRUD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir relatórios por perfil e adicionar edição, arquivamento auditado, restauração e exclusão definitiva para as entidades operacionais do Box Box.

**Architecture:** Adicionar um app `trash` com auditoria genérica, mantendo o estado de arquivamento nas próprias entidades. Views específicas aplicam permissões e transações; templates recebem uma coluna de ações reutilizável e uma tela central de lixeira.

**Tech Stack:** Python, Django 5.2, SQLite, Django Templates, CSS e JavaScript puro.

**Spec:** `docs/superpowers/specs/2026-10-28-box-box-trash-crud-design.md`

## Global Constraints

- Manter os três perfis existentes.
- Usar POST + CSRF para arquivar, restaurar e excluir.
- Exclusão definitiva e limpeza completa exclusivas do administrador.
- Registros protegidos permanecem arquivados e exibem mensagem explicativa.
- A publicação pública está fora deste plano.

## Review Focus

- Mecânico não pode visualizar ordens de outros mecânicos nos relatórios.
- Objetos arquivados não podem permanecer em listas ou seletores normais.
- Restauração deve reativar o mesmo registro, sem criar cópia.
- Limpeza total não pode abortar tudo quando um item estiver protegido.
- O atendente da ordem deve vir exclusivamente de `request.user`.

---

### Task 1: Corrigir relatórios por perfil

**Files:** `reports/filters.py`, `reports/views.py`, `reports/tests/test_permissions.py`

- [ ] Escrever testes para administrador, atendente e mecânico.
- [ ] Confirmar RED para atendente/mecânico.
- [ ] Permitir os três perfis e filtrar mecânico por `mechanic=request.user`.
- [ ] Verificar página, CSV e PDF.
- [ ] Commitar `fix: scope reports by operational role`.

### Task 2: Criar infraestrutura de lixeira auditada

**Files:** `trash/models.py`, `trash/services.py`, `trash/views.py`, `trash/urls.py`, migration e testes.

**Interfaces:** `archive_object(obj, actor)`, `restore_record(record, actor)`, `permanently_delete(record, actor)`.

- [ ] Escrever testes de auditoria, restauração e proteção.
- [ ] Confirmar RED.
- [ ] Implementar `TrashRecord` e serviços transacionais.
- [ ] Implementar lista, restauração, exclusão e esvaziamento.
- [ ] Commitar `feat: add audited recycle bin`.

### Task 3: Integrar clientes, veículos, peças e usuários

**Files:** views, URLs, forms e templates de `customers`, `services`, `accounts`; testes por entidade.

- [ ] Escrever testes de editar, arquivar, ocultar e restaurar.
- [ ] Confirmar RED.
- [ ] Substituir desativações isoladas pelo serviço de lixeira.
- [ ] Adicionar coluna de ações com lápis e lixeira.
- [ ] Garantir filtros `is_active=True` nas listas e seletores.
- [ ] Commitar `feat: add CRUD actions and archival flows`.

### Task 4: Integrar ordens de serviço

**Files:** `services/models.py`, migration, views, URLs, templates e testes.

- [ ] Escrever testes de `is_archived`, edição e arquivamento.
- [ ] Confirmar RED.
- [ ] Ocultar ordens arquivadas das telas e relatórios.
- [ ] Adicionar editar/arquivar na lista e detalhe.
- [ ] Preservar proteção de estados finais e reabertura administrativa.
- [ ] Commitar `feat: add order editing and archival`.

### Task 5: Identidade do atendente na abertura

**Files:** `services/forms.py`, `services/views.py`, `templates/services/order_form.html`, testes.

- [ ] Escrever teste provando que POST não pode trocar o atendente.
- [ ] Confirmar RED do contrato visual somente leitura.
- [ ] Exibir nome e grupo do usuário autenticado.
- [ ] Continuar atribuindo `order.attendant = request.user` no servidor.
- [ ] Commitar `fix: show authenticated attendant on new orders`.

### Task 6: Design, aceitação e regressão

**Files:** `templates/trash/*`, `static/css/app.css`, README e testes funcionais.

- [ ] Adicionar navegação para a lixeira conforme permissão.
- [ ] Estilizar botões de ação, confirmações e estados arquivados.
- [ ] Verificar desktop e mobile.
- [ ] Executar migrations, seed, `check` e toda a suíte.
- [ ] Revisar em navegador com administrador, atendente e mecânico.
- [ ] Solicitar revisão final independente.
- [ ] Commitar `chore: verify trash and CRUD workflows`.
