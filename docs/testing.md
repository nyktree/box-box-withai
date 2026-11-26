# Testes

A suíte usa `django.test` e banco temporário isolado.

- Unitários: normalização de placa, permissões, transições, sugestões e validações.
- Integração: relações do ORM, histórico de status, seed e exportadores.
- Funcionais: acesso às telas por perfil e fluxo operacional.
- Regressão: `python manage.py test -v 2`.

A verificação final executou migrations, seed, check e toda a suíte em um clone limpo seguindo o README.

## Resultado verificado

- `python manage.py check`: nenhum problema identificado.
- `python manage.py test`: 28 testes executados, zero falhas.
- Clone limpo: dependências instaladas, migrations e seed concluídos.
- Navegador desktop: login, navegação e três ordens demonstrativas renderizadas.
- Navegador móvel (390 × 844): sem overflow horizontal e menu com alvo de 44 px.
