# Sistema de Loja - Lan House (v2.9.0)

API REST conteinerizada para gerenciar o estoque da lan house 'Taciana Variedades'. Evoluída de um protótipo em SQLite para uma infraestrutura corporativa com PostgreSQL e Caching em Memória com Redis, garantindo alta performance, segurança (JWT e RBAC), resiliência e validação estrita (100% de cobertura Pytest).

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma infraestrutura escalável com PostgreSQL e Docker.

Na **versão 2.9.0**, o foco principal foi a **Otimização de Performance e Redução de I/O na Base de Dados**. Foi implementada uma Prova de Conceito (PoC) introduzindo o **Redis** como camada NoSQL de armazenamento em memória, utilizando o padrão **Cache-Aside (Lazy Loading)** para os endpoints de leitura de categorias e produtos. A alteração foi acompanhada por testes empíricos de carga via ApacheBench, comprovando ganhos expressivos de throughput e redução de latência.

## Arquitetura e Tecnologias

A stack foi escolhida para simular um ambiente de produção moderno, priorizando a performance, segurança e separação de responsabilidades:

* **Python + Flask:** Motor base alinhado ao padrão *Application Factory*, isolando rotas, modelos e lógica de testes.
* **PostgreSQL + SQLAlchemy + Alembic:** Persistência relacional, integridade de dados e versionamento rastreável da base de dados através de migrações.
* **Redis 8.1.0 (Alpine):** Armazenamento NoSQL em memória para caching com tempo de expiração (TTL de 3600s) e invalidação ativa em rotas de escrita (`POST`, `PUT`, `DELETE`). Conta com fallback defensivo para o PostgreSQL em caso de indisponibilidade do Redis.
* **Flask-JWT-Extended & Werkzeug:** Segurança stateless via tokens injetados em cookies seguros `HttpOnly`, matriz RBAC (*Role-Based Access Control*) com claims adicionais e decoradores customizados (`@admin_required`).
* **Marshmallow:** Sanitização de contratos e validação tipada estrita de entradas e saídas JSON.
* **Docker & Docker Compose:** Orquestração de múltiplos serviços (`taciana_api`, `taciana_db`, `taciana_redis`) com *healthchecks* nativos (`pg_isready`) e comunicação em rede privada isolada (`taciana_net`).
* **GitHub Actions (CI/CD):** Esteira automatizada de integração contínua (Ubuntu Runner) executando a suíte Pytest com injeção de *secrets* a cada *push* ou *pull request*.
* **Pytest & python-dotenv:** Suíte completa de testes automatizados modulares com fixtures dinâmicas (`conftest.py`).

## Estudo de Caso & Benchmarking (ApacheBench)

Foram realizados testes de carga sob concorrência (`ab -n 500 -c 10`) no endpoint `GET /categorias` para medir empiricamente o impacto da introdução do Redis no sistema:

| Métrica | Somente PostgreSQL (Baseline) | PostgreSQL + Redis (Cache-Aside) | Impacto / Otimização |
| :--- | :---: | :---: | :---: |
| **Vazão (Throughput)** | `255.29 req/sec` | `493.10 req/sec` | **+93.1%** 🚀 |
| **Tempo Médio por Req.** | `39.172 ms` | `20.280 ms` | **-48.2%** ⚡ |
| **Tempo Máximo (Worst-case)** | `218 ms` | `66 ms` | **-69.7%** 📉 |

## Funcionalidades

* **Autenticação & Sessão:** Login e registro com injeção de perfil (Admin vs User) via cookies HTTP-Only seguros.
* **Controle de Acesso (RBAC):** Proteção estrita de rotas mutáveis (POST, PUT, DELETE) exclusivas para administradores via decorador `@admin_required`.
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

### Desafios Superados (v2.9.0 e Anteriores)
* **PoC de Caching e Otimização NoSQL (v2.9.0):** Integração do container `taciana_redis`, criação do módulo `app/cache.py` e aplicação do padrão Cache-Aside com suporte a resiliência defensiva e invalidação inteligente de cache.
* **RBAC e Decoradores Customizados (v2.8.0):** Implementação de autorização baseada em papéis inspecionando claims JWT em tempo de execução sem acoplar regras de segurança nas funções de rota.
* **Modularização da Suíte de Testes (v2.8.0):** Fragmentação dos arquivos de teste e consolidação do `conftest.py` com fixtures dinâmicas de autenticação (100% de cobertura).
* **Pipeline de CI/CD e Healthchecks (v2.7.0):** Validação automatizada no GitHub Actions e sincronização de subida dos serviços via `condition: service_healthy` no Docker Compose.

### Próximos Passos (Backlog)
* **Observabilidade:** Estruturar módulo centralizado de logs (`logging`) em substituição a `print()` para rastreabilidade de requisições e eventos de cache.
* **Documentação OpenAPI / Swagger:** Integrar o Flasgger para documentar os endpoints e contratos da API de forma interativa.
* **Paginação e Filtros:** Implementar paginação nas rotas `GET` de produtos para suportar alta volumetria.
* **Desenvolvimento da Interface (Front-End):** Interface gráfica web (HTML5, CSS3 e JavaScript) para consumo da API.

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
   # Abra o arquivo .env e preencha as credenciais do banco e a sua JWT_SECRET_KEY
   ```

3. Suba os contêineres:
   ```bash
   docker-compose up -d --build
   ```
   > O Docker compilará a imagem. A API estará disponível em `http://127.0.0.1:5000`.

**Para rodar a suíte de testes (Pytest) manualmente:**
```bash
docker exec taciana_api pytest -v
```

## Endpoints Principais

| Método | Rota | Descrição | Segurança | Cache |
|--------|------|-----------|-----------|-------|
| POST | `/auth/login` | Autentica usuário, valida role e retorna Token | Livre | N/A
| GET | `/produtos` | Lista todos os produtos | Livre | ⚡ Redis (1h TTL)
| POST | `/produtos` | Cadastra um novo produto | 🔒 Admin JWT | 🧹 Invalida Cache
| PUT | `/produtos/<id>` | Atualiza dados de um produto | 🔒 Admin JWT | 🧹 Invalida Cache
| DELETE | `/produtos/<id>` | Remove um produto do estoque | 🔒 Admin JWT | 🧹 Invalida Cache

*(As rotas de `/categorias` seguem o mesmo padrão de segurança e nomenclatura).*

## Estrutura do Projeto

```bash
├── .github/                 # Automação e Integração Contínua
│   └── workflows/
│       └── ci.yml           # Esteira de CI (GitHub Actions)
├── app/                     # Núcleo da Aplicação (Application Factory)
│   ├── __init__.py          # Fábrica (create_app)
│   ├── cache.py             # Módulo de integração e conexão com Redis
│   ├── decorators.py        # Decoradores de autorização (RBAC)
│   ├── models/              # Entidades SQLAlchemy, Marshmallow Schemas e Database
│   └── routes/              # Blueprints de rotas (Categorias, Produtos e Auth)
├── tests/                   # Suíte de testes modulares e integrados (Pytest)
│   ├── conftest.py          # Fixtures e ciclo de vida do app/banco (Pytest)
│   ├── test_auth.py         # Testes de login e matriz JWT
│   ├── test_categorias.py   # Validação de regras e RBAC (Categorias)
│   └── test_produtos.py     # Validação de regras e RBAC (Produtos)
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
