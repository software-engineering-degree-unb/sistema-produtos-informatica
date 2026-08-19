# Arquitetura do Sistema de Produtos de Informática

Este documento descreve em detalhes a arquitetura da aplicação, as decisões de
design adotadas e como as diferentes partes do sistema se conectam. Ele serve
como referência para quem for dar manutenção, avaliar (contexto acadêmico) ou
evoluir o projeto.

## 1. Visão geral

O sistema é uma aplicação web monolítica que gerencia produtos de
informática, usuários, compras e relatórios de vendas. Foi originalmente
escrito em **PHP procedural** e posteriormente **portado para Python**,
mantendo o mesmo banco de dados relacional (MySQL/MariaDB) e o front-end
(HTML/CSS/JS) herdados do projeto original. Essa origem explica algumas
características do código — por exemplo, a ausência de um ORM e o uso de SQL
"cru" (raw SQL) em todos os pontos de acesso a dados, espelhando fielmente as
consultas que existiam na versão PHP.

A stack atual é:

| Camada | Tecnologia | Papel |
|---|---|---|
| Linguagem | Python 3.13 | Runtime da aplicação |
| Framework web | FastAPI + Uvicorn | Roteamento HTTP, ASGI server |
| Templates | Jinja2 | Renderização server-side (SSR) |
| Banco de dados | MySQL / MariaDB | Persistência relacional |
| Driver de acesso a dados | PyMySQL | Comunicação com o banco (sem ORM) |
| Sessão | Starlette `SessionMiddleware` | Cookie assinado (itsdangerous) |
| Senhas | bcrypt | Hash de credenciais |
| Front-end | HTML + CSS + JavaScript vanilla | Interatividade herdada do PHP |
| Containerização | Docker + Docker Compose | Empacotamento e orquestração |

## 2. Estilo arquitetural: MVC adaptado a um framework de rotas

O projeto segue uma variação do padrão **MVC (Model-View-Controller)**,
comum em frameworks PHP como CodeIgniter/Laravel — o que faz sentido dado o
código de origem. A adaptação para FastAPI (que não é um framework MVC
"nativo", e sim um framework de rotas baseado em funções) foi feita
organizando o código em pastas com responsabilidades equivalentes:

```
app/
├── controllers/   → "C" do MVC: recebem a requisição HTTP, orquestram
│                    models e devolvem uma resposta (HTML ou JSON)
├── models/        → "M" do MVC: acesso a dados e regras de persistência
├── views/         → "V" do MVC: templates Jinja2 renderizados pelos
│                    controllers
├── functions/     → Camada transversal (cross-cutting): sessão,
│                    autorização, histórico/auditoria, formatação
├── config/        → Configuração de ambiente e conexão com banco
├── dependencies.py→ Injeção de dependência (fornece a conexão de banco)
└── templating.py  → Configuração central do Jinja2 e filtros customizados
```

Diferente de um MVC "de livro-texto", aqui:

- **Não há uma classe `Controller` base.** Cada controller é um
  `APIRouter` do FastAPI com funções soltas decoradas por rota
  (`@router.get`, `@router.post`). Isso é o padrão idiomático do FastAPI.
- **Os Models não herdam de uma classe base comum nem usam um ORM
  (SQLAlchemy, Tortoise etc.).** Cada Model é uma classe simples que recebe
  uma conexão PyMySQL no construtor e expõe métodos que executam SQL
  diretamente. Isso foi uma escolha deliberada para manter a portabilidade
  1:1 com as queries do sistema PHP original, facilitando auditoria e
  comparação durante a migração.
- **As Views não têm lógica de apresentação complexa** além de laços,
  condicionais e filtros Jinja2. Toda regra de negócio fica em
  Controllers/Models, mantendo as templates "burras" (dumb templates).

### 2.1 Por que não usar um ORM?

Essa é provavelmente a decisão arquitetural mais visível do projeto. As
razões práticas foram:

1. **Fidelidade à migração**: o banco e as queries já existiam no sistema
   PHP; reescrever tudo com um ORM introduziria risco de divergência de
   comportamento (ex.: joins, agregações e relatórios complexos como
   `vendas/relatorio-mensal` e `vendas/relatorio-clientes`).
