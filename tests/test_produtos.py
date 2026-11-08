from app.core.cache import redis_client
from app.routes.produtos import CACHE_KEY_PRODUTOS

def test_create_produto_com_categoria_valida(client, admin_auth_headers):
    """
    Admin cria produto com sucesso.
    """
    categoria = client.post('/categorias', json={"nome": "Eletrônicos"}, headers=admin_auth_headers)
    dados = {
            "nome": "Pendrive 8GB",
            "preco": 20,
            "quantidade": 15,
            "categoria_id": categoria.get_json()['id']
        }
    resposta = client.post('/produtos', json=dados, headers=admin_auth_headers)
    assert resposta.status_code == 201

def test_create_produto_como_usuario_comum(client, user_auth_headers):
    """
    Usuário Comum é impedido de criar categoria (HTTP 403).
    """
    categoria = client.post('/categorias', json={"nome": "Eletrônicos"}, headers=user_auth_headers)
    dados = {
            "nome": "Pendrive 8GB",
            "preco": 20,
            "quantidade": 15,
            "categoria_id": 1
        }
    resposta = client.post('/produtos', json=dados, headers=user_auth_headers)
    assert resposta.status_code == 403
    assert resposta.get_json()['msg'] == "Acesso restrito a Administradores"

def test_create_produto_sem_categoria(client, admin_auth_headers):
    """
    Erro 404 ao tentar associar produto a categoria inexistente.
    """
    dados = {
        "nome": "Pendrive 8GB",
        "preco": 20,
        "quantidade": 15,
        "categoria_id": 999
    }
    resposta = client.post('/produtos', json=dados, headers=admin_auth_headers)
    assert resposta.status_code == 404
    assert resposta.get_json()['erro'] == 'Categoria não encontrada'

def test_update_produto_não_existe(client, admin_auth_headers):
    """
    Erro 404 ao tentar atualizar produto inexistente.
    """
    categoria = client.post('/categorias', json={'nome': 'Eletrônicos'}, headers=admin_auth_headers)
    dados = {
        "nome": "Carregador C",
        "preco": 30,
        "quantidade": 25,
        "categoria_id": categoria.get_json()['id']
    }
    resposta = client.put('/produtos/999', json=dados, headers=admin_auth_headers)
    assert resposta.status_code == 404
    assert resposta.get_json()['erro'] == 'Produto não encontrado'

def test_cache_hit_and_invalidation(client, admin_auth_headers):
    """
    Testa a mecânica de Caching (Cache-Aside) e Invalidação no Redis:
        
        1. Cache MISS: Garante que a primeira leitura consulta o PostgreSQL, 
           retorna a mensagem de banco e armazena os dados no Redis.
        2. Cache HIT: Garante que a segunda leitura busca os dados em memória 
           no Redis e que o payload de categorias permanece idêntico.
        3. Invalidação: Garante que operações de escrita (POST) removem a chave 
           do Redis para evitar a entrega de dados obsoletos.
    """
    response_1 = client.get('/produtos')
    assert response_1.status_code == 200
    assert response_1.get_json()['mensagem'] == "Lista de Produtos (Banco)"
    assert redis_client.exists(CACHE_KEY_PRODUTOS) == 1

    response_2 = client.get('/produtos')
    assert response_2.status_code == 200
    assert response_2.get_json()['mensagem'] == "Lista de Produtos (Cache)"
    assert response_2.get_json()['produtos'] == response_1.get_json()['produtos']

    nova_cat = client.post('/categorias', json={'nome': 'Eletrônicos'}, headers=admin_auth_headers)

    novo_produto = {"nome": "Carregador", "preco": 25, "quantidade": 15, "categoria_id": nova_cat.get_json()['id']}
    post_res = client.post('/produtos', json=novo_produto, headers=admin_auth_headers)
    assert post_res.status_code == 201
    assert redis_client.exists(CACHE_KEY_PRODUTOS) == 0