import pytest
from unittest.mock import patch
from app.core.cache import redis_client
from app.routes.produtos import CACHE_KEY_PRODUTOS

def test_create_produto_com_categoria_valida(client, categoria_id, admin_auth_headers):
    """
    Admin cria produto com sucesso.
    """
    dados = {
            "nome": "Pendrive 8GB",
            "preco": 20,
            "quantidade": 15,
            "categoria_id": categoria_id
        }
    resposta = client.post('/produtos', json=dados, headers=admin_auth_headers)
    assert resposta.status_code == 201

def test_create_produto_como_usuario_comum(client, categoria_id, user_auth_headers):
    """
    Usuário Comum é impedido de criar categoria (HTTP 403).
    """
    dados = {
            "nome": "Pendrive 8GB",
            "preco": 20,
            "quantidade": 15,
            "categoria_id": categoria_id
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

def test_update_produto_não_existe(client, categoria_id, admin_auth_headers):
    """
    Erro 404 ao tentar atualizar produto inexistente.
    """
    dados = {
        "nome": "Carregador C",
        "preco": 30,
        "quantidade": 25,
        "categoria_id": categoria_id
    }
    resposta = client.put('/produtos/999', json=dados, headers=admin_auth_headers)
    assert resposta.status_code == 404
    assert resposta.get_json()['erro'] == 'Produto não encontrado'

def test_cache_hit_and_invalidation(client, categoria_id, admin_auth_headers):
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

    novo_produto = {"nome": "Carregador", "preco": 25, "quantidade": 15, "categoria_id": categoria_id}
    post_res = client.post('/produtos', json=novo_produto, headers=admin_auth_headers)
    assert post_res.status_code == 201
    assert redis_client.exists(CACHE_KEY_PRODUTOS) == 0

@pytest.mark.parametrize(
    "campo, valor_invalido",
    [
        ("preco", 0),
        ("preco", -15.50),
        ("quantidade", -1),
        ("nome", "A"),
    ]
)
def test_create_produto_payload_invalido(client, categoria_id, admin_auth_headers, campo, valor_invalido):
    novo_produto = {"nome": "Carregador", "preco": 25, "quantidade": 15, "categoria_id": categoria_id}

    novo_produto[campo] = valor_invalido
    response = client.post('/produtos', json=novo_produto, headers=admin_auth_headers)
    assert response.status_code == 400
    assert campo in response.get_json()

def test_get_produtos_resiliencia_redis_offline(client):
    with patch("app.decorators.cache.redis_client") as mock_redis:
        mock_redis.get.side_effect = ConnectionError("Redis fora do ar")
        mock_redis.set.side_effect = ConnectionError("Redis fora do ar")
        response = client.get('/produtos')

    assert response.status_code == 200
    assert response.get_json()['mensagem'] == "Lista de Produtos (Banco)"
    mock_redis.get.assert_called_once()