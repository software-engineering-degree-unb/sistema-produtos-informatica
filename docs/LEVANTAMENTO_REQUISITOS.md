# Levantamento de Requisitos — Sistema de Produtos de Informática

## 1. Introdução

Este documento apresenta o levantamento de requisitos do **Sistema de Produtos
de Informática**, uma aplicação web para gerenciamento de produtos, usuários,
vendas e relatórios.

O sistema foi originalmente escrito em Python (FastAPI), com banco de dados 
relacional MySQL/MariaDB e o front-end em HTML/CSS/JS vanilla.

## 2. Objetivo

Consolidar, em um único documento, os requisitos funcionais e não funcionais
do sistema, servindo como referência para manutenção, avaliação acadêmica e
evolução do projeto.

## 3. Visão geral do sistema

Aplicação web monolítica, com renderização server-side (Jinja2), acesso a
dados via SQL puro (sem ORM) e persistência em MySQL/MariaDB. A sessão do
usuário é mantida inteiramente em cookie assinado (stateless no servidor).

### 3.1 Perfis de usuário (atores)

| Perfil | Código interno | Descrição |
|---|---|---|
| **Administrador** | `idTipoLogin = 2` | Acesso completo: gestão de produtos, usuários, relatórios de vendas e históricos de auditoria. |
| **Usuário comum** | `idTipoLogin = 1` | Acesso restrito: navegação de produtos, finalização de compras e consulta ao próprio histórico de compras/perfil. |



### 4. Requisitos Funcionais

**4.1 Cadastro e gerenciamento de usuários**

| ID | Requisito |
| --- | --- |
| RF01 | O sistema deve permitir o cadastro de usuários, incluindo dados pessoais, endereço e credenciais de acesso. |
| RF02 | O sistema deve permitir a consulta dos usuários cadastrados. |
| RF03 | O sistema deve permitir a busca de usuários por nome ou documento e por situação cadastral. |
| RF04 | O sistema deve permitir a visualização dos dados completos de um usuário, incluindo seus dados pessoais, endereço e informações de acesso. |
| RF05 | O sistema deve permitir a edição dos dados cadastrais, endereço e credenciais de um usuário. |
| RF06 | O sistema deve permitir que usuários autenticados consultem seus próprios dados de perfil. |

**4.2 Cadastro e gerenciamento de produtos**

| ID | Requisito |
| --- | --- |
| RF07 | O sistema deve permitir o cadastro de produtos, incluindo nome, descrição, valor, categoria, visibilidade e imagens. |
| RF08 | O sistema deve permitir a consulta dos produtos cadastrados. |
| RF09 | O sistema deve permitir a pesquisa e filtragem de produtos por nome, descrição, código, categoria e visibilidade. |
| RF10 | O sistema deve permitir a edição dos dados cadastrais de produtos. |
| RF11 | O sistema deve permitir a inclusão e remoção de imagens associadas aos produtos. |
| RF12 | O sistema deve permitir a exclusão de produtos. |
| RF13 | O sistema deve permitir o cadastro de categorias de produtos. |
| RF14 | O sistema deve permitir a consulta das categorias e dos valores de visibilidade disponíveis para os produtos. |

**4.3 Operações de compras e vendas**

| ID | Requisito |
| --- | --- |
| RF15 | O sistema deve permitir que usuários realizem compras de produtos disponíveis no catálogo. |
| RF16 | O sistema deve permitir a inclusão de produtos e respectivas quantidades em uma compra. |
| RF17 | O sistema deve registrar as compras realizadas e seus respectivos itens. |
| RF18 | O sistema deve permitir que o usuário consulte seu histórico de compras. |
| RF19 | O sistema deve permitir a consulta dos detalhes de uma compra, incluindo os produtos e quantidades adquiridos. |

**4.4 Relatórios e consultas gerenciais**

| ID | Requisito |
| --- | --- |
| RF20 | O sistema deve disponibilizar um relatório geral das vendas realizadas. |
| RF21 | O sistema deve permitir a filtragem do relatório geral de vendas por período, usuário e faixa de valor. |
| RF22 | O sistema deve disponibilizar um relatório de vendas agrupado por mês. |
| RF23 | O sistema deve disponibilizar um relatório de vendas por cliente. |
| RF24 | O sistema deve permitir a ordenação do relatório de clientes por valor gasto ou quantidade de compras. |
| RF25 | O sistema deve disponibilizar informações sobre os produtos mais comprados por cada cliente apresentado no relatório. |
| RF26 | O sistema deve disponibilizar um relatório de vendas por canal de venda. |
| RF27 | O sistema deve permitir a filtragem dos relatórios de vendas por período e, quando aplicável, por cliente ou canal de venda. |

