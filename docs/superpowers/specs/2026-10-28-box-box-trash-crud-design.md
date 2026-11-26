# Box Box — Design da Lixeira, CRUD e Permissões

## Objetivo

Corrigir o acesso aos relatórios e tornar clientes, veículos, ordens, peças e usuários fáceis de editar, arquivar, restaurar e, quando seguro, excluir definitivamente.

## Relatórios

- Administrador e atendente consultam todas as ordens.
- Mecânico consulta apenas ordens atribuídas a ele.
- Página, CSV e PDF usam o mesmo escopo e os mesmos filtros.
- O item de navegação permanece visível aos três perfis.

## Ações nas listas

As listas de clientes, veículos, ordens, peças e usuários terão uma coluna de ações:

- editar, representado por ícone de lápis;
- mover para a lixeira, representado por ícone de lixeira.

Os botões terão rótulos acessíveis e confirmação antes de arquivar.

## Lixeira centralizada

A lixeira armazenará eventos de arquivamento com:

- tipo do registro;
- identificador do registro;
- descrição legível;
- usuário que arquivou;
- data e hora;
- usuário e data da restauração, quando aplicável.

Cada entidade arquivável terá `is_active` ou `is_archived`. Registros arquivados deixam de aparecer nas listagens normais, buscas e seletores.

A lixeira permitirá:

- restaurar individualmente;
- excluir definitivamente individualmente;
- esvaziar toda a lixeira.

Restauração estará disponível ao administrador e aos perfis que possuam permissão para administrar aquele tipo. Exclusão definitiva e limpeza completa serão exclusivas do administrador.

Exclusão definitiva respeitará a integridade relacional. Quando `PROTECT` impedir a remoção, o sistema apresentará uma mensagem explicando que o registro possui histórico dependente e deve permanecer arquivado. Ordens podem ser excluídas definitivamente pelo administrador, removendo seus detalhes dependentes em cascata, mas não removendo cliente, veículo ou usuários relacionados.

## Ordens

- A listagem terá edição e arquivamento.
- Ordens entregues ou canceladas permanecem bloqueadas para edição comum.
- O administrador pode reabrir uma ordem finalizada com justificativa antes de editá-la.
- Arquivamento não altera o histórico técnico interno.

## Atendente responsável

Na abertura da ordem, o atendente será sempre o usuário autenticado. A interface exibirá um bloco somente leitura com nome e perfil, por exemplo:

`Marina · Atendente responsável`

Não haverá campo para escolher ou falsificar outro atendente. O servidor continuará atribuindo `request.user` independentemente do conteúdo enviado pelo navegador.

## Entidades

- `Customer`: já possui `is_active`; será usado como estado de arquivamento.
- `Vehicle`: já possui `is_active`.
- `Part`: já possui `is_active`.
- `User`: usa `is_active` nativo.
- `ServiceOrder`: receberá `is_archived`.
- `TrashRecord`: registra auditoria e oferece referência genérica ao objeto arquivado.

## Segurança funcional

- Operações de arquivamento, restauração e exclusão definitiva usarão POST e CSRF.
- Exclusão definitiva e esvaziamento exigirão administrador.
- Views validarão permissões no servidor.
- Operações em lote serão transacionais.

## Testes

- relatórios acessíveis e corretamente filtrados por perfil;
- edição e arquivamento por entidade;
- itens arquivados ausentes das listas normais;
- restauração devolvendo o registro à lista;
- autoria e data do arquivamento registradas;
- exclusão definitiva protegida por perfil e integridade;
- limpeza total processando todos os itens possíveis e informando bloqueados;
- atendente autenticado atribuído automaticamente à ordem;
- ordens finalizadas continuam protegidas.

## Fora desta etapa

A publicação pública e migração para PostgreSQL serão tratadas depois da conclusão e validação destas funcionalidades.