2. **Controle total sobre SQL**: relatórios com `GROUP BY`, subqueries e
   agregações estatísticas (ver `Compra.get_top_clientes`,
   `Compra.get_relatorio_mensal`) são mais diretos de escrever e otimizar em
   SQL puro do que via ORM.
3. **Simplicidade de dependências**: PyMySQL é uma dependência leve, sem
   necessidade de migrations framework, mapeamento de metadados, etc.

O trade-off é que o projeto não tem proteção automática contra
inconsistências de schema, não tem migrations versionadas (o schema é criado
via `scripts/setup_database.py`, que roda `CREATE TABLE IF NOT EXISTS`), e a
responsabilidade de escapar valores corretamente recai inteiramente sobre o
uso disciplinado de placeholders `%s` do PyMySQL (que, corretamente, é
seguido em todo o código — não há concatenação de valores de usuário em
SQL).

## 3. Fluxo de uma requisição

O diagrama abaixo ilustra o caminho de uma requisição típica, por exemplo
`GET /produtos`:

```
Cliente (browser)
   │  GET /produtos
   ▼
Uvicorn (ASGI server)
   ▼
FastAPI app (main.py)
   │  1. SessionMiddleware decodifica o cookie de sessão assinado
   ▼
Router correspondente (app/controllers/produto.py)
   │  2. Dependency Injection: Depends(get_db) abre uma conexão PyMySQL
   │  3. require_login(request) valida sessão/timeout (functions/session_timeout.py)
   ▼
Model (app/models/produto.py → classe Produto)
   │  4. Monta e executa SQL (SELECT com filtros, paginação)
   ▼
MySQL/MariaDB
   │  5. Retorna linhas (DictCursor → list[dict])
   ▼
Controller
   │  6. Monta o contexto (dict) para o template
   ▼
Jinja2Templates (app/templating.py)
   │  7. Renderiza app/views/produtos/list.html aplicando filtros
   │     (format_valor_brl, date_brl, formatar_cpf, ...)
   ▼
HTMLResponse
   ▼
Cliente (browser) ── carrega também /assets/js/ListarProduto.js (JS vanilla)
```

Para rotas que retornam **JSON** (ex.: `POST /compra/finalizar`,
`POST /produtos/tipo`), o fluxo é o mesmo, mas o controller devolve um
`JSONResponse`/`dict` em vez de renderizar um template — o front-end
consome isso via `fetch()` nos arquivos em `public/assets/js/`.

## 4. Camada de configuração (`app/config/`)

- **`settings.py`**: lê variáveis de ambiente via `python-dotenv`
  (`load_dotenv()`), com valores padrão sensatos para desenvolvimento local
  (`DB_HOST=localhost`, `SECRET_KEY` fraca de exemplo etc.). Centraliza toda
  configuração — nenhuma outra parte do código lê `os.getenv` diretamente.
- **`database.py`**: expõe `get_connection()`, que cria uma conexão PyMySQL
  nova a cada chamada, configurada com `cursorclass=DictCursor` (para que
  toda query retorne `dict` em vez de tuplas posicionais) e
  `autocommit=False` (transações precisam de commit/rollback explícito —
  ver seção 6).

Essa separação permite que o mesmo código rode tanto localmente (via `.env`)
quanto em container (variáveis definidas no `docker-compose.yml`), sem
nenhuma alteração de código-fonte — apenas troca de ambiente.

## 5. Injeção de dependência (`app/dependencies.py`)

O FastAPI usa seu sistema nativo de **Dependency Injection** para fornecer
conexões de banco aos endpoints:

```python
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
```

Cada endpoint declara `db=Depends(get_db)` na assinatura. O FastAPI executa
o generator, injeta a conexão (`conn`) no controller, e — graças ao
`try/finally` — garante o fechamento da conexão ao final da requisição,
independentemente de sucesso ou exceção. Isso evita vazamento de conexões e
centraliza o ciclo de vida do recurso em um único lugar, seguindo o
princípio de *Separation of Concerns*.

Não há *connection pooling* explícito: cada requisição abre e fecha sua
própria conexão TCP com o MySQL. Para o volume de uso de um sistema
acadêmico isso é aceitável; em produção com tráfego maior, valeria a pena
introduzir um pool (ex.: `DBUtils` ou `aiomysql` com pool assíncrono).

## 6. Autenticação, sessão e autorização

### 6.1 Sessão baseada em cookie assinado