**4.5 Histórico e auditoria**

Aqui eu manteria como funcional, porque existe uma funcionalidade efetiva de consulta do histórico pelo administrador:

| ID | Requisito |
| --- | --- |
| RF28 | O sistema deve disponibilizar a consulta do histórico de acessos ao sistema. |
| RF29 | O sistema deve disponibilizar a consulta do histórico de alterações realizadas nos dados cadastrais dos usuários. |
| RF30 | O sistema deve permitir a filtragem do histórico de alterações por período e tipo de operação. |



## 5. Requisitos Não Funcionais (RNF)

### 5.1 Tecnologia e arquitetura

| ID | Requisito |
| --- | --- |
| RNF01 | O sistema deve ser implementado utilizando Python 3.13. |
| RNF02 | O sistema deve utilizar o framework FastAPI para implementação das rotas e serviços web. |
| RNF03 | O sistema deve utilizar Uvicorn como servidor ASGI para execução da aplicação. |
| RNF04 | O sistema deve utilizar arquitetura monolítica, mantendo os componentes da aplicação em uma única unidade de execução. |
| RNF05 | O sistema deve organizar sua estrutura de software segundo uma adaptação do padrão MVC, separando Controllers, Models, Views e funções de responsabilidade transversal. |
| RNF06 | A camada de apresentação deve utilizar Jinja2 para renderização server-side das páginas HTML. |
| RNF07 | A aplicação deve manter separação entre a lógica de apresentação, controle das requisições e acesso aos dados. |

### 5.2 Banco de dados e persistência

| ID | Requisito |
| --- | --- |
| RNF08 | O sistema deve utilizar MySQL ou MariaDB como sistema gerenciador de banco de dados relacional. |
| RNF09 | O acesso ao banco de dados deve ser realizado por meio do driver PyMySQL. |
| RNF10 | O sistema não deve depender de um framework ORM para acesso aos dados. |
| RNF11 | As operações de acesso ao banco devem utilizar consultas SQL parametrizadas, evitando a concatenação direta de valores fornecidos pelo usuário nas consultas. |
| RNF12 | As conexões com o banco devem utilizar cursores que permitam o acesso aos resultados por nome de campo. |
| RNF13 | As conexões de banco devem utilizar controle explícito de transações, com confirmação (`commit`) ou reversão (`rollback`) das operações de escrita. |
| RNF14 | Operações que envolvam múltiplas alterações relacionadas ao banco de dados devem preservar a atomicidade da transação. |
| RNF15 | O sistema deve fechar as conexões de banco ao final de cada requisição, inclusive em situações de erro. |
| RNF16 | O schema do banco deve poder ser criado de forma idempotente, sem provocar erro quando tabelas já existentes forem processadas novamente. |
| RNF17 | O sistema deve manter compatibilidade com o schema relacional herdado do sistema original em PHP. |
| RNF18 | O sistema deve funcionar sem necessidade de alteração do código-fonte quando executado em diferentes ambientes de banco, utilizando configurações externas. |

### 5.3 Segurança e autenticação

| ID | Requisito |
| --- | --- |
| RNF19 | As senhas dos usuários devem ser armazenadas exclusivamente na forma de hash criptográfico utilizando bcrypt. |
| RNF20 | O processo de geração das senhas deve utilizar custo bcrypt 10. |
| RNF21 | A verificação das credenciais deve utilizar o mecanismo de comparação fornecido pelo bcrypt, sem comparação direta de senhas em texto puro. |
| RNF22 | O gerenciamento da sessão deve utilizar cookies assinados. |
| RNF23 | A chave utilizada para assinatura das sessões deve ser configurável externamente por meio da variável `SECRET_KEY`. |
| RNF24 | O sistema deve permitir a configuração do tempo máximo de inatividade da sessão por meio da variável `SESSION_TIMEOUT`. |
| RNF25 | A aplicação deve utilizar política `SameSite=Lax` para o cookie de sessão. |
| RNF26 | O sistema não deve depender de uma tabela de sessões no banco de dados para manutenção do estado da sessão. |
| RNF27 | As credenciais de acesso ao banco de dados devem ser configuráveis por variáveis de ambiente. |
| RNF28 | Credenciais padrão ou chaves de desenvolvimento não devem ser utilizadas em ambiente de produção. |

