# Sistema de Loja - Lan House (v3.1.0)

API REST conteinerizada para gerenciar o estoque da lan house 'Taciana Variedades'. Evoluída de um protótipo em SQLite para uma infraestrutura corporativa de alta performance, contando com PostgreSQL, Caching em Memória com Redis, precisão financeira exata, segurança robusta (JWT e RBAC via Cookies HTTP-Only), observabilidade, documentação OpenAPI/Swagger e suíte automatizada de 19 testes via Pytest.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma infraestrutura escalável com PostgreSQL e Docker.

Na **versão 3.1.0**, o projeto consolidou padrões avançados de engenharia de software e resiliência em produção:
* **Integridade Financeira:** Migração dos valores monetários de `Float` para `Numeric(10, 2)` / `Decimal` com validação em dupla camada (Marshmallow + SQLAlchemy `@validates`).
* **Transações Atômicas:** Criação do gerenciador de contexto `atomic_transaction()` garantindo *commit* e *rollback* automáticos em todas as operações de escrita.
* **Abstração de Cache via Decorators:** Implementação dos decorators genéricos `@cache_aside` e `@invalidate_cache`, eliminando código repetido nas rotas e mantendo degradação graciosa se o Redis ficar indisponível.
* **Hardening Docker & Testes de Resiliência:** Execução do container com usuário não-root (`appuser`), *healthchecks* completos e suíte Pytest expandida com testes parametrizados (`@pytest.mark.parametrize`) e simulação de falhas (`unittest.mock.patch`).

## Arquitetura e Tecnologias

A stack foi projetada para simular um ambiente de produção moderno, priorizando separação de responsabilidades, performance e manutenibilidade:

* **Python 3.12 + Flask:** Motor base alinhado ao padrão *Application Factory*, isolando rotas, modelos e lógica de testes.
* **Arquitetura Modularizada:** Divisão clara do núcleo em `app/core/` (configurações de cache, logging estruturado e Swagger) e `app/decorators/` (decorators genéricos de cache `@cache_aside`/`@invalidate_cache`, verificação de papéis RBAC e handlers JWT).
* **PostgreSQL + SQLAlchemy + Alembic:** Persistência relacional com precisão decimal (`Numeric(10, 2)`), integridade transacional via `atomic_transaction()` e versionamento rastreável da base de dados através de migrações.
* **Redis 7 (Alpine):** Armazenamento NoSQL em memória para caching com TTL de 3600s, abstraído por decorators reutilizáveis com invalidação automática nas rotas de escrita (`POST`, `PUT`, `DELETE`) e fallback defensivo para o PostgreSQL em caso de indisponibilidade.
* **Flask-JWT-Extended & Werkzeug:** Segurança stateless via tokens injetados em cookies seguros `HttpOnly`, matriz RBAC (*Role-Based Access Control*) com claims adicionais e decoradores customizados (`@admin_required`).
* **Flasgger (OpenAPI 2.0 / Swagger UI):** Documentação viva e interativa exposta em `/apidocs/` com suporte nativo a autorização via Cookies no navegador.
* **Logging Centralizado (`logging`):** Sistema de rastreabilidade estruturada em padrão ISO 8601 para monitoramento de acessos, erros e eventos de cache.
* **Marshmallow & Domain Validation:** Sanitização de contratos e validação tipada estrita (`Decimal`, regras de negócio e `@validates` no modelo).
* **Docker & Docker Compose:** Orquestração de múltiplos serviços (`taciana_api`, `taciana_db`, `taciana_redis`) com *healthchecks* nativos (`pg_isready` e `redis-cli ping`), rede privada isolada (`taciana_net`) e execução com usuário não-root (`appuser`).
* **GitHub Actions (CI/CD):** Esteira automatizada de integração contínua (Ubuntu Runner) executando a suíte Pytest com injeção de *secrets* a cada *push* ou *pull request*.
* **Pytest & unittest.mock:** Suíte com **19 testes automatizados** modulares utilizando fixtures compartilhadas (`conftest.py`), parametrização de casos de borda (`@pytest.mark.parametrize`), mocks de falha de infraestrutura (`patch`) e reset de cache via `redis_client.flushdb()`.

## Estudo de Caso & Benchmarking (ApacheBench)

Testes de carga sob concorrência (`ab -n 500 -c 10`) no endpoint `GET /categorias` comprovam a eficiência do padrão Cache-Aside:

