from app.core.cache import redis_client
from app.routes.categorias import CACHE_KEY_CATEGORIAS

def test_get_categorias_vazio(client):
    """
    Rota pública ou acessível a qualquer usuário autenticado.
    """
    resposta = client.get('/categorias')
    assert resposta.status_code == 200
    assert resposta.get_json()['categorias'] == []

def test_create_categoria_como_admin(client, admin_auth_headers):
    """
    Garante que Admin consegue criar categorias (HTTP 201).
    """
    resposta = client.post('/categorias', json={'nome': 'Eletrônicos'}, headers=admin_auth_headers)
    assert resposta.status_code == 201
    assert 'id' in resposta.get_json()
    assert resposta.get_json()['nome'] == 'Eletrônicos'

def test_create_categoria_como_user(client, user_auth_headers):
    """
    Garante que Usuário Comum é barrado pelo decorador (HTTP 403).
    """
    resposta = client.post('/categorias', json={'nome': 'Eletrônicos'}, headers=user_auth_headers)
    assert resposta.status_code == 403
    assert resposta.get_json()['msg'] == 'Acesso restrito a Administradores'

def test_delete_categoria_com_produtos(client, admin_auth_headers):
    """
    Garante regra de negócio ao tentar apagar categoria vinculada a produtos.
    """
    categoria = client.post('/categorias', json={'nome': 'Eletrônicos'}, headers=admin_auth_headers)
    cat_id = categoria.get_json()['id']
    dados = {
        "nome": "Pendrive 16GB",
        "preco": 40,
        "quantidade": 15,
        "categoria_id": cat_id
    }
    client.post('/produtos', json=dados, headers=admin_auth_headers)
    resposta = client.delete(f'/categorias/{cat_id}', headers=admin_auth_headers    )
    assert resposta.status_code == 400
    assert resposta.get_json()['erro'] == 'Categoria está sendo usada'

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
    response_1 = client.get('/categorias')
    assert response_1.status_code == 200
    assert response_1.get_json()['mensagem'] == "Lista de Categorias (Banco)"
    assert redis_client.exists(CACHE_KEY_CATEGORIAS) == 1

    response_2 = client.get('/categorias')
    assert response_2.status_code == 200
    assert response_2.get_json()['categorias'] == response_1.get_json()['categorias']
    assert response_2.get_json()['mensagem'] == "Lista de Categorias (Cache)"

    nova_cat = {"nome": "Papelaria"}
    post_res = client.post('/categorias', json=nova_cat, headers=admin_auth_headers)
    assert post_res.status_code == 201
    assert redis_client.exists(CACHE_KEY_CATEGORIAS) == 0