### 5.4 Controle de acesso

| ID | Requisito |
| --- | --- |
| RNF29 | O sistema deve possuir mecanismo de controle de acesso baseado nos papéis definidos para os usuários. |
| RNF30 | O mecanismo de autorização deve diferenciar os perfis Administrador e Usuário Comum. |
| RNF31 | As rotas que exigem autenticação devem validar a existência de uma sessão válida antes de executar suas operações. |
| RNF32 | As rotas administrativas devem possuir verificação específica de autorização. |
| RNF33 | As rotas destinadas ao usuário comum devem possuir verificação específica de autorização. |
| RNF34 | O mecanismo de controle de acesso deve considerar o timeout configurado para a sessão. |

### 5.5 Configuração e gerenciamento de ambiente

| ID | Requisito |
| --- | --- |
| RNF35 | As configurações específicas do ambiente devem ser externas ao código-fonte da aplicação. |
| RNF36 | O sistema deve permitir a configuração do endereço do banco por meio de variáveis de ambiente. |
| RNF37 | O sistema deve permitir a configuração da porta do banco por meio de variável de ambiente. |
| RNF38 | O sistema deve permitir a configuração do nome do banco por meio de variável de ambiente. |
| RNF39 | O sistema deve permitir a configuração das credenciais do banco por meio de variáveis de ambiente. |
| RNF40 | O sistema deve permitir a configuração da chave de assinatura da sessão por meio de variável de ambiente. |
| RNF41 | O sistema deve permitir a configuração do timeout da sessão por meio de variável de ambiente. |
| RNF42 | O sistema deve permitir a ativação ou desativação da geração automática de dados fictícios por meio da variável `GENERATE_DATA`. |
| RNF43 | A mesma base de código deve poder ser executada localmente ou em ambiente Docker por meio de diferentes configurações de ambiente. |

### 5.6 Tratamento de erros e resiliência

| ID | Requisito |
| --- | --- |
| RNF44 | O sistema deve tratar falhas de acesso a dados sem permitir que erros de consultas isoladas interrompam necessariamente a renderização das páginas de consulta e relatórios. |
| RNF45 | Métodos de leitura e geração de relatórios devem retornar estruturas válidas mesmo quando ocorrer uma falha na consulta. |
| RNF46 | Erros ocorridos durante operações transacionais devem provocar rollback antes do encerramento da operação. |
| RNF47 | Falhas de infraestrutura e acesso a dados devem ser registradas em log para permitir diagnóstico posterior. |
| RNF48 | Erros esperados relacionados a autenticação, autorização e expiração de sessão devem ser tratados por mecanismos de redirecionamento apropriados. |
| RNF49 | O sistema deve possuir tratamento global para a exceção utilizada para redirecionamentos de fluxo. |

### 5.7 Interface e apresentação

| ID | Requisito |
| --- | --- |
| RNF50 | A interface web deve utilizar HTML, CSS e JavaScript. |
| RNF51 | O front-end deve utilizar JavaScript vanilla, sem dependência de framework SPA. |
| RNF52 | O front-end não deve depender de etapa de build ou bundler para execução. |
| RNF53 | Os arquivos JavaScript específicos das páginas devem poder ser carregados diretamente pelas respectivas views. |
| RNF54 | Os arquivos estáticos, incluindo CSS, JavaScript e imagens, devem ser disponibilizados diretamente pela aplicação, sem processamento pelo mecanismo de templates. |
| RNF55 | Os valores monetários apresentados na interface devem utilizar a formatação brasileira. |
| RNF56 | Os valores numéricos apresentados na interface devem utilizar a formatação brasileira. |
| RNF57 | As datas apresentadas na interface devem utilizar o formato `dd/mm/aaaa`. |
| RNF58 | Os documentos apresentados na interface devem utilizar máscaras adequadas ao tipo de documento. |

### 5.8 Containerização e implantação

