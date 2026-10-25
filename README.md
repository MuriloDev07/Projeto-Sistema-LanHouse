# Sistema de Loja - Lan House (V2.0)

API REST conteinerizada para gerenciar produtos e categorias de uma lan house, desenvolvida com Flask, SQLAlchemy, PostgreSQL e Docker.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Inicialmente construído com SQLite para consolidação de fundamentos, o sistema evoluiu para uma **versão 2.0 focada em infraestrutura e escalabilidade**. A aplicação agora roda em um ambiente totalmente isolado com Docker, utilizando o PostgreSQL como banco de dados relacional e mantendo a alta confiabilidade com testes automatizados via Pytest.

## Funcionalidades

- CRUD completo de **categorias** (ex: Bebidas, Salgadinhos, Acessórios de PC)
- CRUD completo de **produtos**, cada um vinculado a uma categoria
- Validação de dados de entrada (nome obrigatório, preço numérico, estoque não negativo)
- Bloqueio de exclusão de categoria se houver produtos vinculados
- Impedimento de criação/atualização de produto com `categoria_id` inexistente

## Decisões de Engenharia e Regras de Negócio

Para garantir que o sistema escale sem inconsistências, a arquitetura atual baseia-se nas seguintes decisões:

* **Infraestrutura Imutável (Docker):** O ambiente de desenvolvimento e produção é idêntico. O uso do `docker-compose` garante que a API e o banco de dados subam juntos e configurados, eliminando o problema de "na minha máquina funciona".
* **Segurança de Credenciais:** As chaves e senhas do banco de dados não ficam hardcoded. O sistema consome variáveis de ambiente injetadas por um arquivo `.env` ignorado pelo Git.
* **Integridade Relacional (PostgreSQL):** A migração do SQLite para o PostgreSQL garante maior robustez para futuras requisições simultâneas e integridade de dados em um SGBD de mercado.
* **Proteção contra Produtos Órfãos:** Restrição rígida no método `DELETE` das categorias. O sistema impede a remoção de uma categoria se ainda existirem produtos vinculados a ela.

## Por que esta Stack?

* **Python + Flask:** Mantidos pela rapidez na prototipagem de rotas RESTful e flexibilidade arquitetural.
* **SQLAlchemy (ORM):** Substituiu o antigo padrão de repositório manual para agilizar a modelagem de dados e a comunicação segura com o PostgreSQL.
* **Docker & Docker Compose:** Escolhidos para orquestrar a infraestrutura, garantindo que o banco de dados e a aplicação se comuniquem em uma rede isolada.
* **Pytest (Testes Automatizados):** Uma suíte de testes que assegura que refatorações estruturais (como a troca de banco de dados) não quebrem as regras de negócio.

## O que aprendi e o que faria diferente (Próximos Passos)

1. **Separação em Blueprints:** Atualmente as rotas estão centralizadas. O próximo passo de refatoração do código será utilizar *Flask Blueprints* para separar as rotas de Categorias e Produtos em módulos independentes.
2. **Soft Delete (Histórico):** Em vez de apagar fisicamente um produto que parou de ser vendido, pretendo adicionar uma flag de "inativo". Apagar o produto exclui os dados históricos, prejudicando relatórios futuros.
3. **Identificação (Autenticação JWT):** Implementar um sistema de login para registrar qual funcionário realizou cada operação de entrada e saída no estoque.

## Tecnologias

- Python 3 / Flask
- PostgreSQL / SQLAlchemy
- Docker / Docker Compose
- Pytest

---

## 🚀 Como rodar o projeto (V2.0)

> **BREAKING CHANGE:** A versão 2.0 não utiliza mais banco de dados local em arquivo. É obrigatório ter o **Docker** e o **Docker Compose** instalados na sua máquina.

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
docker exec -it taciana_api pytest -v
```

## Endpoints

### Categorias
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /categorias | Lista todas as categorias |
| GET | /categorias/\<id\> | Busca uma categoria por id |
| POST | /categorias | Cria uma categoria |
| PUT | /categorias/\<id\> | Atualiza uma categoria |
| DELETE | /categorias/\<id\> | Remove uma categoria (se vazia) |

### Produtos
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /produtos | Lista todos os produtos |
| GET | /produtos/\<id\> | Busca um produto por id |
| POST | /produtos | Cria um produto |
| PUT | /produtos/\<id\> | Atualiza um produto |
| DELETE | /produtos/\<id\> | Remove um produto |

## Estrutura do projeto

```bash
├── models/
│   ├── database.py          # Configuração do SQLAlchemy
│   ├── categoria.py
│   └── produto.py
├── .env.example             # Template de variáveis de ambiente
├── .gitignore               # Ignora .env, venv, caches
├── .dockerignore            # Otimização da imagem Docker
├── app.py                   # Motor da aplicação e Rotas Flask
├── docker-compose.yml       # Orquestração (API + PostgreSQL)
├── Dockerfile               # Receita da imagem da API
├── LICENSE                  # Licença MIT
├── requirements.txt         # Dependências do Python
└── test_app.py              # Suíte de testes (Pytest)
```
