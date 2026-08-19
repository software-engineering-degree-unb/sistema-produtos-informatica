# Classes do Sistema

Este documento cataloga todas as classes do projeto, seu propósito, atributos,
métodos e como elas se relacionam entre si. Ele complementa o `ARCHITECTURE.md`
com um nível de detalhe mais próximo do código.

> Nota sobre nomenclatura: como o projeto não usa um ORM, os "Models" não são
> classes de entidade (não representam uma linha da tabela); são **classes de
> acesso a dados** (data access objects / repositórios) que encapsulam as
> queries relacionadas a um domínio. Cada uma recebe a conexão de banco
> (`db`) no construtor e a mantém como estado de instância.

## 1. Visão geral / diagrama de relacionamento

```
                         ┌─────────────────────┐
                         │   Controllers        │
                         │ (app/controllers/*)  │
                         │  funções de rota,     │
                         │  não são classes      │
                         └──────────┬───────────┘
                                    │ instanciam com Depends(get_db)
        ┌───────────┬───────────┬──┴────────┬────────────┐
        ▼           ▼           ▼           ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  ┌──────────┐
   │  User   │ │  Admin  │ │ Usuario │ │ Produto │  │  Compra  │
   │(login.py)│ │(admin.py)│ │(usuario.py)│(produto.py)│(compra.py)│
   └─────────┘ └─────────┘ └─────────┘ └─────────┘  └──────────┘
        todas recebem `db` (conexão PyMySQL) no __init__

   ┌────────────────────────┐
   │   RedirectException     │  (app/functions/session_timeout.py)
   │   exceção de controle    │  capturada globalmente em main.py
   │   de fluxo (não é Model) │
   └────────────────────────┘
```

Nenhuma dessas classes herda de uma base comum, nem entre si — todas são
independentes, seguindo o princípio de que cada uma representa um domínio de
dados isolado (`usuario`/`login`, `produto`, `compra`). O único
"acoplamento" entre elas é indireto, via Controllers, que às vezes
instanciam mais de um Model na mesma rota (ex.: `admin.py` usa `Admin` e
`Usuario` juntos para montar o contexto de uma página).

## 2. `User` — `app/models/login.py`

Responsável exclusivamente pela **autenticação** (não confundir com a classe
`Usuario`, que trata do CRUD de usuários — ver seção 4).

```python
class User:
    def __init__(self, db): ...
```

| Método | Assinatura | Retorno | Descrição |
|---|---|---|---|
| `authenticate` | `authenticate(self, login)` | `dict \| None` | Busca um login pelo campo `login`, exigindo que tanto o registro de `login` quanto o `usuario` associado estejam com `idSituacaoUsuario = 1` (ativos). Retorna a senha com hash (`senha`), o tipo de login, nome, `idUsuario`, entre outros — usado por `auth.py` para validar a senha com `bcrypt.checkpw` fora da classe. |
| `get_by_id` | `get_by_id(self, id_login)` | `dict \| None` | Busca um login ativo pelo `idLogin`. Usado em contextos onde já se conhece o id de sessão. |

**Usado por:** `app/controllers/auth.py` (rotas `/login`, `/logout`).

**Observação de design:** a validação da senha (`bcrypt.checkpw`) é feita no
*Controller*, não dentro do Model — o Model apenas retorna o hash
armazenado. Isso é uma leve inconsistência em relação ao resto do sistema
(onde `hash_password` fica dentro do Model `Admin`), mas mantém o Model
`User` livre de dependência direta do `bcrypt`.

## 3. `Admin` — `app/models/admin.py`

A classe mais robusta do projeto. Concentra o **CRUD completo de usuários**
(incluindo endereço e credenciais associadas) e a **auditoria de
alterações**. Também expõe uma função de módulo auxiliar, `hash_password`,
usada tanto internamente quanto potencialmente por outros módulos.

```python
BCRYPT_COST = 10

def hash_password(senha): ...   # função de módulo, não é método da classe

class Admin:
    def __init__(self, db): ...
```

