# Role Actions, Brand, and Local Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir ações incompatíveis com cada perfil, liberar catálogo de peças ao atendente, aplicar a marca fornecida e oferecer inicialização local simples.

**Architecture:** Um context processor fornece capacidades de interface derivadas dos grupos existentes, enquanto as views mantêm autorização explícita. Assets são gerados do alfa do PNG original. Um BAT idempotente prepara o ambiente e executa o servidor.

**Tech Stack:** Python, Django 5.2, Pillow, Django Templates, CSS, Windows Batch.

**Spec:** `docs/superpowers/specs/2026-10-28-role-actions-brand-run-design.md`

## Global Constraints

- Backend continua sendo a autoridade de permissão.
- Mecânico não ganha permissões administrativas.
- Atendente pode criar/editar peças, mas não arquivá-las.
- Imagem original deve preservar proporção e canal alfa.
- Script local não pode apagar banco ou dados.

## Review Focus

- Usuário em vários grupos deve receber a maior permissão aplicável.
- Superusuário não pode ser limitado por grupo incidental.
- Nenhum botão proibido deve permanecer em painel, listas ou detalhes.
- Acesso direto proibido deve retornar 403 com página útil.
- O BAT deve funcionar quando iniciado fora da pasta do projeto.

---

### Task 1: Centralizar capacidades da interface

**Files:** `accounts/context_processors.py`, `boxbox/settings.py`, templates operacionais e testes.

- [ ] Escrever testes para capacidades de administrador, atendente, mecânico e superusuário.
- [ ] Confirmar RED.
- [ ] Implementar context processor com prioridade administrativa.
- [ ] Substituir verificações frágeis nos botões de criação.
- [ ] Confirmar que mecânico não vê criar ordem, cliente, veículo ou peça.
- [ ] Commitar `fix: align interface actions with role permissions`.

### Task 2: Permitir catálogo de peças ao atendente

**Files:** `services/views.py`, templates de peças e testes.

- [ ] Escrever testes de GET/POST para criação e edição pelo atendente e bloqueio de arquivamento.
- [ ] Confirmar RED.
- [ ] Permitir `ROLE_ATTENDANT` em `part_create` e `part_update`.
- [ ] Manter `part_deactivate` administrativo.
- [ ] Confirmar GREEN e commit `fix: allow attendants to manage part catalog`.

### Task 3: Criar página 403 amigável

**Files:** `templates/403.html`, testes de integração.

- [ ] Escrever teste de URL direta proibida.
- [ ] Confirmar RED para conteúdo amigável ausente.
- [ ] Criar template com explicação e retorno ao painel.
- [ ] Confirmar status 403 e conteúdo.
- [ ] Commitar `feat: add friendly permission denied page`.

### Task 4: Gerar e aplicar marca

**Files:** `static/img/boxbox-mark.png`, `static/img/favicon.png`, `templates/base.html`, `static/css/app.css`, testes.

- [ ] Escrever teste para referências da marca e ausência de `WORKSHOP OS`.
- [ ] Confirmar RED.
- [ ] Gerar assets a partir do alfa do PNG original, com foreground coerente ao tema.
- [ ] Configurar favicon e logo lateral.
- [ ] Ajustar dimensões responsivas.
- [ ] Validar dimensões, alfa e aparência em navegador.
- [ ] Commitar `feat: apply Box Box brand assets`.

### Task 5: Criar inicializador e documentação

**Files:** `run-boxbox.bat`, `README.md`, teste textual.

- [ ] Escrever teste/validador para diretório, venv, instalação, migrate e runserver.
- [ ] Confirmar RED pela ausência do BAT.
- [ ] Criar script idempotente com mensagens claras e `pause` em erro.
- [ ] Documentar execução por dois cliques e manual.
- [ ] Exercitar o BAT em modo de verificação sem manter servidor órfão.
- [ ] Commitar `docs: add reliable local startup workflow`.

### Task 6: Verificação e revisão final

- [ ] Executar migrations check, Django check e suíte completa.
- [ ] Validar administrador, atendente e mecânico no navegador.
- [ ] Validar favicon, logo, 403 e viewport móvel.
- [ ] Solicitar revisão independente de permissões, assets e BAT.
- [ ] Corrigir achados relevantes e repetir a suíte.
