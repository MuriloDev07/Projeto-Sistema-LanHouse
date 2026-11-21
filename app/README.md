# Back-end & API REST - Taciana Variedades

Documentação técnica da camada de servidor, persistência, caching e segurança da aplicação **Taciana Variedades**.

> Para visão geral do sistema Full-Stack e instruções de inicialização via Docker, consulte o [README principal](../README.md).

## Arquitetura Interna (`app/`)

O back-end segue o padrão **Application Factory** (`create_app()` em `app/__init__.py`), garantindo isolamento de contexto entre execução em produção e testes automatizados:

* **`app/core/` (Infraestrutura):**
  * `cache.py`: Gerenciamento da conexão com o Redis 7 e serialização JSON.
  * `logging_config.py`: Logs estruturados em padrão ISO 8601 gravados em `stdout` para rastreabilidade de requisições, acertos/falhas de cache e erros de autorização.
  * `swagger_config.py`: Configuração do Flasgger (OpenAPI 2.0) carregando especificações YAML desacopladas de `app/docs/`.
* **`app/decorators/` (Aspectos Transversais):**
  * `@admin_required`: Inspeção de *claims* JWT em tempo de execução para controle de acesso baseado em papéis (RBAC).
  * `@cache_aside` e `@invalidate_cache`: Decorators genéricos que abstraem a leitura e invalidação ativa no Redis, mantendo degradação graciosa (fallback automático ao PostgreSQL) caso o serviço de cache fique offline.
  * `jwt_handlers.py`: Padronização das respostas JSON para tokens ausentes, expirados ou inválidos.
* **`app/models/` (Domínio & Persistência):**
  * Precisão monetária garantida pelo uso estrito de `Numeric(10, 2)` no PostgreSQL e `Decimal` no Python, com validação em dupla camada (schemas Marshmallow + `@validates` no SQLAlchemy).
  * Gerenciador de contexto `atomic_transaction()` em `database.py` assegurando atomicidade ACID (*commit* e *rollback* automáticos).
* **`app/routes/` (Blueprints):**
  * Separação limpa entre rotas da API REST (`usuarios.py`, `categorias.py`, `produtos.py`) e o Blueprint `web.py`, responsável por servir a interface HTML na raiz (`/`) e os recursos estáticos em `/assets`.

## Estudo de Caso & Benchmarking (ApacheBench)

Testes de carga sob concorrência (`ab -n 500 -c 10`) no endpoint `GET /categorias` comprovam o ganho de desempenho do padrão *Cache-Aside*:

| Métrica | Somente PostgreSQL (Baseline) | PostgreSQL + Redis (Cache-Aside) | Impacto / Otimização |
| :--- | :---: | :---: | :---: |
| **Vazão (Throughput)** | `255.29 req/sec` | `493.10 req/sec` | **+93.1%** 🚀  |
| **Tempo Médio por Req.** | `39.172 ms` | `20.280 ms` | **-48.2%** ⚡  |
| **Tempo Máximo (Worst-case)** | `218 ms` | `66 ms` | **-69.7%** 📉 |

## Endpoints da API

| Método | Rota | Descrição | Segurança | Cache |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Entrega a interface web principal (`index.html`) | Livre | Estático (`/assets`) |
| `POST` | `/auth/registro` | Cadastra novo usuário na plataforma | Livre (Restrito na UI ao Admin) | N/A |
| `POST` | `/auth/login` | Autentica credenciais e injeta Cookie JWT `HttpOnly` | Livre | N/A |
| `POST` | `/auth/logout` | Revoga a sessão e limpa o Cookie JWT | 🔒 Autenticado | N/A |
| `GET` | `/produtos` | Lista todos os produtos cadastrados | Livre | ⚡ `@cache_aside` (1h TTL) |
| `POST` | `/produtos` | Cadastra um novo produto no estoque | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| `PUT` | `/produtos/<id>` | Atualiza preço, estoque ou categoria de um produto | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| `DELETE` | `/produtos/<id>` | Remove um produto do catálogo | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| `GET` | `/categorias` | Lista todas as categorias | Livre | ⚡ `@cache_aside` (1h TTL) |
| `POST` | `/categorias` | Cadastra uma nova categoria | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| `PUT` | `/categorias/<id>` | Atualiza o nome de uma categoria | 🔒 Admin JWT | 🧹 `@invalidate_cache` |
| `DELETE` | `/categorias/<id>` | Remove categoria (bloqueado se houver produtos vinculados) | 🔒 Admin JWT | `@invalidate_cache` |

## Qualidade e Testes Automatizados (Pytest)

A suíte em `tests/` conta com **29 testes automatizados** executados tanto localmente quanto na esteira de CI (GitHub Actions):
* **Isolamento:** Uso de SQLite em memória e limpeza automática do Redis (`flushdb()`) via fixtures em `conftest.py`.
* **Cobertura de Borda e Falhas:** Testes parametrizados (`@pytest.mark.parametrize`) para valores inválidos e simulação de queda do Redis (`unittest.mock.patch`) validando o fallback para o banco relacional.
* **Integridade da Interface Web (`test_web.py`):** Validação parametrizada da entrega do `index.html` (`GET /`), dos ativos estáticos em `/assets` (CSS, JS, logotipo e favicon) e do tratamento de rotas inexistentes (`404`).

```bash
# Executar a suíte completa dentro do container:
docker compose exec api pytest -v
```