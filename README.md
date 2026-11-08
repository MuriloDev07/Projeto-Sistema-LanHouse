# Sistema de Loja - Lan House (v3.0.0)

API REST conteinerizada para gerenciar o estoque da lan house 'Taciana Variedades'. Evoluída de um protótipo em SQLite para uma infraestrutura corporativa de alta performance, contando com PostgreSQL, Caching em Memória com Redis, segurança robusta (JWT e RBAC via Cookies HTTP-Only), observabilidade, documentação OpenAPI/Swagger e 100% de cobertura nos testes automatizados via Pytest.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma infraestrutura escalável com PostgreSQL e Docker.

Na **versão 3.0.0**, o projeto alcançou maturidade de produção através de uma grande refatoração de arquitetura limpa e observabilidade. Foram introduzidos **Logging Estruturado** centralizado, **Documentação Swagger UI (OpenAPI 2.0)** interativa com autenticação por cookies, **Arquitetura Modularizada** (`app/core/` e `app/decorators/`), **Suíte de Testes com Validação de Ciclo de Vida do Cache (HIT, MISS e Invalidação)**, e a modernização das chamadas do cliente Redis.

## Arquitetura e Tecnologias

A stack foi projetada para simular um ambiente de produção moderno, priorizando separação de responsabilidades, performance e manutenibilidade:

* **Python + Flask:** Motor base alinhado ao padrão *Application Factory*, isolando rotas, modelos e lógica de testes.
* **Arquitetura Modularizada:** Divisão clara do núcleo em `app/core/` (configurações de cache, logging estruturado e Swagger) e `app/decorators/` (verificação de papéis RBAC e tratamento de erros JWT).
* **PostgreSQL + SQLAlchemy + Alembic:** Persistência relacional, integridade de dados e versionamento rastreável da base de dados através de migrações.
* **Redis 8.1.0 (Alpine):** Armazenamento NoSQL em memória para caching com TTL de 3600s, usando a sintaxe moderna `.set(..., ex=3600)` e invalidação ativa nas rotas de escrita (`POST`, `PUT`, `DELETE`). Conta com fallback defensivo para o PostgreSQL em caso de indisponibilidade.
* **Flask-JWT-Extended & Werkzeug:** Segurança stateless via tokens injetados em cookies seguros `HttpOnly`, matriz RBAC (*Role-Based Access Control*) com claims adicionais e decoradores customizados (`@admin_required`).
* **Flasgger (OpenAPI 2.0 / Swagger UI):** Documentação viva e interativa exposta em `/apidocs/` com suporte nativo a autorização via Cookies no navegador.
* **Logging Centralizado (`logging`):** Sistema de rastreabilidade estruturada em padrão ISO 8601, substituindo chamadas manuais para monitoramento de acessos, erros e eventos de cache.
* **Marshmallow:** Sanitização de contratos e validação tipada estrita de entradas e saídas JSON.
* **Docker & Docker Compose:** Orquestração de múltiplos serviços (`taciana_api`, `taciana_db`, `taciana_redis`) com *healthchecks* nativos (`pg_isready`) e comunicação em rede privada isolada (`taciana_net`).
* **GitHub Actions (CI/CD):** Esteira automatizada de integração contínua (Ubuntu Runner) executando a suíte Pytest com injeção de *secrets* a cada *push* ou *pull request*.
* **Pytest & python-dotenv:** Suíte completa de testes automatizados modulares com fixtures dinâmicas (`conftest.py`), incluindo isolamento de base via SQLite em memória e reset de cache via `redis_client.flushdb()`.

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
* **Gestão de Estoque:** CRUD completo de **Categorias** e **Produtos**.
* **Cache-Aside Inteligente:**
  * Leitura acelerada via Redis (`GET /categorias` e `GET /produtos`).
  * Invalidação ativa e automática das chaves no Redis em operações de inserção, edição ou remoção.
  * Resiliência de infraestrutura com fallback automático para a base relacional se o Redis estiver offline.
* **Regras de Negócio Blindadas:**
  * Bloqueio de inserção de produtos duplicados.
  * Impedimento de exclusão de categoria com produtos vinculados.
  * Bloqueio de alteração ou inserção de produtos com categorias inexistentes.

