# Sistema de Loja - Lan House (V2.5)

API REST conteinerizada para gerenciar produtos e categorias de uma lan house, desenvolvida com Flask, SQLAlchemy, PostgreSQL, Docker, validação com Marshmallow e segurança via JWT.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma infraestrutura escalável com PostgreSQL e Docker. Na atual **versão 2.5**, o foco foi a **Segurança e Validação**, integrando autenticação JWT, criptografia de senhas e serialização tipada com Marshmallow. O sistema mantém alta confiabilidade com testes automatizados via Pytest com 100% de cobertura.

## Funcionalidades

- **[NOVO]** Autenticação e autorização gerando tokens de acesso (JWT).
- **[NOVO]** Cadastro de usuários com senhas criptografadas (hash via Werkzeug).
- **[NOVO]** Serialização e validação robusta de entrada/saída de dados usando Marshmallow.
- **[NOVO]** Bloqueio de inserção de produtos duplicados na base de dados.
- Rotas de escrita (POST, PUT, DELETE) protegidas por token de acesso.
- CRUD completo de **categorias** e **produtos**.
- Bloqueio de exclusão de categoria se houver produtos vinculados.
- Impedimento de criação/atualização de produto com `categoria_id` inexistente.

## Decisões de Engenharia e Regras de Negócio

Para garantir que o sistema escale sem inconsistências, a arquitetura atual baseia-se nas seguintes decisões:

* **Segurança e Identificação (JWT):** Implementação de endpoints de autenticação, restringindo alterações no estoque apenas a usuários autorizados (evitando manipulações indevidas).
* **Validação de Contratos (Marshmallow):** A substituição dos antigos métodos `to_dict` manuais pelos esquemas do Marshmallow simplificou os modelos e garantiu maior segurança e tipagem no recebimento e envio de JSONs.
* **Versionamento de Banco (Migrations):** Adoção de migrações estruturais (Flask-Migrate/Alembic) para gerenciar alterações nas tabelas de forma segura e rastreável.
* **Infraestrutura Imutável (Docker):** O ambiente de desenvolvimento e produção é idêntico. O uso do `docker-compose` garante que a API e o banco de dados subam juntos e configurados.
* **Segurança de Credenciais:** As chaves e senhas não ficam hardcoded. O sistema consome variáveis de ambiente injetadas por um arquivo `.env`.

## Por que esta Stack?

* **Python + Flask:** Mantidos pela rapidez na prototipagem de rotas RESTful e flexibilidade arquitetural.
* **SQLAlchemy & PostgreSQL:** Agilidade na modelagem de dados e integridade em um SGBD de mercado.
* **Flask-JWT-Extended & Werkzeug:** Ferramentas consolidadas para geração de tokens de acesso e hash de senhas.
* **Marshmallow:** Biblioteca agnóstica e poderosa para validação e serialização de objetos complexos.
* **Docker & Docker Compose:** Escolhidos para orquestrar a infraestrutura em uma rede isolada.
* **Pytest (Testes Automatizados):** Suíte de testes (com injeção de tokens fictícios) que assegura que refatorações não quebrem as regras de negócio.

## Aprendizados e Próximos Passos

### O que aprendi nesta jornada

* **Conteinerização e Orquestração (Docker & Docker Compose):** Padronização completa do ambiente de desenvolvimento e produção, garantindo isolamento da API e do banco de dados em uma rede privada.
* **Persistência Relacional Escalável (PostgreSQL & SQLAlchemy):** Transição de uma base local SQLite para um SGBD de mercado de alta performance, capaz de lidar com alta concorrência e requisições simultâneas mantendo a integridade dos dados.
* **Validação Tipada e Tratamento de Erros (Marshmallow):** Substituição de validações manuais por schemas estruturados de serialização e desserialização, garantindo sanitização de entrada/saída e tratamento de erros padronizado.
* **Segurança e Autenticação (JWT & Werkzeug):** Implementação de controle de acesso stateless via tokens Bearer JWT e proteção de credenciais com criptografia hash de senhas.

### Próximos Passos (Roadmap)

