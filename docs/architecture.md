# Arquitetura

Monólito modular Django no padrão Model–Template–View. Models representam o domínio e a persistência; módulos `domain.py` e `suggestions.py` concentram regras; views coordenam formulários e templates; SQLite é o banco padrão.

## Padrões aplicados

- Service Layer pequena para transições e sugestões.
- Template Method fornecido pelas class-based internals do Django, sem abstrações próprias desnecessárias.
- Strategy simples por perfis/grupos para autorização.
- Observer por `post_migrate` para garantir grupos.

A separação evita lógica crítica nos templates e mantém o projeto explicável.