| Método | Assinatura | Retorno | Descrição |
|---|---|---|---|
| `get_by_id` | `get_by_id(self, id_login)` | `dict \| None` | Retorna dados combinados de `usuario` + `login` para um administrador específico (`idTipoLogin = 2`). Usado para exibir o nome do admin logado no cabeçalho das páginas administrativas. |
| `get_all_usuarios` | `get_all_usuarios(self)` | `list[dict]` | Lista todos os usuários com seus dados de login (join `usuario` + `login`), sem filtro. |
| `search_usuarios` | `search_usuarios(self, search_type, search_term, status)` | `list[dict]` | Busca usuários filtrando por `nome` ou `documento` (`LIKE`) e por `status` (situação). Monta a query dinamicamente concatenando cláusulas `AND` conforme os parâmetros informados. |
| `create_usuario` | `create_usuario(self, data, id_login_alterador)` | `int \| False` | Cria um novo usuário em **transação**: insere em `usuario`, `endereco` e `login` (com senha já hasheada via `hash_password`), e grava múltiplas entradas de auditoria (`_registrar_alteracao`) para cada campo relevante. Retorna o `idUsuario` criado, ou `False` em caso de falha (com rollback). |
| `get_usuario_by_id` | `get_usuario_by_id(self, id_usuario)` | `dict \| None` | Retorna a "visão completa" de um usuário: `usuario` + `login` + `endereco` (LEFT JOIN, pois endereço pode não existir). |
| `update_usuario` | `update_usuario(self, id_usuario, data, id_login_alterador)` | `bool` | Atualiza usuário, endereço (faz `UPDATE` ou `INSERT` conforme o endereço já exista) e login (só reescreve a senha se uma nova senha for informada). Compara valores antigos vs. novos campo a campo e grava auditoria apenas para o que de fato mudou. Tudo dentro de uma transação com rollback em caso de erro. |
| `_registrar_alteracao` | `_registrar_alteracao(self, cursor, tabela, operacao, id_registro, campo, valor_antigo, valor_novo, id_login)` | `None` | Método privado (prefixo `_`) que insere uma linha em `historicoAlteracoesUsuario`. Reutilizado por `create_usuario` e `update_usuario`. Recebe o `cursor` já aberto para participar da mesma transação do método chamador. |
| `get_historico_alteracoes_usuario` | `get_historico_alteracoes_usuario(self, data_inicial, data_final, tipo_operacao="")` | `list[dict]` | Consulta o histórico de alterações em um intervalo de datas, opcionalmente filtrado por tipo de operação (`INSERT`/`UPDATE`), fazendo self-join na tabela `login` para identificar tanto o registro alterado quanto quem fez a alteração. |

**Usado por:** `app/controllers/admin.py` (CRUD de usuários e telas de
histórico).

**Relação com outras classes:** `Admin.create_usuario` e
`Admin.update_usuario` chamam a função de módulo `hash_password` (bcrypt,
custo 10) — a única classe do projeto que efetivamente gera hashes de
senha.

## 4. `Usuario` — `app/models/usuario.py`

A menor classe do projeto — deliberadamente enxuta.

```python
class Usuario:
    def __init__(self, db): ...
```

| Método | Assinatura | Retorno | Descrição |
|---|---|---|---|
| `get_by_id` | `get_by_id(self, id_login)` | `dict \| None` | Retorna os dados combinados de `login` + `usuario` para o usuário atualmente logado (qualquer papel). |

**Usado por:** praticamente todos os controllers que precisam exibir dados
do usuário logado no layout (nome no cabeçalho), incluindo `admin.py` e
`profile.py`.

**Diferença em relação a `Admin`:** `Usuario` é agnóstica de papel (serve
tanto para admin quanto para usuário comum) e não tem métodos de
escrita/CRUD — essas responsabilidades ficam em `Admin`, que é quem tem
permissão de gerenciar outros usuários.

## 5. `Produto` — `app/models/produto.py`

Encapsula o catálogo de produtos, incluindo imagens (armazenadas como
`MEDIUMTEXT` em base64 na tabela `imagemProduto`, não em arquivos no
disco/S3) e categorias (`tipoProduto`).

```python
DEFAULT_IMAGE_PATH = ...  # caminho para public/assets/img/no-image.png

class Produto:
    def __init__(self, db): ...
```