| Métrica | Somente PostgreSQL (Baseline) | PostgreSQL + Redis (Cache-Aside) | Impacto / Otimização |
| :--- | :---: | :---: | :---: |
| **Vazão (Throughput)** | `255.29 req/sec` | `493.10 req/sec` | **+93.1%** 🚀 |
| **Tempo Médio por Req.** | `39.172 ms` | `20.280 ms` | **-48.2%** ⚡ |
| **Tempo Máximo (Worst-case)** | `218 ms` | `66 ms` | **-69.7%** 📉 |

## Funcionalidades

* **Autenticação & Sessão:** Login e registro com injeção de perfil (Admin vs User) via cookies HTTP-Only seguros.
* **Controle de Acesso (RBAC):** Proteção estrita de rotas mutáveis (POST, PUT, DELETE) exclusivas para administradores via decorador `@admin_required`.
* **Documentação Interativa:** Interface Swagger UI acessível publicamente para teste de todos os endpoints e schemas da API.
* **Observabilidade:** Logs formatados gravados em stdout detalhando requisições, hits/misses de cache e falhas de autorização.
* **Gestão de Estoque & Precisão Financeira:** CRUD completo de **Categorias** e **Produtos** utilizando `Decimal` / `Numeric(10, 2)` e cálculo encapsulado de patrimônio em estoque (`valor_total_estoque`).
* **Cache-Aside Inteligente via Decorators:**
  * Leitura acelerada via `@cache_aside` (`GET /categorias` e `GET /produtos`).
  * Invalidação ativa e automática das chaves no Redis via `@invalidate_cache` apenas quando operações de escrita retornam sucesso (`200`/`201`).
  * Resiliência de infraestrutura com fallback automático para o PostgreSQL caso o Redis fique offline.
* **Regras de Negócio & Integridade ACID:**
  * Transações atômicas com rollback automático em caso de falha (`atomic_transaction`).
  * Bloqueio de valores monetários nulos/negativos e quantidades negativas tanto no schema quanto no domínio.
  * Bloqueio de inserção de produtos duplicados, exclusão de categoria com produtos vinculados e associação com categorias inexistentes.

## Desafios Superados e Roadmap

### Desafios Superados (v3.1.0 e Anteriores)
* **Integridade Financeira, Decorators de Cache e Hardening (v3.1.0):**
  * Migração de `preco` para `Numeric(10, 2)` via Alembic com validação dupla (`Marshmallow` + `@validates`) e property `valor_total_estoque`.
  * Criação do context manager `atomic_transaction()` para garantir atomicidade nas escritas.
  * Desacoplamento da lógica de cache com `@cache_aside` e `@invalidate_cache`, eliminando duplicação de código nas rotas.
  * Expansão da suíte Pytest para **19 testes** com `@pytest.mark.parametrize` e `unittest.mock.patch` simulando Redis offline.
  * Aplicação do princípio do menor privilégio no `Dockerfile` (`appuser`) e *healthchecks* completos no `docker-compose.yml`.
* **Refatoração Modular e Observabilidade (v3.0.0):** Criação dos pacotes `app/core/` e `app/decorators/`, padronização de logs ISO 8601 e modernização das chamadas do Redis client.
* **Documentação Swagger & Flasgger (v3.0.0):** Integração OpenAPI 2.0 modularizada via arquivos YAML externos em `app/docs/` com suporte a autenticação por cookies.
* **Testes Integrados de Cache (v3.0.0):** Validação empírica das etapas de Cache MISS, Cache HIT e Invalidação com isolamento via `flushdb()`.
* **PoC de Caching e Otimização NoSQL (v2.9.0):** Integração do container `taciana_redis` e aplicação do padrão Cache-Aside.
* **RBAC e Decoradores Customizados (v2.8.0):** Autorização baseada em papéis inspecionando claims JWT em tempo de execução.
* **Pipeline de CI/CD e Healthchecks (v2.7.0):** Validação automatizada no GitHub Actions e orquestração Docker Compose.

### Próximos Passos (Backlog)
* **Paginação e Filtros:** Implementar paginação nas rotas `GET` de produtos e categorias para suportar alta volumetria de dados.
* **Taxa de Limite de Requisições (Rate Limiting):** Proteger a API contra ataques de força bruta e DDoS utilizando Flask-Limiter com armazenamento no Redis.
* **Interface Gráfica (Front-End):** Desenvolver um painel web interativo (React / Vue.js) para consumo das rotas da API.

## Como rodar o projeto localmente

> **Pré-requisitos:** É obrigatório ter o **Docker** e o **Docker Compose** instalados na sua máquina.

1. Clone o repositório e acesse a pasta:
   ```bash
   git clone https://github.com/MuriloDev07/Projeto-Sistema-LanHouse.git
   cd Projeto-Sistema-LanHouse
   ```

2. Configure o ambiente de variáveis:
   ```bash
   cp .env.example .env
   # Preencha as credenciais do banco de dados e a sua JWT_SECRET_KEY
   ```