| ID | Requisito |
| --- | --- |
| RNF59 | O sistema deve ser executável por meio de Docker. |
| RNF60 | O ambiente Docker deve ser orquestrado utilizando Docker Compose. |
| RNF61 | O ambiente Docker deve possuir um container destinado à aplicação e outro destinado ao banco de dados. |
| RNF62 | O container da aplicação deve utilizar uma imagem baseada em Python 3.13. |
| RNF63 | A inicialização da aplicação deve aguardar o banco de dados estar disponível antes de executar as operações dependentes do banco. |
| RNF64 | O banco de dados deve possuir mecanismo de health check para indicar sua disponibilidade. |
| RNF65 | O processo de inicialização deve permitir a criação do schema e a população dos dados iniciais antes da inicialização do servidor da aplicação. |
| RNF66 | A geração de dados fictícios para os relatórios deve poder ser habilitada ou desabilitada durante a inicialização do ambiente. |
| RNF67 | O sistema deve manter o mesmo código de aplicação entre execução local e execução em containers. |

### 5.9 Manutenibilidade e organização do código

| ID | Requisito |
| --- | --- |
| RNF68 | O código deve manter separação entre as responsabilidades de roteamento, acesso a dados, apresentação, configuração e funções transversais. |
| RNF69 | As classes de acesso a dados devem receber a conexão de banco por injeção de dependência, evitando a criação direta da conexão dentro de cada Model. |
| RNF70 | Os Models devem encapsular as consultas SQL relacionadas aos seus respectivos domínios de dados. |
| RNF71 | As Views devem concentrar a apresentação dos dados, evitando a implementação de regras de negócio complexas nos templates. |
| RNF72 | A configuração da aplicação deve ser centralizada no módulo de configurações. |
| RNF73 | As funções de formatação utilizadas pelos templates devem ser centralizadas e reutilizáveis. |
| RNF74 | O schema inicial do banco deve ser criado por script próprio e idempotente. |
| RNF75 | Os scripts de preparação, população e geração de dados devem permanecer separados da lógica de execução da aplicação. |

### 5.10 Auditoria e rastreabilidade técnica

| ID | Requisito |
| --- | --- |
| RNF76 | O sistema deve manter registros técnicos das operações de autenticação realizadas pelos usuários. |
| RNF77 | Os registros de autenticação devem permitir identificar o endereço IP associado à requisição. |
| RNF78 | Os registros de autenticação devem armazenar o User-Agent informado pelo cliente. |
| RNF79 | Os registros de autenticação devem armazenar informações adicionais sobre o resultado ou motivo da operação. |
| RNF80 | As alterações cadastrais realizadas por usuários administrativos devem possuir informações suficientes para identificar o responsável pela alteração. |
| RNF81 | O mecanismo de auditoria de alterações deve permitir registrar os valores anterior e posterior de um campo alterado. |

### 5.11 Compatibilidade operacional

| ID | Requisito |
| --- | --- |
| RNF82 | O sistema deve permanecer compatível com o banco de dados utilizado pela versão original do sistema desenvolvido em PHP. |
| RNF83 | A migração para Python/FastAPI não deve exigir a adoção de ORM para acesso ao banco existente. |
| RNF84 | O sistema deve preservar o comportamento das consultas e operações que dependem do schema existente, especialmente aquelas utilizadas pelos relatórios. |
| RNF85 | A aplicação deve poder ser executada em ambiente local com Python e banco MySQL/MariaDB acessível, sem necessidade de alteração do código-fonte. |
| RNF86 | A aplicação deve poder ser executada em ambiente Docker Compose sem necessidade de alteração do código-fonte. |

### 5.12 Inicialização e dados de suporte

| ID | Requisito |
| --- | --- |
| RNF87 | O sistema deve disponibilizar script para criação do banco e das tabelas necessárias à aplicação. |
| RNF88 | O sistema deve disponibilizar script para população dos dados iniciais de referência e usuários. |
| RNF89 | O sistema deve disponibilizar mecanismo para geração de dados fictícios utilizados pelos relatórios. |
| RNF90 | A execução dos scripts de inicialização deve poder ocorrer de forma repetida sem provocar inconsistências decorrentes da criação duplicada do schema. |



## 6. Regras de Negócio (RN)

### 6.1 Regras de usuários e acesso