| Método | Assinatura | Retorno | Descrição |
|---|---|---|---|
| `search_produtos` | `search_produtos(self, search_term, search_type="geral", tipo_produto=None, visibilidade=None, page=1, items_per_page=10)` | `dict` (`produtos`, `totalItems`, `itemsPerPage`, `currentPage`) | Busca paginada com filtros opcionais por termo (nome/descrição/código), tipo e visibilidade. Para cada produto retornado, faz uma query adicional buscando suas imagens associadas (padrão N+1, aceitável dado o volume esperado). |
| `get_tipos_produto` | `get_tipos_produto(self)` | `list[dict]` | Lista todas as categorias de produto (`tipoProduto`), usada para popular selects nos formulários. |
| `get_visibilidade_produto` | `get_visibilidade_produto(self)` | `list[dict]` | Lista os valores possíveis de visibilidade (`Visível`/`Oculto`). |
| `create_produto` | `create_produto(self, data)` | `bool` (lança exceção em erro) | Cria um produto e suas imagens em transação. Se nenhuma imagem for enviada, usa `_default_image_base64()` para associar uma imagem placeholder. |
| `_default_image_base64` | `_default_image_base64(self)` | `str` | Método privado que lê `no-image.png` do disco e retorna em base64. |
| `add_tipo_produto` | `add_tipo_produto(self, descricao)` | `dict` (`success`, `message`, `id`) | Adiciona uma nova categoria, validando duplicidade antes de inserir. Retorna um dict de resultado (não lança exceção), pensado para ser devolvido diretamente como JSON pelo controller. |
| `get_produto_by_id` | `get_produto_by_id(self, id_produto)` | `dict \| None` | Busca um produto e todas as suas imagens associadas. |
| `update_produto` | `update_produto(self, data)` | `bool` | Atualiza os dados do produto, remove imagens marcadas para exclusão (`imagensRemovidas`) e insere novas imagens, tudo em uma transação. |

**Funções auxiliares externas usadas:** `parse_valor_brl` (de
`app/functions/helpers.py`), que converte um valor monetário no formato
brasileiro (`"1.234,56"`) para uma string numérica aceita pelo MySQL antes
de gravar em `valorProduto`.

**Usado por:** `app/controllers/produto.py`.

## 6. `Compra` — `app/models/compra.py`

A classe com a lógica de negócio mais elaborada, responsável por registrar
vendas e gerar todos os relatórios analíticos do sistema.

```python
MESES = {1: "Janeiro", ..., 12: "Dezembro"}  # dicionário de módulo

class Compra:
    def __init__(self, db): ...
```

| Método | Assinatura | Retorno | Descrição |
|---|---|---|---|
| `registrar_compra` | `registrar_compra(self, id_usuario, itens)` | `dict` (`success`, `idCompra` ou `message`) | Registra uma compra e seus itens em transação. Calcula `valorTotal` somando `preço × quantidade` de cada item. Sorteia aleatoriamente um `idCanalVenda` (1 a 4) — simula a origem da venda (loja física, online, marketplace, revendedor), já que o checkout não coleta essa informação do usuário. |
| `listar_compras_usuario` | `listar_compras_usuario(self, id_usuario)` | `list[dict]` | Lista as compras de um usuário específico, com contagem de itens por compra (`GROUP BY`). |
| `get_compra_detalhes` | `get_compra_detalhes(self, id_compra)` | `dict \| None` | Retorna uma compra com todos os seus itens (join com `produto` para nome/código). |
| `listar_todas_compras` | `listar_todas_compras(self, filtros=None)` | `dict` (`compras`, `estatisticas`) | Relatório geral de vendas (visão do admin), com filtros por data, usuário e faixa de valor, paginado. Delega o cálculo de estatísticas agregadas a `_calcular_estatisticas_compras`. |
| `_calcular_estatisticas_compras` | `_calcular_estatisticas_compras(self, filtros=None)` | `dict` | Método privado: calcula total de compras, valor total e valor médio, aplicando os mesmos filtros da listagem (mas sem paginação/GROUP BY, para estatística agregada correta). |
| `get_usuarios_com_compras` | `get_usuarios_com_compras(self)` | `list[dict]` | Lista usuários distintos que já compraram — usado para popular o filtro por cliente no relatório geral. |
| `get_relatorio_mensal` | `get_relatorio_mensal(self, ano=None)` | `dict` | Agrega vendas por mês de um ano (padrão: ano atual). Preenche os 12 meses do ano mesmo os que não tiveram vendas (zerados), garantindo que o front-end sempre receba uma série temporal completa para os gráficos. Também retorna a lista de anos disponíveis no banco. |
| `get_top_clientes` | `get_top_clientes(self, limit=10, order_by="valorTotal", periodo=None)` | `dict` (`clientes`, `estatisticas`, `filtros`) | Ranking dos maiores clientes por valor gasto ou por quantidade de compras, com filtro de período relativo (mês/trimestre/semestre/ano). Para cada cliente do ranking, busca também seus 3 produtos mais frequentes (subquery por cliente). Calcula percentuais de concentração (quanto os "top clientes" representam do total geral). |
| `listar_vendas_por_canal` | `listar_vendas_por_canal(self, filtros=None)` | `dict` (`vendasPorCanal`, `totais`, `canais`) | Agrega vendas por canal de venda (`canalVenda`), com filtro de data e canal específico. |