## Desafios Superados e Roadmap

### Desafios Superados (v3.0.0 e Anteriores)
* **Refatoração Modular e Observabilidade (v3.0.0):** Criação dos pacotes `app/core/` (configurações de cache, logging estruturado e Swagger UI) e `app/decorators/` (RBAC e handlers JWT), padronização de logs ISO 8601 e eliminação de deprecation warnings no Redis client (`.set(..., ex=3600)`).
* **Documentação Swagger & Flasgger (v3.0.0):** Integração OpenAPI 2.0 modularizada via arquivos YAML externos em `app/docs/` com suporte a autenticação por cookies.
* **Testes Integrados de Cache (v3.0.0):** Expansão da suíte Pytest com validação empírica das etapas de Cache MISS, Cache HIT e Invalidação, utilizando fixture com `flushdb()` para isolamento absoluto entre testes.
* **PoC de Caching e Otimização NoSQL (v2.9.0):** Integração do container `taciana_redis` e aplicação do padrão Cache-Aside com resiliência defensiva.
* **RBAC e Decoradores Customizados (v2.8.0):** Autorização baseada em papéis inspecionando claims JWT em tempo de execução.
* **Pipeline de CI/CD e Healthchecks (v2.7.0):** Validação automatizada no GitHub Actions e orquestração Docker Compose via `condition: service_healthy`.

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
   docker-compose up -d --build
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
| GET | `/produtos` | Lista todos os produtos | Livre | ⚡ Redis (1h TTL) |
| POST | `/produtos` | Cadastra um novo produto | 🔒 Admin JWT | 🧹 Invalida Cache |
| PUT | `/produtos/<id>` | Atualiza dados de um produto | 🔒 Admin JWT | 🧹 Invalida Cache |
| DELETE | `/produtos/<id>` | Remove um produto do estoque | 🔒 Admin JWT | 🧹 Invalida Cache |
| GET | `/categorias` | Lista todas as categorias | Livre | ⚡ Redis (1h TTL) |
| POST | `/categorias` | Cadastra uma nova categoria | 🔒 Admin JWT | 🧹 Invalida Cache |
| DELETE | `/categorias/<id>` | Remove uma categoria | 🔒 Admin JWT | 🧹 Invalida Cache |

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
│   │   └── jwt_handlers.py   # Callbacks de expiração e erros de token JWT
│   ├── docs/                 # Especificações OpenAPI 2.0 (YAML)
│   │   ├── auth.py           # Schemas de autenticação
│   │   ├── categorias.py     # Schemas das rotas de categoria
│   │   └── produtos.py       # Schemas das rotas de produto
│   ├── models/               # Entidades SQLAlchemy, Schemas Marshmallow e DB
│   │   ├── categoria.py
│   │   ├── database.py
│   │   ├── produto.py
│   │   └── usuario.py
│   └── routes/              # Blueprints de rotas da API
│       ├── auth.py
│       ├── categorias.py
│       └── produtos.py
├── tests/                   # Suíte de testes modulares e integrados (Pytest)
│   ├── conftest.py          # Fixtures, SQLite em memória e ciclo de vida do Redis
│   ├── test_auth.py         # Testes de autenticação e RBAC
│   ├── test_categorias.py   # Testes integrados de categorias e Cache
│   └── test_produtos.py     # Testes integrados de produtos e Cache
├── migrations/              # Arquivos de migração do banco de dados (Alembic)
├── config.py                # Gerenciador de configurações (python-dotenv)
├── run.py                   # Ponto de entrada leve da aplicação
├── pytest.ini               # Configuração declarativa de mapeamento de testes
├── .env.example             # Template de variáveis de ambiente
├── .gitignore               # Ignora .env, venv, caches
├── .dockerignore            # Otimização da imagem Docker
├── docker-compose.yml       # Orquestração (API + PostgreSQL + Redis com Healthchecks)
├── Dockerfile               # Receita da imagem da API
└── requirements.txt         # Dependências do ecossistema Python (Flask, Redis, SQLAlchemy...)
```
