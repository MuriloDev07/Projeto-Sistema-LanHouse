# Sistema de Gestão - Taciana Variedades (v4.0.0)

Aplicação web **Full-Stack conteinerizada** para gestão de estoque e consulta rápida de preços da lan house e loja **Taciana Variedades**. Evoluída de um protótipo de API em SQLite para uma arquitetura completa servida em origem única via Docker, integrando back-end de alta performance (Flask, PostgreSQL, Redis) com uma interface web responsiva (*mobile-first*) construída em HTML5, CSS3 modular e JavaScript ES Modules.

## Contexto e Evolução

Projetado para atender à operação diária no balcão da **Taciana Variedades**, o sistema oferece aos operadores da loja uma interface rápida e intuitiva para consultar preços, acompanhar a disponibilidade em tempo real e gerenciar o cadastro de produtos e categorias durante o atendimento, além de permitir o controle de contas de acesso através de um painel administrativo protegido.

Na **versão 4.0.0**, o projeto deu o salto de uma API pura para uma **aplicação Full-Stack unificada**:
* **Entrega Unificada (Same-Origin):** O Flask entrega tanto os endpoints REST quanto a interface web na porta `5000` por meio de um Blueprint dedicado (`app/routes/web.py`), simplificando o deploy local e eliminando atritos de CORS com cookies `HttpOnly`.
* **Interface Responsiva e Intuitiva:** Tabela adaptativa no desktop que se transforma automaticamente em cartões (*cards*) em dispositivos móveis, com busca instantânea, filtros dinâmicos por categoria e alertas visuais de estoque.
* **Alta Disponibilidade Local:** Orquestração Docker Compose com *healthchecks* e política `restart: unless-stopped`, garantindo recuperação automática após reinicializações do computador do balcão.

## Documentação Modular

Para facilitar a navegação técnica, a documentação está dividida por camadas:

* 📘 **[Documentação do Back-end (`app/README.md`)](app/README.md):** Detalhes da *Application Factory*, precisão financeira (`Decimal`), transações atômicas, padrão *Cache-Aside* com Redis, benchmarking (ApacheBench), segurança RBAC/JWT e suíte de 29 testes Pytest.
* 🎨 **[Documentação do Front-end (`frontend/README.md`)](frontend/README.md):** Arquitetura semântica HTML5, design system com CSS Variables, responsividade *mobile-first*, modais nativos (`<dialog>`) e separação de responsabilidades em ES Modules (`api.js`, `ui.js`, `main.js`).

## Arquitetura e Stack Tecnológica

| Camada | Tecnologias e Padrões |
| :--- | :--- |
| **Front-end** | HTML5 Semântico, CSS3 Modular (Variables, Flexbox/Grid, Media Queries), Vanilla JavaScript (ES6+ Modules, Fetch API) |
| **Back-end** | Python 3.12, Flask (*Application Factory* & Blueprints), Marshmallow, Flasgger (OpenAPI 2.0 / Swagger) |
| **Persistência & Cache** | PostgreSQL 15 (`Numeric(10, 2)`), SQLAlchemy, Alembic, Redis 7 (`@cache_aside` e `@invalidate_cache`) |
| **Segurança** | Flask-JWT-Extended via Cookies `HttpOnly`, RBAC (`@admin_required`), cadastro de operadores restrito a administradores |
| **Infraestrutura & QA** | Docker, Docker Compose (`restart: unless-stopped`, usuário não-root `appuser`), GitHub Actions (CI), Pytest (29 testes) |

## Funcionalidades Principais

* **Consulta Pública Ágil:** Pesquisa instantânea por nome, filtragem por categorias dinâmicas e sinalização semântica de estoque (**Disponível**, **Estoque Baixo** e **Esgotado**).
* **Painel Administrativo Protegido:** Login via cookies seguros `HttpOnly` que desbloqueia controles de criação, edição e exclusão de produtos e categorias sem recarregar a página.
* **Gestão de Operadores:** Cadastro de novas contas de acesso restrito exclusivamente a administradores já autenticados.
* **Performance & Resiliência:** Leitura acelerada pelo Redis (+93.1% de vazão comprovada em benchmark) com fallback automático para o PostgreSQL em caso de indisponibilidade do cache.

## Como Rodar o Projeto Localmente

> **Pré-requisitos:** Ter o **Docker** e o **Docker Compose** instalados na máquina.

