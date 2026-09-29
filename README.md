# Sistema de Loja - Lan House

API REST para gerenciar produtos e categorias de uma lan house, desenvolvida com Flask e SQLite.

## Funcionalidades

- CRUD completo de **categorias** (ex: Bebidas, Salgadinhos, Acessórios de PC)
- CRUD completo de **produtos**, cada um vinculado a uma categoria
- Validação de dados de entrada (nome obrigatório, preço numérico, etc.)
- Impede remover uma categoria que ainda tem produtos vinculados a ela
- Impede criar/atualizar um produto com uma categoria que não existe

## Tecnologias

- Python 3
- Flask
- SQLite
- Pytest (testes automatizados)

## Como rodar o projeto

1. Clone o repositório
   \`\`\`bash
   git clone <url-do-seu-repo>
   cd <pasta-do-projeto>
   \`\`\`

2. Crie e ative um ambiente virtual
   \`\`\`bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   \`\`\`

3. Instale as dependências
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Rode a aplicação
   \`\`\`bash
   python app.py
   \`\`\`

A API sobe em `http://127.0.0.1:5000`.

## Rodando os testes

\`\`\`bash
pytest -v
\`\`\`

## Endpoints

### Categorias
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /categorias | Lista todas as categorias |
| GET | /categorias/\<id\> | Busca uma categoria por id |
| POST | /categorias | Cria uma categoria |
| PUT | /categorias/\<id\> | Atualiza uma categoria |
| DELETE | /categorias/\<id\> | Remove uma categoria (se não houver produtos vinculados) |

### Produtos
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /produtos | Lista todos os produtos |
| GET | /produtos/\<id\> | Busca um produto por id |
| POST | /produtos | Cria um produto |
| PUT | /produtos/\<id\> | Atualiza um produto |
| DELETE | /produtos/\<id\> | Remove um produto |

## Exemplo de uso

\`\`\`bash
curl -X POST http://127.0.0.1:5000/categorias -H "Content-Type: application/json" -d "{\"nome\": \"Bebidas\"}"

curl -X POST http://127.0.0.1:5000/produtos -H "Content-Type: application/json" -d "{\"nome\": \"Coca-Cola\", \"preço\": 5.0, \"estoque\": 20, \"categoria_id\": 1}"
\`\`\`

## Estrutura do projeto

\`\`\`
├── app.py                  # Rotas Flask
├── Banco/
│   ├── banco.py             # Classe Conexao (gerencia SQLite)
│   ├── CategoriaRepositorio.py
│   └── ProdutoRepositorio.py
├── test_app.py              # Testes automatizados
└── requirements.txt
\`\`\`

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Este sistema serviu como o meu principal laboratório prático para consolidar conhecimentos em Back-end com Python, integrando rotas Flask, banco de dados SQLite e garantindo a confiabilidade com testes automatizados via Pytest. O próximo passo será evoluir esta arquitetura e integrar novas funcionalidades para a gestão completa da Lan House.