A aplicação usa `starlette.middleware.sessions.SessionMiddleware`,
registrado em `main.py` com uma `SECRET_KEY` (vinda de `settings.py`). Esse
middleware serializa o dicionário `request.session` e o grava em um cookie
assinado (HMAC via `itsdangerous`), com `same_site="lax"`. Não há tabela de
sessões no banco: todo o estado de sessão vive no cookie do cliente, o que
torna a aplicação **stateless no servidor** (facilita escalar
horizontalmente, já que qualquer instância pode validar o cookie sem
precisar de um back-end de sessão compartilhado, como Redis).

Ao logar com sucesso (`POST /login` em `app/controllers/auth.py`), o
controller popula a sessão com:

```python
request.session["loggedin"] = True
request.session["login"] = row["login"]
request.session["id"] = row["idLogin"]
request.session["idTipoLogin"] = row["idTipoLogin"]  # 1=Comum, 2=Administrador
request.session["nome"] = row["nome"]
request.session["idUsuario"] = row["idUsuario"]
```

### 6.2 Controle de acesso por papel (RBAC simples)

O sistema tem dois papéis fixos, definidos pela tabela de referência
`tipoLogin`: **Administrador** (`idTipoLogin=2`) e **Usuário Comum**
(`idTipoLogin=1`). O controle de acesso é feito por funções guard em
`app/functions/session_timeout.py`, chamadas manualmente no início de cada
endpoint protegido:

| Função | Verifica | Ação se falhar |
|---|---|---|
| `require_login(request)` | Sessão ativa + timeout | `RedirectException("/login")` |
| `require_admin(request)` | Login + timeout + `idTipoLogin == 2` | Redireciona para `/produtos?error=unauthorized` |
| `require_comum(request)` | Login + timeout + `idTipoLogin == 1` | Redireciona para `/` |

Essas funções **não são dependências do FastAPI** (não usam `Depends`);
são chamadas de forma imperativa como a primeira linha de cada handler,
seguindo o mesmo padrão que existia no PHP original (checagens no topo de
cada script). Isso é uma diferença notável em relação ao idiomático do
FastAPI (que favoreceria `Depends(require_admin)`), refletindo novamente a
fidelidade à estrutura original durante a migração.

### 6.3 Timeout de sessão e o padrão `RedirectException`

Como as guard functions não podem simplesmente `return` um redirect (elas
são chamadas de dentro do corpo do controller, não são o retorno da rota), o
projeto usa uma exceção customizada para propagar o redirecionamento:

```python
class RedirectException(Exception):
    def __init__(self, url: str):
        self.url = url
```

Ela é capturada globalmente por um exception handler registrado em
`main.py`:

```python
@app.exception_handler(RedirectException)
async def redirect_exception_handler(request, exc):
    return RedirectResponse(url=exc.url)
```

Esse é um uso elegante do sistema de exception handlers do FastAPI para
simular um "early return com side-effect" a partir de qualquer profundidade
de chamada — evita que toda função precise checar e repassar manualmente um
valor de "usuário não autorizado" camada por camada.

O timeout em si (`check_session_timeout`) compara `time.time()` com um
timestamp `LAST_ACTIVITY` gravado na sessão a cada requisição autenticada;
se o intervalo excede `SESSION_TIMEOUT` (padrão 900s = 15 min), a sessão é
limpa, um evento de logout por expiração é registrado no histórico
(`registrar_operacao`), e o usuário é redirecionado com `?timeout=1`.

### 6.4 Hash de senhas

Senhas são armazenadas com **bcrypt** (`bcrypt.hashpw`, custo 10, definido
em `app/models/admin.py`). A verificação no login usa `bcrypt.checkpw`,
protegida por `try/except ValueError` para hashes malformados. Não há
"salt" manual — o bcrypt já embute o salt no próprio hash resultante.

## 7. Auditoria e histórico

O sistema mantém **duas tabelas de auditoria** distintas, refletidas por
funcionalidades separadas na navegação (`/historico/login` e
`/historico/alteracoes`):

