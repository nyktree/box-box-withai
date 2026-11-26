# Box Box — Documento de Design

## 1. Intenção

O Box Box será uma aplicação web de gestão para uma única oficina mecânica. O sistema centralizará clientes, veículos, avarias, ordens de serviço, manutenções e o histórico técnico dos veículos, reduzindo o uso de registros dispersos e tornando o andamento dos serviços visível para a equipe.

O projeto também deve demonstrar, de maneira compreensível para uma banca acadêmica, práticas de engenharia e qualidade de software: orientação a objetos, requisitos, arquitetura, banco de dados relacional, controle de acesso, testes, documentação e diagramas UML.

## 2. Público e perfis

### Administrador

- Acesso integral ao sistema.
- Gerencia usuários e consulta todas as informações.
- Cadastra, edita e consulta clientes, veículos, peças, avarias e serviços.
- Consulta indicadores e exporta relatórios.

### Atendente

- Cadastra e atualiza clientes e veículos.
- Abre ordens de serviço e registra sintomas relatados.
- Consulta o andamento dos serviços e o histórico dos veículos.
- Não gerencia usuários nem exclui registros críticos.

### Mecânico

- Consulta veículos e ordens atribuídas.
- Registra diagnóstico, avarias, causas, peças e observações técnicas.
- Atualiza o andamento permitido da ordem de serviço.
- Consulta o histórico técnico do veículo.

## 3. Objetivos

- Manter clientes e veículos associados corretamente.
- Registrar ordens de serviço e acompanhar seu andamento.
- Preservar o histórico de manutenção de cada veículo.
- Registrar avarias em seções expansíveis, evitando poluição visual.
- Sugerir possíveis causas e peças com base em regras simples e registros anteriores.
- Exportar informações operacionais em CSV e PDF.
- Demonstrar persistência, integridade relacional, orientação a objetos e testes.
- Permitir instalação e execução por terceiros seguindo apenas o README.

## 4. Não objetivos

- Atender múltiplas oficinas independentes.
- Criar aplicativo móvel nativo.
- Integrar pagamentos, emissão fiscal ou fornecedores externos.
- Usar inteligência artificial generativa para diagnóstico.
- Construir um ERP completo de estoque, contabilidade ou folha de pagamento.
- Implantar infraestrutura distribuída ou arquitetura de microsserviços.

## 5. Antiobjetivos

O projeto será considerado inadequado se:

- Parecer apenas uma demonstração visual sem fluxos completos.
- Exigir conhecimentos excessivos para que os integrantes expliquem o código.
- Adicionar tecnologias sem necessidade acadêmica ou funcional.
- Apresentar dados fictícios como se fossem estatísticas reais.
- Usar uma interface genérica de SaaS, carregada de cards decorativos, gradientes ou elementos sem função.
- Depender de caminhos absolutos ou configurações locais não documentadas.

## 6. Restrições

- Linguagem principal: Python.
- Framework: Django.
- Banco relacional padrão: SQLite.
- Interface: Django Templates, HTML, CSS e JavaScript puro.
- Sem low-code ou no-code.
- Repositório público preparado para GitHub.
- Código e arquitetura devem ser compreensíveis e explicáveis pela equipe.
- A aplicação deve funcionar localmente com instruções reproduzíveis.

## 7. Abordagens consideradas

### Django tradicional, SQLite e templates próprios — escolhida

Oferece autenticação, ORM, migrations, formulários, validações, testes e organização estrutural em um único projeto. Reduz dependências e mantém backend e frontend fáceis de executar e explicar.

### Flask, SQLAlchemy e templates

Seria mais minimalista, mas exigiria decisões e implementações manuais para autenticação, permissões, formulários e estrutura. A aparente simplicidade inicial aumentaria o trabalho repetitivo.

### Django REST Framework e React

Separaria backend e frontend, porém adicionaria API, autenticação por token, Node.js e dois ambientes de desenvolvimento. O aumento de complexidade não oferece benefício proporcional para o escopo acadêmico.

## 8. Arquitetura

A aplicação utilizará uma arquitetura monolítica modular, baseada no padrão Model–Template–View do Django:

- **Apresentação:** templates, componentes HTML, CSS e JavaScript.
- **Aplicação:** views, formulários, serviços e regras de permissão.
- **Domínio e persistência:** models Django, validações e banco relacional.

Apps propostos:

