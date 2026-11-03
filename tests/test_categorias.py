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