**Padrão de resiliência:** todos os métodos de leitura/relatório envolvem o
corpo em `try/except`, logam o erro via `logger.error(...)` (logger de
módulo, `logging.getLogger(__name__)`) e retornam uma estrutura "vazia mas
válida" no formato esperado, em vez de deixar a exceção propagar. Isso
evita que uma falha pontual de query quebre a renderização inteira da
página de relatório — a página é exibida com dados zerados/vazios.

**Usado por:** `app/controllers/compra.py` (checkout do usuário comum e
todos os relatórios de vendas do admin).

## 7. `RedirectException` — `app/functions/session_timeout.py`

Não é um Model, mas é a única classe do projeto que representa uma
**exceção customizada com papel arquitetural** (controle de fluxo — ver
`ARCHITECTURE.md`, seção 6.3).

```python
class RedirectException(Exception):
    def __init__(self, url: str):
        self.url = url
```

| Atributo | Tipo | Descrição |
|---|---|---|
| `url` | `str` | URL para a qual o cliente deve ser redirecionado. |

É lançada por `require_login`, `require_admin`, `require_comum` e
`check_session_timeout` (todas funções, não métodos de classe, no mesmo
módulo) sempre que a sessão é inválida, expirada ou sem permissão
suficiente. Capturada globalmente pelo `exception_handler` registrado em
`main.py`, que a converte em um `RedirectResponse` HTTP real.

## 8. Funções relacionadas que não são classes, mas colaboram diretamente

Para completar o entendimento das classes acima, vale registrar as
principais funções "vizinhas" que elas dependem:

| Função | Módulo | Papel |
|---|---|---|
| `hash_password(senha)` | `app/models/admin.py` | Gera hash bcrypt (custo 10). Usada por `Admin.create_usuario`/`update_usuario`. |
| `parse_valor_brl(valor)` | `app/functions/helpers.py` | Converte string monetária BR (`"1.234,56"`) para formato numérico aceito pelo banco. Usada por `Produto`. |
| `format_valor_brl`, `format_int_brl`, `date_brl`, `datetime_brl`, `formatar_cpf`, `formatar_cnpj` | `app/functions/helpers.py` | Filtros Jinja2 registrados em `app/templating.py`, usados nas Views para formatar dados vindos dos Models. |
| `registrar_operacao(db, id_login, tipo_operacao, status, detalhes, request)` | `app/functions/historico.py` | Grava uma entrada em `historicoLogin`. Chamada por `auth.py` e por `check_session_timeout`. Não pertence a nenhuma classe — é uma função utilitária pura de escrita no banco. |
| `get_client_ip(request)` | `app/functions/historico.py` | Extrai o IP real do cliente, respeitando `X-Forwarded-For`. Usada por `registrar_operacao`. |
| `is_logged_in`, `is_admin`, `is_comum` | `app/functions/session.py` | Helpers de leitura de sessão, usados sobretudo nas Views (Jinja2) para exibir/ocultar elementos de UI conforme o papel do usuário. |

## 9. Convenções observadas em todas as classes de Model

1. **Construtor uniforme**: `__init__(self, db)` — toda classe é "stateless"
   além de guardar a conexão; nenhuma mantém cache ou estado de negócio
   entre chamadas.
2. **Cursor como context manager**: `with self.db.cursor() as cursor:`,
   garantindo que o cursor seja fechado mesmo em caso de exceção.
2. **Métodos privados prefixados com `_`**: usados para lógica interna que
   não deve ser chamada de fora da classe (`_registrar_alteracao`,
   `_default_image_base64`, `_calcular_estatisticas_compras`).
3. **Tratamento de erro assimétrico por criticidade**: métodos de
   *escrita* que fazem parte de um fluxo crítico (`create_usuario`,
   `update_usuario`, `update_produto`) fazem `rollback()` e retornam
   `False`/lançam a exceção; métodos de *leitura*/relatório preferem
   retornar uma estrutura vazia válida para não quebrar a renderização da
   página.
4. **Sem validação de tipos/dados dentro do Model**: a validação básica de
   presença de campos é feita no Controller (ex.: `str(form.get(...,
   "")).strip()`); os Models assumem que os dados recebidos em `data` já
   estão nas chaves esperadas.
