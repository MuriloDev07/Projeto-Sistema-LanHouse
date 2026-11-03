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

