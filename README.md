# Sistema de Produtos de Informática

## Visão geral

Sistema web de gerenciamento de produtos de informática, originalmente escrito em PHP e portado para **Python + FastAPI**, mantendo o mesmo banco MySQL/MariaDB e o front-end (CSS/JS) herdados.

Funcionalidades principais:

- **Autenticação** por sessão assinada (cookie), com papéis de **Administrador** e **Usuário comum**, timeout de sessão configurável e registro de histórico de acessos.
- **Produtos**: listagem com filtros/paginação, cadastro, edição e exclusão, com imagens e categorias (tipos).
- **Usuários**: CRUD de usuários e credenciais (senhas com hash `bcrypt`).
- **Vendas/Compras**: checkout de compras, relatório geral e relatórios de vendas **mensal**, **por cliente** e **por canal de venda**.
- **Históricos**: registro de logins e de alterações feitas por usuários.

### Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.13 |
| Web framework | FastAPI + Uvicorn |
| Templates | Jinja2 (arquitetura MVC) |
| Banco de dados | MySQL / MariaDB |
| Acesso a dados | PyMySQL |
| Sessão | Starlette SessionMiddleware (cookie assinado) |
| Senhas | bcrypt |

## Estrutura do projeto

```
.
├── main.py                  # App FastAPI: middlewares, assets, rotas, tratamento de erros
├── requirements.txt         # Dependências Python
├── .env                     # Configurações de banco, sessão e chave secreta
├── Dockerfile               # Imagem da aplicação
├── docker-compose.yml       # Orquestração (banco + aplicação) em um único comando
├── docker/
│   └── entrypoint.sh        # Inicialização: espera DB, cria schema, seed e gera dados
├── app/
│   ├── config/
│   │   ├── settings.py      # Leitura do .env
│   │   └── database.py      # Conexão PyMySQL
│   ├── controllers/         # Rotas FastAPI (auth, home, admin, produto, compra, profile)
│   ├── models/              # Acesso a dados (login, produto, usuario, compra, admin)
│   ├── functions/           # Sessão, permissões, helpers de formatação, histórico
│   ├── views/               # Templates Jinja2 (produtos, usuarios, vendas, compras, ...)
│   ├── templating.py        # Jinja2 + filtros globais (datas, moeda, CPF/CNPJ)
│   └── dependencies.py      # Injeção de dependência do banco (get_db)
├── scripts/                 # Utilitários Python de banco
│   ├── setup_database.py    # Cria banco + tabelas + dados de referência (idempotente)
│   ├── seed_data.py         # Insere produtos, usuários e credenciais iniciais
│   └── generate_data.py     # Gera compras/vendas fictícias (relatórios)
└── public/
    └── assets/              # CSS, JS e imagens herdados do projeto PHP
```

## Como executar

### Opção 1 — Docker (recomendado, um único comando)

Requer Docker e Docker Compose instalados.

```bash
docker compose up --build
```

A primeira subida cria o banco, as tabelas, popula os dados iniciais e gera compras fictícias automaticamente. Depois, basta acessar:

- **Aplicação:** http://localhost:8080

Para parar:

```bash
docker compose down        # remove os containers (os dados do banco são preservados)
docker compose down -v     # remove também os dados do banco (recria tudo do zero)
```

### Opção 2 — Execução local (Python)

Requisitos: Python 3.13+, um servidor MySQL/MariaDB acessível em `localhost:3306` e um venv com as dependências instaladas.

```bash
# 1) Configurar o banco em .env (host, porta, usuário, senha, nome do banco)

# 2) Criar venv e instalar dependências
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3) Criar banco/tabelas e popular dados
.venv/bin/python scripts/setup_database.py
.venv/bin/python scripts/seed_data.py
.venv/bin/python scripts/generate_data.py   # opcional: gera vendas para os relatórios

# 4) Rodar
.venv/bin/uvicorn main:app --reload --port 8000
```

Acesse **http://localhost:8000** (redireciona para `/login`).

### Credenciais iniciais

| Perfil | Login | Senha |
|---|---|---|
| Administrador | `gerente` | `admin` |
| Administrador | `supervisor` | `admin` |
| Usuário comum | `user3` a `user27` | `admin` |

## Configurações interessantes de se alterar e porquê

Todas as variáveis abaixo ficam no arquivo **`.env`** (execução local) ou no serviço `app` do **`docker-compose.yml`** (Docker).

| Variável | Padrão | O que faz | Por que alterar |
|---|---|---|---|
| `DB_HOST` | `localhost` (Docker: `db`) | Endereço do banco | No Docker deve apontar para o serviço `db`; localmente, para seu MySQL/MariaDB. |
| `DB_PORT` | `3306` | Porta do banco | Altere se o banco rodar em outra porta. |
| `DB_NAME` | `sistema_produtos_informatica` | Nome do banco de dados | Altere para usar outro banco (ex.: um de testes). |
| `DB_USER` / `DB_PASSWORD` | `root` / `root` | Credenciais do banco | **Obrigatório alterar** em produção — nunca use root/senha fraca. |
| `SECRET_KEY` | `altera-esta-chave-em-producao` | Chave que assina o cookie de sessão | **Obrigatório alterar** em produção: quem souber dela pode forjar sessões. Use um valor aleatório e longo (ex.: `openssl rand -hex 32`). |
| `SESSION_TIMEOUT` | `900` | Tempo (s) de inatividade para expirar a sessão | Reduza para maior segurança ou aumente para sessões mais longas. |
| `GENERATE_DATA` | `true` | Gera compras fictícias ao subir com banco vazio | Defina como `false` para não popular os relatórios automaticamente. |