- `core`: dashboard, navegação e utilidades compartilhadas.
- `accounts`: usuários, perfis e permissões.
- `customers`: clientes e veículos.
- `services`: ordens de serviço, avarias, diagnósticos, peças utilizadas e histórico.
- `reports`: filtros, CSV e PDF.

Regras de negócio que não pertencem diretamente à apresentação ficarão em módulos `services.py` ou métodos de domínio pequenos e documentados. Não será criada uma camada abstrata excessiva de repositórios, pois o ORM do Django já atende ao escopo.

## 9. Modelo de dados proposto

### User

Usuário nativo do Django, associado a grupos de permissão: Administrador, Atendente ou Mecânico.

### Customer

- nome
- CPF ou CNPJ opcional
- telefone
- e-mail opcional
- endereço opcional
- observações
- criado_em
- atualizado_em

### Vehicle

- proprietário (`Customer`)
- placa única
- marca
- modelo
- ano
- cor opcional
- quilometragem
- chassi opcional
- observações
- criado_em
- atualizado_em

### ServiceOrder

- veículo (`Vehicle`)
- responsável técnico (`User`, opcional)
- atendente responsável (`User`)
- número sequencial
- data de abertura
- previsão de entrega opcional
- status
- quilometragem de entrada
- reclamação do cliente
- observações gerais
- valor estimado
- valor final opcional
- data de conclusão opcional

Status propostos:

1. `ABERTA`
2. `AGUARDANDO_DIAGNOSTICO`
3. `AGUARDANDO_PECAS`
4. `EM_MANUTENCAO`
5. `PRONTA_ENTREGA`
6. `ENTREGUE`
7. `CANCELADA`

A interface destacará especialmente os três estados pedidos: aguardando peças, em manutenção e pronta para entrega.

### Damage

- ordem de serviço (`ServiceOrder`)
- título ou componente afetado
- descrição do sintoma
- diagnóstico
- causa confirmada opcional
- gravidade
- resolvida
- criado_em
- atualizado_em

### CauseSuggestion

- termo ou categoria da avaria
- possível causa
- explicação curta
- prioridade

### Part

- nome
- código opcional
- descrição opcional
- quantidade em estoque opcional
- valor unitário opcional
- ativo

O controle de estoque será simples e auxiliar, não um módulo de compras completo.

### DamagePartSuggestion

Relaciona uma sugestão de causa ou categoria de avaria a peças possivelmente relacionadas.

### ServicePart

- ordem de serviço
- avaria opcional
- peça
- quantidade
- valor unitário registrado no momento do serviço

### MaintenanceRecord

O histórico será derivado principalmente das ordens concluídas/entregues. Uma visão consolidada apresentará data, quilometragem, avarias, diagnóstico, peças, valores e observações. Não será mantida uma cópia redundante sem necessidade.

### StatusHistory

- ordem de serviço
- status anterior
- novo status
- usuário responsável
- data e hora
- observação opcional

Este registro preserva rastreabilidade das mudanças importantes.

## 10. Regras principais

- Uma placa não pode pertencer a dois veículos.
- Uma ordem deve estar associada a um veículo e a um atendente.
- O valor final não pode ser negativo.
- Quantidades de peças devem ser positivas.
- Ordens entregues ou canceladas ficam bloqueadas para alterações técnicas comuns.
- A conclusão exige ao menos um diagnóstico ou observação de serviço.
- Alterações de status geram automaticamente um registro em `StatusHistory`.
- Apenas administradores gerenciam usuários.
- Atendentes não confirmam diagnósticos técnicos nem alteram dados técnicos concluídos.
- Mecânicos não excluem clientes, veículos ou ordens.
- Exclusões de entidades relacionadas serão restritas ou substituídas por desativação quando preservar o histórico for necessário.

### Transições de status

- `ABERTA` → `AGUARDANDO_DIAGNOSTICO` ou `CANCELADA`.
- `AGUARDANDO_DIAGNOSTICO` → `AGUARDANDO_PECAS`, `EM_MANUTENCAO` ou `CANCELADA`.
- `AGUARDANDO_PECAS` → `EM_MANUTENCAO` ou `CANCELADA`.
- `EM_MANUTENCAO` → `AGUARDANDO_PECAS`, `PRONTA_ENTREGA` ou `CANCELADA`.
- `PRONTA_ENTREGA` → `ENTREGUE` ou, quando houver correção necessária, `EM_MANUTENCAO`.
- `ENTREGUE` e `CANCELADA` são estados finais.
- Apenas o administrador pode reabrir uma ordem entregue ou cancelada, informando uma justificativa; a reabertura retorna para `AGUARDANDO_DIAGNOSTICO` e fica registrada no histórico.
- Atendentes podem abrir, cancelar antes do início técnico e marcar uma ordem pronta como entregue.
- Mecânicos podem executar transições técnicas nas ordens atribuídas a eles.
- Administradores podem executar qualquer transição válida.

