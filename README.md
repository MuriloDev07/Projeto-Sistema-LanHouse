# Sistema de Loja - Lan House

API REST para gerenciar produtos e categorias de uma lan house, desenvolvida com Flask e SQLite.

## Contexto

Projeto criado para gerenciar o estoque real da lan house 'Taciana Variedades'. Este sistema serviu como o meu principal laboratório prático para consolidar conhecimentos em Back-end com Python, integrando rotas Flask, banco de dados SQLite e garantindo a confiabilidade com testes automatizados via Pytest. O próximo passo será evoluir esta arquitetura e integrar novas funcionalidades para a gestão completa da Lan House.

## Funcionalidades

- CRUD completo de **categorias** (ex: Bebidas, Salgadinhos, Acessórios de PC)
- CRUD completo de **produtos**, cada um vinculado a uma categoria
- Validação de dados de entrada (nome obrigatório, preço numérico, etc.)
- Impede remover uma categoria que ainda tem produtos vinculados a ela
- Impede criar/atualizar um produto com uma categoria que não existe

## Decisões de Engenharia e Regras de Negócio

Para garantir que o sistema não permitia inconsistências, tomei as seguintes decisões:

* **Proteção contra Produtos Órfãos:** Implementei uma restrição rígida no método `DELETE` das categorias. O sistema **impede** a remoção de uma categoria (ex: "Salgadinhos") se ainda existirem produtos vinculados a ela.
* **Validação de Referência:** No `POST` e `PUT` de produtos, a API bloqueia a criação de um item associado a um `categoria_id` inexistente.
* **Segurança de Dados:** Validações de entrada estritas (nome obrigatório, preço numérico e stock não negativo) diretamente na camada de negócio, antes de tentar persistir no banco.

## Por que esta Stack?

* **Python + Flask:** Escolhidos pela rapidez na prototipagem de rotas RESTful, permitindo que o meu foco estivesse nas regras de negócio e não em configurações complexas de infraestrutura.
* **SQLite + Padrão Repository:** Para manter o projeto portátil e modular, isolei as queries de banco de dados em classes de repositório (`CategoriaRepositorio.py` e `ProdutoRepositorio.py`).
* **Pytest (Testes Automatizados):** Com as regras de negócio a ficarem mais complexas, testar manualmente no Postman/Insomnia deixou de ser viável. Introduzi o Pytest para garantir que as restrições de categoria nunca fossem quebradas em futuras atualizações.

## O que aprendi e o que faria diferente (Próximos Passos)

1. **Vendas Simultâneas (Concorrência):** O que acontece se dois funcionários tentarem dar baixa no último refrigerante do estoque exatamente no mesmo segundo? Atualmente, o sistema pode falhar e registrar um estoque negativo. Como próximo passo, quero estudar como os bancos de dados lidam com requisições simultâneas para prevenir esse erro.
2. **Histórico de Produtos:** Em vez de usar o método `DELETE` para apagar um produto que a Lan House parou de vender, percebi que seria mais inteligente inativá-lo. Apagar o produto exclui os dados, o que prejudicaria um futuro relatório de vendas passadas.
3. **Identificação (Autenticação):** Atualmente qualquer pessoa com acesso à API faz alterações. A próxima evolução natural seria implementar um sistema de login para saber *qual* atendente registrou ou apagou cada produto.

## Tecnologias

- Python 3
- Flask
- SQLite
- Pytest (testes automatizados)

## Como rodar o projeto

1. Clone o repositório
   ```bash
   git clone <url-do-seu-repo>
   cd <pasta-do-projeto>
   ```

2. Crie e ative um ambiente virtual
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências
   ```bash
   pip install -r requirements.txt
   ```

4. Rode a aplicação
   ```bash
   python app.py
   ```

A API sobe em `http://127.0.0.1:5000`.

## Rodando os testes

```bash
pytest -v
```

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

```bash
curl -X POST http://127.0.0.1:5000/categorias -H "Content-Type: application/json" -d "{\"nome\": \"Bebidas\"}"

curl -X POST http://127.0.0.1:5000/produtos -H "Content-Type: application/json" -d "{\"nome\": \"Coca-Cola\", \"preço\": 5.0, \"estoque\": 20, \"categoria_id\": 1}"
```

## Estrutura do projeto

```bash
├── app.py                  # Rotas Flask
├── Banco/
│   ├── banco.py             # Classe Conexao (gerencia SQLite)
│   ├── CategoriaRepositorio.py
│   └── ProdutoRepositorio.py
├── test_app.py              # Testes automatizados
└── requirements.txt
```
