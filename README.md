# Sistema de Loja - Lan House (v2.8.0)

API REST conteinerizada para gerenciar o estoque da lan house 'Taciana Variedades'. Evoluída de um protótipo em SQLite para uma infraestrutura escalável com PostgreSQL, o sistema foca em segurança (JWT e RBAC), validação estrita (Marshmallow), arquitetura corporativa (Application Factory) e integração contínua (CI/CD) com 100% de cobertura de testes.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma infraestrutura escalável com PostgreSQL e Docker. Na **versão 2.8.0**, o foco foi a **Segurança e Controle de Acesso**, implementando o padrão RBAC (*Role-Based Access Control*) com injeção de *claims* via JWT e decoradores customizados. A aplicação possui total isolamento entre configurações, rotas, regras de negócio e a suíte de testes automatizados modulares (100% de cobertura via Pytest).

## Arquitetura e Tecnologias

A stack foi escolhida para simular um ambiente de produção moderno, priorizando a segurança e a separação de responsabilidades:

* **Python + Flask:** Motor e estrutura baseada no padrão Application Factory, isolando rotas, modelos e lógica de testes.
* **PostgreSQL + SQLAlchemy + Alembic:** Persistência relacional, integridade de dados e versionamento rastreável da base de dados através de migrações.
* **Flask-JWT-Extended & Werkzeug:** Segurança stateless via tokens Bearer para autorização, criptografia hash de senhas e injeção de *roles* de usuário no payload.
* **Marshmallow:** Sanitização de contratos e validação tipada estrita para entrada e saída de dados (JSON).
* **Docker & Docker Compose:** Infraestrutura imutável orquestrando a API e o banco de dados em uma rede privada, contando com *healthchecks* declarativos e dependências condicionais entre contêineres.
* **GitHub Actions (CI/CD):** Esteira automatizada para validação de compilação do ambiente, injeção de segredos (*Secrets*) e execução da suíte de testes em ambiente virtual limpo (Ubuntu Runner) a cada *push* ou *pull request*.
* **Pytest & python-dotenv:** Qualidade e QA isolado (`tests/`, `conftest.py`, `pytest.ini`) com injeção declarativa de configurações e testes unitários granulares simulando diferentes perfis de acesso.

## Funcionalidades

* **Autenticação:** Geração de tokens de acesso (Login/Registro) e senhas protegidas com injeção de perfil (Admin/User).
* **Controle de Acesso Baseado em Papéis (RBAC):** Rotas mutáveis (POST, PUT, DELETE) rigorosamente protegidas, garantindo privilégios exclusivos para administradores.
* **Gestão de Estoque:** CRUD completo de **Categorias** e **Produtos**.
* **Regras de Negócio Blindadas:**
  * Bloqueio estrito de inserção de produtos duplicados.
  * Impedimento de exclusão de categoria se houver produtos vinculados a ela.
  * Bloqueio de criação ou atualização de produto referenciando uma categoria inexistente.

## Desafios Superados e Roadmap

### Desafios Superados (v2.8.0 e Anteriores)
* **Implementação de RBAC e Decoradores Customizados (v2.8.0):** Criação de uma matriz de autorização injetando a *role* nas *additional claims* do token JWT. Desenvolvimento do decorador customizado `@admin_required` (utilizando `functools.wraps` e `get_jwt()`) para inspecionar permissões em tempo de execução sem acoplar regras de segurança diretamente nas funções de rota.
* **Modularização da Suíte de Testes (v2.8.0):** Fragmentação dos casos de teste (`test_auth.py`, `test_categorias.py`, `test_produtos.py`) e consolidação do `conftest.py` com *fixtures* dinâmicas de autenticação, cobrindo com precisão respostas 200, 201, 401, 403 e 404 de acordo com o perfil injetado (Admin vs User).
* **Pipeline de CI/CD Automático (v2.7.0):** Implementação do GitHub Actions como barreira de segurança (*quality gate*). 
* **Resiliência de Infraestrutura (v2.7.0):** Adição de *healthchecks* nativos no PostgreSQL e sincronização de subida da API via `condition: service_healthy`.
* **Application Factory e SoC (v2.6.0):** Isolamento total da infraestrutura de testes (`tests/`) do código de produção (`app/`), resolvendo importações circulares.

### Próximos Passos (Backlog)
* **Documentação OpenAPI:** Integrar Swagger/Flasgger para documentar os endpoints e seus contratos dinamicamente.
* **Paginação e Filtros:** Implementar paginação nas rotas `GET` de produtos para suportar alta volumetria de dados no futuro.
* **Fluxo de Caixa:** Criar novas rotas para registrar a saída (venda) de produtos, baixando o estoque automaticamente e registrando o faturamento diário.
* **Desenvolvimento da Interface (Front-End):** Construção da interface gráfica de usuário (UI) estruturada em HTML, CSS e JavaScript para consumir os endpoints da API.
* **Controle de Idempotência:** Implementação de chaves de idempotência (Idempotency Keys) nas rotas de criação (POST) contra duplicidades por falhas de rede.
* **Backup Automatizado do Banco de Dados:** Implementação de uma rotina automatizada para criação e exportação periódica de dumps do PostgreSQL (pg_dump) em contêiner Docker.

## Como rodar o projeto localmente

> **Pré-requisitos:** É obrigatório ter o **Docker** e o **Docker Compose** instalados na sua máquina.

1. Clone o repositório e acesse a pasta:
   ```bash
   git clone <https://github.com/MuriloDev07/Projeto-Sistema-LanHouse.git>
   cd <pasta-do-projeto>
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

| Método | Rota | Descrição | Segurança |
|--------|------|-----------|-----------|
| POST | `/auth/login` | Autentica usuário, valida role e retorna Token | Livre |
| GET | `/produtos` | Lista todos os produtos | Livre |
| POST | `/produtos` | Cadastra um novo produto | 🔒 Admin JWT |
| PUT | `/produtos/<id>` | Atualiza dados de um produto | 🔒 Admin JWT |
| DELETE | `/produtos/<id>` | Remove um produto do estoque | 🔒 Admin JWT |

*(As rotas de `/categorias` seguem o mesmo padrão de segurança e nomenclatura).*

## Estrutura do Projeto

```bash
├── .github/                 # Automação e Integração Contínua
│   └── workflows/
│       └── ci.yml           # Esteira de CI (GitHub Actions)
├── app/                     # Núcleo da Aplicação (Application Factory)
│   ├── __init__.py          # Fábrica (create_app)
│   ├── decorators.py        # Decoradores de autorização (RBAC)
│   ├── models/              # Entidades, Schemas e Database
│   └── routes/              # Blueprints de rotas
├── tests/                   # Infraestrutura de testes modulares e integrados
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
├── docker-compose.yml       # Orquestração (API + PostgreSQL com Healthcheck)
├── Dockerfile               # Receita da imagem da API
└── requirements.txt         # Dependências do ecossistema Python
```