### Escopo do mecânico

O mecânico poderá consultar o cadastro básico e o histórico técnico de todos os veículos, pois essas informações apoiam diagnósticos. Entretanto, somente poderá editar dados técnicos e alterar status de ordens atribuídas a ele. Ordens não atribuídas permanecerão em modo de consulta.

### Numeração das ordens

O número público seguirá o formato `BB-AAAA-NNNN`, com sequência reiniciada a cada ano. A geração ocorrerá no servidor dentro de transação e terá restrição de unicidade no banco. O identificador interno continuará sendo a chave primária padrão do Django.

### Exclusão e desativação

- Clientes e veículos com histórico não serão excluídos; poderão ser marcados como inativos.
- Peças já utilizadas não serão excluídas; poderão ser desativadas.
- Usuários serão desativados para preservar autoria e auditoria.
- Ordens de serviço e registros técnicos não terão exclusão comum pela interface.
- Registros sem qualquer relacionamento histórico, criados por engano, poderão ser excluídos por administradores quando isso não quebrar integridade referencial.

## 11. Sugestões de causas e peças

O recurso será determinístico e explicável. Ao registrar uma avaria, o sistema buscará correspondências por categoria ou palavras-chave em uma base cadastrada de sugestões. Também poderá ordenar sugestões pela frequência de causas confirmadas em avarias semelhantes.

Exemplo:

- Sintoma/categoria: “motor superaquecendo”.
- Causas sugeridas: baixo nível de líquido, válvula termostática, ventoinha, bomba d'água.
- Peças relacionadas: válvula termostática, sensor de temperatura, bomba d'água.

A interface deixará claro que são sugestões de apoio, não diagnósticos automáticos.

Cada avaria terá uma categoria estruturada e poderá referenciar uma sugestão cadastrada como causa confirmada, mantendo também um campo textual opcional para diagnósticos não previstos. As sugestões compatíveis serão ordenadas primeiro pela prioridade cadastrada e depois pela frequência de confirmação em avarias da mesma categoria. Esse comportamento fará parte da primeira versão e será coberto por testes.

O campo de quantidade em estoque de `Part` será apenas informativo nesta versão. O registro de uma peça em uma ordem não fará movimentação automática de estoque. Essa limitação será exibida e documentada claramente, evitando introduzir um subsistema transacional de compras e estoque fora do objetivo central.

## 12. Telas e fluxos

### Login

Tela direta com identidade Box Box, campo de usuário, senha e credenciais demonstrativas documentadas.

### Dashboard

Superfície principal do tipo **Monitor/Operate**, sem hero promocional. Mostrará:

- ordens que exigem atenção;
- colunas ou listas por status operacional;
- busca rápida por placa, cliente ou número da ordem;
- ações para abrir ordem, cadastrar cliente e cadastrar veículo;
- contagens operacionais discretas e baseadas em dados reais.

### Clientes

- listagem pesquisável;
- cadastro e edição;
- detalhe com veículos associados;
- proteção contra exclusão destrutiva quando houver histórico.

### Veículos

- listagem e filtros;
- cadastro e edição;
- detalhe com proprietário, ordens abertas e histórico completo;
- acesso rápido para abrir nova ordem.

### Ordens de serviço

- lista com busca e filtros por status, período, veículo e responsável;
- criação guiada;
- detalhe dividido em resumo, avarias, diagnóstico, peças, valores e histórico de status;
- avarias em painéis expansíveis acionados por setas;
- atualização de status conforme permissões e regras.

### Relatórios

- filtro por período e status;
- ordens abertas e concluídas;
- serviços por veículo/cliente;
- peças utilizadas;
- exportação CSV e PDF.

### Usuários

Área exclusiva do administrador para criação, ativação, desativação e atribuição de perfil.

## 13. Direção visual