| ID | Regra |
| --- | --- |
| RN01 | Somente usuários que possuam registro de login ativo e estejam com situação cadastral ativa podem realizar autenticação no sistema. |
| RN02 | O sistema deve reconhecer dois tipos de usuário: Administrador (`idTipoLogin = 2`) e Usuário Comum (`idTipoLogin = 1`). |
| RN03 | O Administrador possui acesso às funcionalidades administrativas de gerenciamento de usuários, produtos, relatórios e históricos. |
| RN04 | O Usuário Comum possui acesso às funcionalidades destinadas à consulta de produtos, realização de compras, consulta de suas compras e consulta de seu próprio perfil. |
| RN05 | Um Usuário Comum não pode acessar funcionalidades administrativas destinadas exclusivamente ao Administrador. |
| RN06 | Um Usuário Comum somente pode consultar informações relacionadas às suas próprias compras. |
| RN07 | Um usuário autenticado pode consultar seus próprios dados cadastrais e de perfil. |

### 6.2 Regras de cadastro de usuários

| ID | Regra |
| --- | --- |
| RN08 | O cadastro de um usuário deve compreender os dados cadastrais, endereço e credenciais de acesso correspondentes. |
| RN09 | A criação de um usuário deve registrar os dados relacionados ao usuário, endereço e login de forma consistente. |
| RN10 | A senha de um novo usuário deve ser armazenada somente após aplicação do mecanismo de hash definido pelo sistema. |
| RN11 | Ao editar um usuário, a senha existente deve ser preservada quando nenhuma nova senha for informada. |
| RN12 | Quando uma nova senha for informada durante a edição, somente a nova senha deve substituir a credencial anteriormente armazenada. |
| RN13 | A alteração de dados de usuário deve registrar auditoria somente para os campos cujo valor tenha efetivamente sido alterado. |
| RN14 | A criação de um usuário deve gerar os registros de auditoria correspondentes aos dados cadastrados. |
| RN15 | Uma falha durante qualquer etapa da criação ou edição de um usuário deve impedir que apenas parte da operação seja persistida. |

### 6.3 Regras de produtos

| ID | Regra |
| --- | --- |
| RN16 | Todo produto deve possuir as informações necessárias ao seu cadastro, incluindo nome, descrição, valor, categoria e visibilidade. |
| RN17 | Um produto pode possuir uma ou mais imagens associadas. |
| RN18 | Quando nenhum arquivo de imagem for informado no cadastro de um produto, o sistema deve associar automaticamente uma imagem padrão ao produto. |
| RN19 | Durante a edição de um produto, o sistema deve permitir a inclusão de novas imagens e a remoção das imagens selecionadas para exclusão. |
| RN20 | A exclusão de um produto deve remover o produto de seu catálogo conforme as regras de persistência estabelecidas pelo sistema. |
| RN21 | Um produto deve estar associado a uma categoria de produto cadastrada no sistema. |
| RN22 | Uma categoria de produto não pode ser cadastrada quando já existir outra categoria com a mesma descrição. |
| RN23 | O produto deve possuir um estado de visibilidade que determine se ele está visível ou oculto no catálogo. |
| RN24 | Os valores monetários informados no formato brasileiro devem ser interpretados corretamente antes de serem armazenados como valores numéricos. |

### 6.4 Regras de compras

| ID | Regra |
| --- | --- |
| RN25 | Uma compra deve estar associada ao usuário que realizou a operação. |
| RN26 | Uma compra deve possuir um ou mais itens de produtos e suas respectivas quantidades. |
| RN27 | O valor de cada item da compra deve ser determinado a partir do preço do produto e da quantidade adquirida. |
| RN28 | O valor total da compra deve corresponder à soma dos valores de todos os seus itens. |
| RN29 | O registro da compra e de seus itens deve ser realizado de forma atômica. |
| RN30 | O sistema deve atribuir automaticamente um canal de venda à compra, sem solicitar essa informação ao usuário durante o checkout. |
| RN31 | O canal de venda atribuído à compra deve corresponder a um dos canais de venda disponíveis no sistema. |
| RN32 | O usuário deve poder consultar somente as compras associadas ao seu próprio cadastro quando estiver utilizando as funcionalidades destinadas ao usuário comum. |
| RN33 | Os detalhes de uma compra devem apresentar os produtos associados e suas respectivas quantidades. |

### 6.5 Regras dos relatórios de vendas

