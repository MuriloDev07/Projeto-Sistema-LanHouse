# Sistema de Loja - Lan House (v2.6.0)

API REST conteinerizada para gerenciar o estoque da lan house 'Taciana Variedades'. Evoluída de um protótipo em SQLite para uma infraestrutura escalável com PostgreSQL, o sistema foca em segurança (JWT), validação estrita (Marshmallow) e arquitetura corporativa (Application Factory) com 100% de cobertura de testes.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma infraestrutura escalável com PostgreSQL e Docker. Na atual **versão 2.6.0**, o foco foi a **Arquitetura Corporativa**, refatorando o núcleo do sistema para o padrão Application Factory. A aplicação agora possui total isolamento entre configurações, rotas, regras de negócio e a suíte de testes automatizados (100% de cobertura via Pytest).

## Arquitetura e Tecnologias

A stack foi escolhida para simular um ambiente de produção moderno, priorizando a segurança e a separação de responsabilidades:

* **Python + Flask:** Motor e estrutura baseada no padrão Application Factory, isolando rotas, modelos e lógica de testes.
* **PostgreSQL + SQLAlchemy + Alembic:** Persistência relacional, integridade de dados e versionamento rastreável da base de dados através de migrações.
* **Flask-JWT-Extended & Werkzeug:** Segurança stateless via tokens Bearer para autorização e criptografia hash de senhas de usuários.
* **Marshmallow:** Sanitização de contratos e validação tipada estrita para entrada e saída de dados (JSON).
* **Docker & Docker Compose:** Infraestrutura imutável orquestrando a API e o banco de dados em uma rede privada.
* **Pytest & python-dotenv:** Qualidade e CI isolado (`tests/`, `conftest.py`, `pytest.ini`) com injeção declarativa de configurações.

## Funcionalidades

* **Autenticação:** Geração de tokens de acesso (Login/Registro) e senhas protegidas.
* **Segurança de Escrita:** Rotas de modificação (POST, PUT, DELETE) bloqueadas para usuários não autenticados.
* **Gestão de Estoque:** CRUD completo de **Categorias** e **Produtos**.
* **Regras de Negócio Blindadas:**
  * Bloqueio estrito de inserção de produtos duplicados.
  * Impedimento de exclusão de categoria se houver produtos vinculados a ela.
  * Bloqueio de criação ou atualização de produto referenciando uma categoria inexistente.

## Desafios Superados e Roadmap

### Desafios Superados (v2.6.0)
* **Application Factory:** A transição do núcleo do sistema para este padrão resolveu problemas críticos de importação circular e isolou as configurações.
* **Separação de Preocupações (SoC):** Isolamento total da infraestrutura de testes (`tests/`) do código de produção (`app/`), garantindo um ambiente de QA blindado sem poluir a aplicação.

### Próximos Passos (Backlog)
* **Documentação OpenAPI:** Integrar Swagger/Flasgger para documentar os endpoints e seus contratos dinamicamente.
* **Paginação e Filtros:** Implementar paginação nas rotas `GET` de produtos para suportar alta volumetria de dados no futuro.
* **RBAC (Controle de Acesso):** Criar níveis de permissão, separando perfil de "Administradores" (poder total de alteração) e "Usuários" (apenas leitura ou acesso restrito).
* **Fluxo de Caixa:** Criar novas rotas para registrar a saída (venda) de produtos, baixando o estoque automaticamente e registrando o faturamento diário.
* **Pipeline CI/CD:** Configurar GitHub Actions para executar a verificação de código e os testes automaticamente a cada novo *Pull Request*.
* **Desenvolvimento da Interface (Front-End):** Construção da interface gráfica de usuário (UI) estruturada em HTML, CSS e JavaScript para consumir os endpoints da API, substituindo o uso de ferramentas de teste por telas funcionais para a operação diária.
* **Controle de Idempotência:** Implementação de chaves de idempotência (Idempotency Keys) nas rotas de criação (POST), garantindo que requisições duplicadas por falhas de rede não gerem registros inconsistentes na base de dados.

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

**Para rodar a suíte de testes (Pytest):**
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
├── docker-compose.yml       # Orquestração (API + PostgreSQL)
├── Dockerfile               # Receita da imagem da API
└── requirements.txt         # Dependências do ecossistema Python
``