A interface será original, inspirada na precisão e sobriedade de produtos automotivos modernos, sem copiar telas ou identidade de Tesla, Nissan ou Toyota.

- Fundo grafite quase preto, com superfícies pouco mais claras.
- Tipografia sans-serif precisa e legível; monoespaçada apenas para placas, números de ordem e pequenos rótulos técnicos.
- Um único acento principal, vermelho automotivo contido.
- Verde, âmbar, azul e vermelho reservados para estados semânticos.
- Cards com raio discreto, bordas finas e sem glassmorphism.
- Ícones lineares somente onde acelerarem a leitura.
- Hierarquia por tipografia, espaçamento e alinhamento antes de caixas decorativas.
- Navegação lateral no desktop e menu compacto no mobile.
- Tabelas responsivas e formulários divididos por assunto.
- Estados vazios e mensagens de erro úteis.
- Animações curtas apenas para expansão, feedback e mudança de estado.
- Respeito a `prefers-reduced-motion`.

## 14. Tratamento de erros

- Validação no servidor por meio de forms e models Django.
- Mensagens específicas junto aos campos inválidos.
- Páginas próprias para 403, 404 e 500.
- Operações de múltiplas gravações importantes dentro de transações.
- Erros de exportação apresentados sem corromper dados operacionais.

## 15. Testes

### Unitários

- validações de placa, valores e quantidades;
- transições de status;
- bloqueio de edição em ordens finalizadas;
- mecanismo de sugestão;
- permissões por perfil.

### Integração

- persistência das relações cliente–veículo–ordem–avaria;
- registro automático do histórico de status;
- peças associadas a ordens;
- filtros e exportações consultando o banco.

### Funcionais/aceitação

- login com cada perfil;
- cadastrar cliente e veículo;
- abrir ordem e registrar avaria;
- atribuir mecânico e avançar status;
- registrar diagnóstico e peças;
- concluir e entregar serviço;
- consultar histórico do veículo;
- exportar relatório.

### Regressão

Uma suíte automatizada será executada após alterações. Os fluxos críticos também serão documentados para teste manual de apresentação.

## 16. Documentação acadêmica e técnica

O repositório conterá:

- `README.md` com instalação e execução completa;
- requisitos funcionais e não funcionais;
- regras de negócio e critérios de aceite;
- descrição da metodologia de desenvolvimento;
- arquitetura e decisões técnicas;
- modelo relacional e dicionário de dados;
- diagramas UML de casos de uso, classes e sequência/atividade;
- plano e resultados dos testes;
- limitações conhecidas;
- scripts e migrations do banco;
- dados demonstrativos opcionais por comando de seed.

## 17. Execução e implantação acadêmica

Fluxo esperado:

1. Clonar o repositório.
2. Criar e ativar ambiente virtual.
3. Instalar `requirements.txt`.
4. Copiar/configurar variáveis de ambiente mínimas, se aplicável.
5. Executar migrations.
6. Carregar dados demonstrativos por comando documentado.
7. Iniciar o servidor Django.
8. Entrar com credenciais de demonstração.
9. Executar a suíte de testes.

O projeto não dependerá de caminhos absolutos. O banco SQLite de desenvolvimento poderá ser criado pelas migrations, com dados demonstrativos gerados por comando reproduzível.

## 18. Critérios de aceite

- Login e autorização funcionam para os três perfis.
- Clientes e veículos podem ser cadastrados, consultados e editados.
- Veículos permanecem corretamente associados aos proprietários.
- Ordens são abertas e percorrem estados válidos.
- Avarias, diagnósticos e peças podem ser registrados.
- Mudanças de status ficam auditadas.
- O histórico de um veículo apresenta serviços anteriores.
- Sugestões de causas e peças são exibidas de forma explicável.
- Relatórios podem ser filtrados e exportados em CSV e PDF.
- Dados persistem no banco relacional.
- Testes automatizados críticos passam.
- O sistema funciona em desktop e mobile.
- Outra pessoa consegue instalar, executar e testar o projeto seguindo somente o README.

## 19. Decisões deixadas ao implementador

- Escolha de biblioteca leve de ícones, preferindo arquivos locais ou SVGs simples.
- Biblioteca específica para PDF, desde que pequena, documentada e estável.
- Detalhes exatos dos breakpoints responsivos.
- Organização interna de pequenos componentes de template.
- Quantidade e conteúdo dos dados de demonstração, mantendo-os coerentes e claramente fictícios.