3. Suba os contêineres e aplique as migrações:
   ```bash
   docker compose up -d --build
   docker exec -it taciana_api flask db upgrade
   ```
   > A API estará disponível em `http://127.0.0.1:5000`.
   > A Documentação Swagger UI estará disponível em `http://127.0.0.1:5000/apidocs/`.

**Para rodar a suíte de testes (Pytest) manualmente:**
```bash
docker exec taciana_api pytest -v
```

## Endpoints Principais

| Método | Rota | Descrição | Segurança | Cache |
|--------|------|-----------|-----------|-------|
| POST | `/auth/registro` | Cadastra novo usuário na plataforma | Livre | N/A |
| POST | `/auth/login` | Autentica usuário, valida role e retorna Cookie JWT | Livre | N/A |
| POST | `/auth/logout` | Revoga a sessão e remove o cookie JWT | 🔒 Autenticado | N/A |
| GET | `/produtos` | Lista todos os produtos | Livre | ⚡ `@cache_aside` (1h TTL) |
| POST | `/produtos` | Cadastra um novo produto | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| PUT | `/produtos/<id>` | Atualiza dados de um produto | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| DELETE | `/produtos/<id>` | Remove um produto do estoque | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| GET | `/categorias` | Lista todas as categorias | Livre | ⚡ `@cache_aside` (1h TTL) |
| POST | `/categorias` | Cadastra uma nova categoria | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| PUT | `/categorias/<id>` | Atualiza uma categoria existente | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| DELETE | `/categorias/<id>` | Remove uma categoria | 🔒 Admin JWT | 🧹 `@invalidate_cache` |

## Estrutura do Projeto

```bash
├── .github/                  # Automação e Integração Contínua
│   └── workflows/
│       └── ci.yml            # Esteira de CI (GitHub Actions)
├── app/                      # Núcleo da Aplicação (Application Factory)
│   ├── __init__.py           # Fábrica de inicialização (create_app)
│   ├── core/                 # Módulos de Infraestrutura e Serviços Core
│   │   ├── cache.py          # Conexão e cliente Redis NoSQL
│   │   ├── logging_config.py # Centralizador de logs formatados em ISO 8601
│   │   └── swagger.py        # Configuração e rotas do Flasgger / Swagger UI
│   ├── decorators/           # Decoradores e Manipuladores de Exceção
│   │   ├── auth.py           # Matriz RBAC (@admin_required)
│   │   ├── cache.py          # Decoradores genéricos (@cache_aside e @invalidate_cache)
│   │   └── jwt_handlers.py   # Callbacks de expiração e erros de token JWT
│   ├── docs/                 # Especificações OpenAPI 2.0 (YAML)
│   │   ├── auth/             # Schemas de autenticação
│   │   ├── categorias/       # Schemas das rotas de categoria
│   │   └── produtos/         # Schemas das rotas de produto
│   ├── models/               # Entidades SQLAlchemy, Schemas Marshmallow e DB
│   │   ├── categoria.py
│   │   ├── database.py       # Instância SQLAlchemy e context manager atomic_transaction
│   │   ├── produto.py        # Modelo Produto com Numeric(10,2) e @validates
│   │   ├── schemas.py        # Validação estrita com Marshmallow Decimal
│   │   └── usuario.py
│   └── routes/               # Blueprints de rotas da API
│       ├── auth.py
│       ├── categorias.py
│       └── produtos.py
├── tests/                    # Suíte de testes modulares e integrados (Pytest - 19 testes)
│   ├── conftest.py           # Fixtures compartilhadas, SQLite em memória e reset do Redis
│   ├── test_auth.py          # Testes de autenticação e RBAC
│   ├── test_categorias.py    # Testes integrados, parametrizados e de Cache para categorias
│   └── test_produtos.py      # Testes integrados, parametrizados, Cache e Mock Redis offline
├── migrations/               # Arquivos de migração do banco de dados (Alembic)
├── config.py                 # Gerenciador de configurações (python-dotenv)
├── run.py                    # Ponto de entrada leve da aplicação
├── pytest.ini                # Configuração declarativa de mapeamento e cache de testes
├── .env.example              # Template de variáveis de ambiente
├── .gitignore                # Ignora .env, venv, caches
├── .dockerignore             # Otimização da imagem Docker
├── docker-compose.yml        # Orquestração (API + PostgreSQL + Redis com Healthchecks)
├── Dockerfile                # Receita segura da imagem da API (usuário não-root appuser)
└── requirements.txt          # Dependências do ecossistema Python (Flask, Redis, SQLAlchemy...)
```