1. **Arquitetura Application Factory:** Refatorar o motor do sistema para o padrão de fábrica de aplicações (`create_app()`). Essa evolução arquitetural isolará a inicialização do Flask, resolvendo gargalos de importação e permitindo criar diretórios dedicados (`app/` e `tests/`). Isso garantirá total isolamento entre o banco de dados de produção e o ambiente de testes automatizados.
2. **Desenvolvimento do Front-End:** Desenvolver a interface gráfica de usuário (UI) utilizando HTML, CSS e JavaScript para consumir esta API REST. O objetivo é substituir o uso de clientes de API (como o Postman) por telas intuitivas, entregando uma plataforma com alta usabilidade para a gestão de estoque pelos administradores da lan house.

## Tecnologias

- Python 3 / Flask
- PostgreSQL / SQLAlchemy
- Flask-JWT-Extended / Werkzeug Security
- Marshmallow
- Docker / Docker Compose
- Pytest

---

## 🚀 Como rodar o projeto (V2.5)

> **BREAKING CHANGE:** A versão 2.5 exige a configuração de uma chave JWT. É obrigatório ter o **Docker** e o **Docker Compose** instalados na sua máquina.

1. Clone o repositório e entre na pasta
   ```bash
   git clone <url-do-seu-repo>
   cd <pasta-do-projeto>
   ```

2. Configure as variáveis de ambiente
   ```bash
   cp .env.example .env
   ```
   > Abra o arquivo .env recém-criado e preencha com as senhas desejadas (este arquivo está protegido pelo .gitignore e não subirá para o GitHub).

3. Suba a infraestrutura completa com o Docker
   ```bash
   docker-compose up --build
   ```
   > O Docker fará o download do PostgreSQL, compilará a imagem da API e conectará os dois. A API estará disponível em http://127.0.0.1:5000.

## Rodando os testes

Como a aplicação agora roda dentro de um contêiner, você deve disparar o Pytest por dentro da rede do Docker:
```bash
docker exec taciana_api python -m pytest
```

## Endpoints

### Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /auth/registro | Cadastra um novo usuário no sistema |
| POST | /auth/login | Autentica o usuário e retorna o Token JWT (Bearer) |

### Categorias
| Método | Rota | Descrição | Seguramça
|--------|------|-----------|-----------|
| GET | /categorias | Lista todas as categorias | Livre
| GET | /categorias/\<id\> | Busca uma categoria por id | Livre
| POST | /categorias | Cria uma categoria | 🔒 Requer JWT
| PUT | /categorias/\<id\> | Atualiza uma categoria | 🔒 Requer JWT
| DELETE | /categorias/\<id\> | Remove uma categoria (se vazia) | 🔒 Requer JWT

### Produtos
| Método | Rota | Descrição | Seguramça
|--------|------|-----------|-----------|
| GET | /produtos | Lista todos os produtos | Livre
| GET | /produtos/\<id\> | Busca um produto por id | Livre
| POST | /produtos | Cria um produto | 🔒 Requer JWT
| PUT | /produtos/\<id\> | Atualiza um produto | 🔒 Requer JWT
| DELETE | /produtos/\<id\> | Remove um produto | 🔒 Requer JWT

## Estrutura do projeto

```bash
├── migrations/              # Arquivos de migração do banco de dados (Alembic)
├── models/
│   ├── database.py          # Configuração do SQLAlchemy
│   ├── schemas.py           # Validações e serialização (Marshmallow)
│   ├── categoria.py         # Entidade Categoria
│   ├── produto.py           # Entidade Produto
│   └── usuario.py           # Entidade Usuário (Senhas criptografadas)
├── routes/                  # Arquivos de rotas isoladas
│   ├── categorias.py
│   ├── produtos.py
│   └── usuarios.py
├── .env.example             # Template de variáveis de ambiente
├── .gitignore               # Ignora .env, venv, caches
├── .dockerignore            # Otimização da imagem Docker
├── app.py                   # Motor da aplicação e inicialização
├── docker-compose.yml       # Orquestração (API + PostgreSQL)
├── Dockerfile               # Receita da imagem da API
├── requirements.txt         # Dependências do Python (incluindo JWT, Marshmallow)
└── test_app.py              # Suíte de testes (Pytest) com injeção de tokens
```