1. **Clone o repositório e acesse a pasta:**
   ```bash
   git clone https://github.com/MuriloDev07/Projeto-Sistema-LanHouse.git
   cd Projeto-Sistema-LanHouse
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o .env definindo DB_USER, DB_PASSWORD, DB_NAME e JWT_SECRET_KEY
   ```

3. **Suba os contêineres:**
   ```bash
   docker compose up -d --build
   ```

4. **Inicialize o banco de dados e crie o primeiro administrador:**
   ```bash
   docker compose exec api flask db upgrade
   # Caso ainda não existam revisões na pasta migrations/versions, crie as tabelas e o admin via shell:
   docker compose exec api flask shell
   ```
   ```python
   from app.models.database import db
   from app.models.usuario import Usuario
   db.create_all()
   admin = Usuario(username="admin", role="admin")
   admin.set_password("sua_senha_segura")
   db.session.add(admin)
   db.session.commit()
   exit()
   ```

5. **Acesse a aplicação:**
   * **Interface Web (Loja):** `http://localhost:5000`
   * **Documentação Interativa da API (Swagger):** `http://localhost:5000/apidocs/`

## Desafios Superados e Roadmap

### Desafios Superados
* **v4.0.0 — Interface Web, Unificação Full-Stack & QA:** Desenvolvimento de front-end responsivo em HTML5/CSS3/JS modular para operação no balcão, integração via Blueprint `web` (`/assets`) na mesma origem da API, expansão da suíte Pytest para **29 testes automatizados** (incluindo validação parametrizada da entrega da interface), configuração de alta disponibilidade (`restart: unless-stopped`) no Docker Compose e garantia de teardown no CI (`if: always()`).
* **v3.1.0 — Integridade Financeira, Cache Decorators & Hardening:** Migração monetária para `Numeric(10, 2)`, transações atômicas (`atomic_transaction()`), abstração `@cache_aside`/`@invalidate_cache`, container com usuário não-root (`appuser`) e suíte de 19 testes automatizados com mocks de falha.
* **v3.0.0 — Modularização & Observabilidade:** Criação de `app/core/` e `app/decorators/`, logs ISO 8601 e Swagger modularizado em YAML.

### Próximos Passos (Roadmap)
* **Módulo de Serviços:** Implementar cadastro e tabela de preços para serviços da lan house (impressões, xerox, digitalizações e manutenções).
* **Evolução para E-commerce (React):** Migrar e expandir a interface web para React visando transformar o sistema em uma vitrine virtual completa com carrinho e pedidos online.
* **Paginação & Rate Limiting:** Adicionar paginação nos endpoints `GET` e proteção contra abuso de requisições com Flask-Limiter + Redis.

## Estrutura do Projeto

```bash
├── .github/                  # Automação e Integração Contínua
│   └── workflows/
│       └── ci.yml            # Esteira de CI (GitHub Actions)
├── app/                      # Back-end Flask (Application Factory)
│   ├── README.md             # Documentação técnica detalhada da API
│   ├── __init__.py           # Fábrica de inicialização (create_app)
│   ├── core/                 # Cache Redis, Logging ISO 8601 e Swagger
│   ├── decorators/           # RBAC (@admin_required), Cache e Handlers JWT
│   ├── docs/                 # Especificações OpenAPI 2.0 (YAML)
│   ├── models/               # Entidades SQLAlchemy e Schemas Marshmallow
│   └── routes/               # Blueprints da API e interface web
│       ├── categorias.py
│       ├── produtos.py
│       ├── usuarios.py
│       └── web.py            # Blueprint de entrega do front-end (/) e /assets
├── frontend/                 # Interface Web Responsiva (HTML5/CSS3/ES Modules)
│   ├── README.md             # Documentação de arquitetura e UI/UX do front-end
│   ├── index.html            # Estrutura semântica e modais nativos (<dialog>)
│   ├── css/                  # Estilos modulares (variables, layout, modals)
│   ├── images/               # Identidade visual (logotipo e favicon)
│   └── js/                   # Lógica modularizada (api.js, ui.js, main.js)
├── tests/                    # Suíte Pytest (29 testes unitários e integrados)
├── migrations/               # Histórico de migrações Alembic
├── config.py                 # Configurações centralizadas via variáveis de ambiente
├── run.py                    # Ponto de entrada da aplicação
├── docker-compose.yml        # Orquestração (API + PostgreSQL + Redis)
├── Dockerfile                # Imagem segura com usuário não-root (appuser)
└── requirements.txt          # Dependências Python
```