1. **`historicoLogin`** — registra tentativas de login/logout (sucesso ou
   falha), IP do cliente (`get_client_ip`, que respeita
   `X-Forwarded-For` quando presente — importante atrás de proxy/load
   balancer), User-Agent e um campo livre de detalhes (ex.: "Senha
   incorreta", "Tempo Expirado"). Gravado pela função
   `registrar_operacao()` em `app/functions/historico.py`, chamada a partir
   de `auth.py` e `session_timeout.py`.

2. **`historicoAlteracoesUsuario`** — registra alterações **campo a
   campo** feitas em usuários e endereços (quem alterou, o que mudou, valor
   antigo vs. novo). Essa lógica vive dentro da própria classe `Admin`
   (método privado `_registrar_alteracao`), chamada explicitamente após
   cada `INSERT`/`UPDATE` em `create_usuario`/`update_usuario`, comparando
   valores antigos e novos campo por campo antes de decidir se grava uma
   entrada de histórico (evita registrar "alterações" quando o valor não
   mudou).

Esse padrão de auditoria granular (uma linha por campo alterado, e não uma
linha por operação) é mais custoso em espaço, mas permite reconstruir o
"diff" exato de qualquer alteração — útil em um sistema que lida com dados
cadastrais sensíveis (documento, endereço, credenciais).

## 8. Camada de dados e transações

Todos os Models seguem o mesmo padrão estrutural:

```python
class NomeDoModel:
    def __init__(self, db):
        self.db = db  # conexão PyMySQL injetada pelo controller

    def algum_metodo(self, ...):
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()  # ou fetchone()
```

Para operações que envolvem múltiplas tabelas (ex.: criar um usuário grava
em `usuario`, `endereco`, `login` e várias linhas de
`historicoAlteracoesUsuario`), os Models usam transações explícitas:

```python
self.db.begin()
try:
    with self.db.cursor() as cursor:
        ...  # múltiplos INSERT/UPDATE
    self.db.commit()
    return True
except Exception:
    self.db.rollback()
    return False
```

Isso garante atomicidade: se qualquer passo falhar (ex.: violação de
constraint), nenhuma escrita parcial fica persistida. Esse padrão aparece em
`Admin.create_usuario`, `Admin.update_usuario`, `Produto.create_produto`,
`Produto.update_produto` e `Compra.registrar_compra`.

## 9. Camada de apresentação (Views + templating)

- Templates Jinja2 ficam em `app/views/`, organizados por domínio
  (`produtos/`, `usuarios/`, `vendas/`, `compras/`, `historico/`,
  `home/`, `auth/`, `profile/`), espelhando a estrutura de Controllers.
- `app/templating.py` centraliza a instância de `Jinja2Templates` e
  registra **filtros customizados** usados nas views, todos implementados
  em `app/functions/helpers.py`:
  - `formatar_cpf` / `formatar_cnpj` — máscaras de documentos brasileiros.
  - `format_valor_brl` / `format_int_brl` — formatação monetária/numérica
    no padrão brasileiro (`1.234,56`).
  - `date_brl` / `datetime_brl` — datas no formato `dd/mm/aaaa`.
  - `tojson_safe` — serialização JSON seguinder para embutir dados Python
    (incluindo `datetime`/`Decimal`) dentro de `<script>` tags nas
    templates, usada pelas páginas que hidratam gráficos/tabelas
    interativas em JS puro.
- Cada rota HTML chama `templates.TemplateResponse(request, "caminho.html",
  {contexto})`, seguindo a assinatura moderna do FastAPI (a partir da
  0.108+), onde `request` é passado como primeiro argumento posicional.

## 10. Front-end

O front-end é **JavaScript vanilla**, um arquivo por página funcional
(`public/assets/js/`), sem framework SPA nem bundler. Cada script é
carregado diretamente pela template correspondente e interage com o back-end
via `fetch()` contra os endpoints JSON (ex.: `CadastrarProduto.js` chama
`POST /produtos/novo`, que retorna texto simples `success=1`/`error=1`, um
formato herdado do PHP original em vez do JSON puro usual do restante da
API). Os arquivos estáticos (CSS/JS/imagens) são servidos via
`StaticFiles`, montados em `/assets` (`app.mount("/assets", ...)` em
`main.py`), sem passar pelo Jinja2.

## 11. Containerização

- **`Dockerfile`**: imagem baseada em `python:3.13-slim`, instala
  dependências, copia o código e define `docker/entrypoint.sh` como
  `ENTRYPOINT`.
- **`docker/entrypoint.sh`**: script de bootstrap executado ao subir o
  container da aplicação — tipicamente aguarda o banco ficar saudável,
  executa `scripts/setup_database.py` (schema), `scripts/seed_data.py`
  (dados de referência/usuários iniciais) e, se `GENERATE_DATA=true`,
  `scripts/generate_data.py` (compras fictícias para popular os
  relatórios), antes de iniciar o Uvicorn.
- **`docker-compose.yml`**: orquestra dois serviços — `db` (MariaDB 11, com
  `healthcheck` via `healthcheck.sh`) e `app` (a aplicação, que só sobe
  após o banco reportar `service_healthy`, evitando race conditions de
  inicialização). Toda a configuração de ambiente é passada por variáveis,
  reaproveitando o mesmo `app/config/settings.py` usado localmente.

Essa separação entre `scripts/` (utilitários de banco, chamados uma vez no
bootstrap ou manualmente) e `app/` (a aplicação em si, que roda
continuamente) é uma boa prática que evita misturar lógica de setup com
lógica de runtime.

## 12. Tratamento de erros

O tratamento de erros no projeto segue duas estratégias, conforme o
contexto:

1. **Erros esperados de fluxo de UI** (usuário não autenticado, sem
   permissão, sessão expirada) → `RedirectException` capturada
   globalmente (seção 6.3).
2. **Erros de infraestrutura/dados** (falha de query, violação de
   constraint) → `try/except Exception` local em cada método de Model,
   com `rollback()` quando há transação aberta, log via
   `logging.getLogger(__name__).error(...)`, e retorno de um valor
   "neutro" (lista vazia, `None`, `{"success": False, ...}`) para que o
   Controller decida como comunicar a falha ao usuário (mensagem de erro
   na URL, JSON de erro etc.), em vez de deixar a exceção subir e gerar um
   HTTP 500 genérico.

## 13. Resumo das decisões arquiteturais e trade-offs

| Decisão | Motivação | Trade-off aceito |
|---|---|---|
| Sem ORM, SQL cru via PyMySQL | Fidelidade à migração do PHP; controle total sobre queries complexas de relatório | Sem migrations versionadas; risco de erro de digitação em SQL não detectado em tempo de desenvolvimento |
| Sessão 100% em cookie assinado | Stateless, fácil de escalar horizontalmente | Cookie cresce com o tamanho da sessão; não é possível invalidar uma sessão específica no servidor sem trocar `SECRET_KEY` (o que invalida todas) |
| Guards chamados manualmente (não `Depends`) | Fidelidade ao padrão de checagem no topo do script do PHP original | Mais fácil esquecer de chamar `require_login`/`require_admin` em uma nova rota do que se fosse obrigatório via assinatura de dependência |
| `RedirectException` + exception handler global | Permite redirecionar de qualquer profundidade de chamada sem `return` explícito em cada camada | Uso de exceções para controle de fluxo (não é um erro real), o que pode confundir quem não conhece o padrão |
| Uma conexão de banco nova por requisição | Simplicidade | Sem pool de conexões — pode não escalar bem sob alta concorrência |
| Auditoria campo a campo | Rastreabilidade granular de alterações cadastrais | Mais linhas gravadas por operação de update |
| JS vanilla por página, sem SPA | Reaproveita front-end herdado do PHP; zero build step | Sem componentização/reuso de UI entre páginas; scripts duplicam padrões (fetch, montagem de tabela) |

## 14. Possíveis evoluções

- Migrar as guard functions de sessão para dependências do FastAPI
  (`Depends(require_admin)`), tornando a proteção de rota explícita na
  assinatura e detectável estaticamente.
- Introduzir um pool de conexões (ex.: `DBUtils.PooledDB` ou migrar para um
  driver assíncrono como `aiomysql`/`asyncmy`) para melhor uso do modelo
  assíncrono do FastAPI (hoje as queries são síncronas e bloqueantes dentro
  de handlers `async def`).
- Adicionar uma ferramenta de migrations (Alembic, ainda que sem SQLAlchemy
  ORM completo, ou um migrator agnóstico) para versionar mudanças de
  schema em vez de `CREATE TABLE IF NOT EXISTS`.
- Padronizar os endpoints "legados" que retornam texto simples
  (`success=1`/`error=1`) para JSON consistente com o restante da API.
