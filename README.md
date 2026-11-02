# Sistema de Loja - Lan House (v2.7.0)

API REST conteinerizada para gerenciar o estoque da lan house 'Taciana Variedades'. Evoluída de um protótipo em SQLite para uma infraestrutura escalável com PostgreSQL, o sistema foca em segurança (JWT), validação estrita (Marshmallow), arquitetura corporativa (Application Factory) e integração contínua (CI/CD) com 100% de cobertura de testes.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma infraestrutura escalável com PostgreSQL e Docker. Na **versão 2.7.0**, o foco foi a **Automação de Engenharia e Resiliência**, integrando uma esteira de CI/CD via GitHub Actions e refinando a orquestração de contêineres com verificações de saúde (*healthcheck*). A aplicação possui total isolamento entre configurações, rotas, regras de negócio e a suíte de testes automatizados (100% de cobertura via Pytest).

## Arquitetura e Tecnologias

A stack foi escolhida para simular um ambiente de produção moderno, priorizando a segurança e a separação de responsabilidades:

* **Python + Flask:** Motor e estrutura baseada no padrão Application Factory, isolando rotas, modelos e lógica de testes.
* **PostgreSQL + SQLAlchemy + Alembic:** Persistência relacional, integridade de dados e versionamento rastreável da base de dados através de migrações.
* **Flask-JWT-Extended & Werkzeug:** Segurança stateless via tokens Bearer para autorização e criptografia hash de senhas de usuários.
* **Marshmallow:** Sanitização de contratos e validação tipada estrita para entrada e saída de dados (JSON).
* **Docker & Docker Compose:** Infraestrutura imutável orquestrando a API e o banco de dados em uma rede privada, contando com *healthchecks* declarativos e dependências condicionais entre contêineres.
* **GitHub Actions (CI/CD):** Esteira automatizada para validação de compilação do ambiente, injeção de segredos (*Secrets*) e execução da suíte de testes em ambiente virtual limpo (Ubuntu Runner) a cada *push* ou *pull request*.
* **Pytest & python-dotenv:** Qualidade e QA isolado (`tests/`, `conftest.py`, `pytest.ini`) com injeção declarativa de configurações.

## Funcionalidades

* **Autenticação:** Geração de tokens de acesso (Login/Registro) e senhas protegidas.
* **Segurança de Escrita:** Rotas de modificação (POST, PUT, DELETE) bloqueadas para usuários não autenticados.
* **Gestão de Estoque:** CRUD completo de **Categorias** e **Produtos**.
* **Regras de Negócio Blindadas:**
  * Bloqueio estrito de inserção de produtos duplicados.
  * Impedimento de exclusão de categoria se houver produtos vinculados a ela.
  * Bloqueio de criação ou atualização de produto referenciando uma categoria inexistente.

## Desafios Superados e Roadmap

### Desafios Superados (v2.7.0 e Anteriores)
* **Pipeline de CI/CD Automático (v2.7.0):** Implementação do GitHub Actions como barreira de segurança (*quality gate*). Qualquer código quebrado ou regressão na suíte de testes é bloqueado automaticamente antes de ser incorporado à ramificação principal.
* **Resiliência de Infraestrutura (v2.7.0):** Adição de *healthchecks* nativos no PostgreSQL e sincronização de subida da API via `condition: service_healthy`, eliminando falhas de inicialização por ausência de conexão do banco.
* **Application Factory (v2.6.0):** A transição do núcleo do sistema para este padrão resolveu problemas críticos de importação circular e isolou as configurações.
* **Separação de Preocupações - SoC (v2.6.0):** Isolamento total da infraestrutura de testes (`tests/`) do código de produção (`app/`), garantindo um ambiente de QA blindado sem poluir a aplicação.

### Próximos Passos (Backlog)
* **Documentação OpenAPI:** Integrar Swagger/Flasgger para documentar os endpoints e seus contratos dinamicamente.
* **Paginação e Filtros:** Implementar paginação nas rotas `GET` de produtos para suportar alta volumetria de dados no futuro.
* **RBAC (Controle de Acesso):** Criar níveis de permissão, separando perfil de "Administradores" (poder total de alteração) e "Usuários" (apenas leitura ou acesso restrito).
* **Fluxo de Caixa:** Criar novas rotas para registrar a saída (venda) de produtos, baixando o estoque automaticamente e registrando o faturamento diário.
* **Desenvolvimento da Interface (Front-End):** Construção da interface gráfica de usuário (UI) estruturada em HTML, CSS e JavaScript para consumir os endpoints da API, substituindo o uso de ferramentas de teste por telas funcionais para a operação diária.
* **Controle de Idempotência:** Implementação de chaves de idempotência (Idempotency Keys) nas rotas de criação (POST), garantindo que requisições duplicadas por falhas de rede não gerem registros inconsistentes na base de dados.
* **Backup Automatizado do Banco de Dados:** Implementação de uma rotina automatizada para criação e exportação periódica de dumps do PostgreSQL (pg_dump), garantindo a integridade, resiliência dos dados e rápido plano de recuperação em desastres (Disaster Recovery) para a operação da lan house.

## Como rodar o projeto localmente

> **Pré-requisitos:** É obrigatório ter o **Docker** e o **Docker Compose** instalados na sua máquina.

1. Clone o repositório e acesse a pasta:
   ```bash
   git clone <url-do-seu-repo>
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
docker exec taciana_api pytest
```

## Endpoints Principais

| Método | Rota | Descrição | Segurança |
|--------|------|-----------|-----------|
| POST | `/auth/login` | Autentica usuário e retorna Token | Livre |
| GET | `/produtos` | Lista todos os produtos | Livre |
| POST | `/produtos` | Cadastra um novo produto | 🔒 Requer JWT |
| PUT | `/produtos/<id>` | Atualiza dados de um produto | 🔒 Requer JWT |
| DELETE | `/produtos/<id>` | Remove um produto do estoque | 🔒 Requer JWT |

*(As rotas de `/categorias` seguem o mesmo padrão de segurança e nomenclatura).*

## Estrutura do Projeto

```bash
├── .github/                 # Automação e Integração Contínua
│   └── workflows/
│       └── ci.yml           # Esteira de CI (GitHub Actions)
├── app/                     # Núcleo da Aplicação (Application Factory)
│   ├── __init__.py          # Fábrica (create_app)
│   ├── models/              # Entidades, Schemas e Database
│   └── routes/              # Blueprints de rotas
├── tests/                   # Infraestrutura de testes
│   ├── conftest.py          # Fixtures e configurações do Pytest
│   └── test_api.py          # Casos de teste automatizados
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
