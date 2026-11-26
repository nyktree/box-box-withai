# Box Box — Ações por Perfil, Marca e Inicialização

## Objetivo

Eliminar ações visíveis que levam usuários sem permissão a páginas de erro, liberar o catálogo de peças para atendentes, aplicar o ícone fornecido à marca e simplificar a inicialização local do projeto.

## Permissões

### Mecânico

Pode consultar painel, ordens, clientes, veículos, peças, relatórios permitidos e dados técnicos. Continua podendo editar dados técnicos somente nas próprias ordens.

Não pode criar:

- ordem de serviço;
- cliente;
- veículo;
- peça do catálogo.

Os respectivos botões não serão renderizados para o mecânico. O backend continuará bloqueando tentativas por URL direta.

### Atendente

Pode criar ordens, clientes e veículos. Passa a poder criar e editar peças do catálogo. Arquivamento de peças permanece exclusivo do administrador.

### Administrador

Mantém acesso integral.

## Resposta de permissão

A aplicação manterá `PermissionDenied` no backend. Será criada uma página 403 em português, com explicação simples e botão de retorno ao painel, para acessos diretos não autorizados.

## Regras de apresentação

A visibilidade das ações será calculada por um context processor centralizado, evitando comparações frágeis como `user.groups.first.name` espalhadas nos templates. O contexto disponibilizará indicadores como:

- `is_admin_role`;
- `is_attendant_role`;
- `is_mechanic_role`;
- `can_create_orders`;
- `can_create_customers`;
- `can_create_vehicles`;
- `can_manage_part_catalog`.

A autorização do backend continua sendo a fonte de verdade.

## Marca

O arquivo fornecido é um PNG RGBA de 512 × 512 cujo RGB é preto e cuja forma está no canal alfa. Como o desenho desaparece no tema escuro, será gerada uma versão de primeiro plano claro/vermelho preservando o alfa.

Serão criados:

- `static/img/boxbox-mark.png`, para a barra lateral;
- `static/img/favicon.png`, para a aba do navegador.

A barra lateral exibirá o ícone e o texto `BOX BOX`. O subtítulo `WORKSHOP OS` será removido. O ícone terá dimensões controladas e não deformará em desktop ou mobile.

## Inicialização local

Será criado `run-boxbox.bat` na raiz. O script:

1. muda para a própria pasta;
2. verifica se `.venv` existe;
3. cria o ambiente caso não exista;
4. instala `requirements.txt` na primeira execução;
5. executa migrations;
6. inicia Django em `127.0.0.1:8000`;
7. mantém o terminal aberto em caso de erro.

O README explicará:

- inicialização com dois cliques;
- inicialização manual;
- quando migrations e instalação de dependências são necessárias;
- que alterações só aparecem depois de reiniciar o servidor quando ele não estiver rodando com recarga automática;
- URL correta de acesso.

## Testes

- mecânico não recebe botões de criação;
- URLs diretas continuam bloqueadas;
- atendente cria e edita peças;
- atendente não arquiva peças;
- administrador mantém acesso;
- página 403 possui texto e retorno;
- base template usa o ícone e não contém `WORKSHOP OS`;
- favicon configurado;
- assets gerados possuem alfa e dimensões esperadas;
- script BAT contém os passos necessários;
- suíte completa permanece aprovada.
