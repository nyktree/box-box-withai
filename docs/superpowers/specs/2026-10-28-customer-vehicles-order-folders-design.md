# Box Box — Veículos do Cliente e Ordens Agrupadas

## Intenção

Corrigir a tela de detalhes do cliente para mostrar seus veículos e reduzir o tamanho visual da listagem de ordens agrupando-as pelo proprietário.

## Abordagens consideradas

1. **Popup nativo com dados previamente carregados — escolhido.** Mais simples, rápido, acessível e adequado ao porte acadêmico do sistema.
2. Popup com carregamento assíncrono. Escala melhor para muitos milhares de registros, mas adicionaria endpoint e JavaScript sem necessidade atual.

## Tela do cliente

- Consultar os veículos ativos relacionados por `Vehicle.owner` / `Customer.vehicles`.
- Exibir cards com placa, marca, modelo, ano, cor e quilometragem.
- Cada card leva aos detalhes do veículo.
- Exibir estado vazio real somente quando não houver veículos ativos.
- Permitir cadastrar novo veículo já associado ao cliente por meio do formulário existente, quando viável sem alterar o domínio.

## Tela de ordens

- Manter o queryset operacional existente: somente ordens não arquivadas, com cliente e veículo ativos.
- Aplicar busca e filtro de status antes do agrupamento.
- Agrupar o resultado por cliente no servidor para evitar lógica de domínio no template.
- Exibir um card/pasta por cliente com nome, telefone, número de veículos presentes no resultado e quantidade de ordens.
- A pasta é um botão que abre um modal `<dialog>`.

## Popup do cliente

O popup exibirá:

- nome e telefone do cliente;
- ordens filtradas daquele cliente;
- número da ordem;
- veículo e placa;
- status;
- mecânico;
- ação para visualizar;
- ação para editar;
- ação para arquivar quando o perfil permitir.

O modal fecha por botão, tecla Escape ou clique na área externa. Em telas pequenas ocupa quase toda a viewport e permite rolagem interna.

## Filtros e estados vazios

- A busca continua aceitando número da ordem, placa ou nome do cliente.
- O filtro de status continua usando os estados atuais.
- Pastas sem ordens após o filtro não são renderizadas.
- Se nenhuma ordem corresponder, a página mostra um estado vazio único.

## Permissões

- O agrupamento não muda permissões existentes.
- Botões podem ser ocultados conforme o perfil, mas o backend continua sendo a autoridade.
- Mecânicos continuam sujeitos às regras atuais de edição e arquivamento.

## Testes

- cliente com veículos ativos exibe os veículos;
- cliente sem veículos exibe estado vazio;
- veículos arquivados não aparecem;
- ordens são agrupadas pelo proprietário correto;
- busca e status removem ordens e pastas sem correspondência;
- modal contém links e ações esperadas;
- permissões existentes permanecem válidas;
- interface funciona em desktop e viewport móvel.