| ID | Regra |
| --- | --- |
| RN34 | O relatório geral de vendas deve considerar os filtros selecionados pelo usuário na consulta. |
| RN35 | As estatísticas do relatório geral devem ser calculadas sobre o conjunto completo de resultados correspondente aos filtros, independentemente da paginação da listagem. |
| RN36 | O relatório geral deve disponibilizar, no mínimo, o número total de compras, o valor total das vendas e o valor médio das compras. |
| RN37 | O relatório mensal deve agrupar as vendas de acordo com o mês de realização da compra. |
| RN38 | O relatório mensal deve apresentar os doze meses do ano selecionado, inclusive aqueles que não possuam vendas. |
| RN39 | Os meses sem vendas devem apresentar valor igual a zero no relatório mensal. |
| RN40 | O relatório mensal deve disponibilizar os anos para os quais existem dados de vendas disponíveis no sistema. |
| RN41 | O relatório de clientes deve permitir a classificação dos clientes pelo valor total gasto ou pela quantidade de compras. |
| RN42 | O relatório de clientes deve permitir a aplicação de período de análise. |
| RN43 | O ranking de clientes deve apresentar os produtos mais frequentemente adquiridos por cada cliente considerado no ranking. |
| RN44 | O ranking de clientes deve considerar os três produtos mais frequentes para cada cliente apresentado. |
| RN45 | O percentual de concentração de vendas dos clientes deve representar a participação dos clientes apresentados no ranking em relação ao total geral considerado. |
| RN46 | O relatório de vendas por canal deve agrupar as vendas de acordo com o canal associado a cada compra. |
| RN47 | O relatório de vendas por canal deve permitir a aplicação de filtros de período e de canal específico. |

### 6.6 Regras de auditoria

| ID | Regra |
| --- | --- |
| RN48 | As operações de autenticação devem possuir registro correspondente no histórico de login. |
| RN49 | O histórico de autenticação deve registrar tanto operações bem-sucedidas quanto operações que resultem em falha. |
| RN50 | Uma expiração de sessão deve ser registrada como evento de encerramento da sessão. |
| RN51 | Alterações cadastrais realizadas em usuários e endereços devem possuir registro de auditoria quando houver alteração efetiva dos dados. |
| RN52 | O registro de auditoria de uma alteração deve identificar o usuário responsável pela operação. |
| RN53 | O registro de auditoria deve identificar a tabela e o registro afetado. |
| RN54 | O registro de auditoria deve armazenar o campo alterado, seu valor anterior e seu novo valor. |
| RN55 | Não deve ser criado registro de auditoria para um campo cujo valor permaneceu inalterado. |
| RN56 | O histórico de alterações deve permitir diferenciar operações de inserção e atualização. |

### 6.7 Regras de consistência das operações

| ID | Regra |
| --- | --- |
| RN57 | Operações que envolvam múltiplas entidades relacionadas devem ser concluídas integralmente ou não devem produzir alterações persistidas. |
| RN58 | O cadastro de usuário deve manter consistência entre os registros de usuário, endereço, login e respectivos registros de auditoria. |
| RN59 | A edição de usuário deve manter consistência entre os dados cadastrais, endereço, credenciais e auditoria correspondente. |
| RN60 | O cadastro ou edição de produto deve manter consistência entre os dados do produto e suas imagens associadas. |
| RN61 | O registro de uma compra deve manter consistência entre o registro principal da compra e seus respectivos itens. |
| RN62 | Caso ocorra falha durante uma operação transacional, as alterações realizadas durante aquela operação devem ser desfeitas. |

### 6.8 Regras de apresentação dos dados

| ID | Regra |
| --- | --- |
| RN63 | Valores monetários devem ser apresentados ao usuário utilizando o padrão brasileiro de representação. |
| RN64 | Datas devem ser apresentadas utilizando o padrão brasileiro `dd/mm/aaaa`. |
| RN65 | Números devem ser apresentados utilizando separadores compatíveis com o padrão brasileiro. |
| RN66 | CPF e CNPJ devem ser apresentados utilizando suas respectivas máscaras de identificação. |



## 7. Restrições Técnicas

- Não há utilização de ORM nem de ferramenta de migrations versionada; a evolução de schema é feita via scripts idempotentes.
- Não há pool de conexões: cada requisição abre e fecha sua própria conexão com o banco de dados.
- O controle de acesso por papel é implementado por meio de funções de verificação chamadas manualmente no início de cada rota protegida, e não por injeção de dependência nativa do framework.

## 8. Possíveis Evoluções (fora do escopo atual)

- Migração das funções de controle de sessão para dependências nativas do FastAPI (`Depends`).
- Introdução de pool de conexões ou driver assíncrono de banco de dados.
- Adoção de ferramenta de migrations para versionamento de schema.
- Padronização de endpoints legados (que retornam `success=1`/`error=1`) para respostas JSON consistentes.
