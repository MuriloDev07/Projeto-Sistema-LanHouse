import pytest
from app.core.cache import redis_client
from app.routes.servicos import CACHE_KEY_SERVICOS

def test_create_servico(client, admin_auth_headers):
    """
    Admin cria servico com sucesso.
    """
    dados = {
        "nome": "Impressão",
        "preco": 1.00,
        "grupo": "Impressões"
    }
    resposta = client.post('/servicos', json=dados, headers=admin_auth_headers)
    assert resposta.status_code == 201

def test_create_servico_como_usuario_comum(client, user_auth_headers):
    """
    Usuário Comum é impedido de criar servico (HTTP 403)
    """
    dados = {
        "nome": "Impressão",
        "preco": 1.00,
        "grupo": "Impressões"
    }
    response = client.post('/servicos', json=dados, headers=user_auth_headers)
    assert response.status_code == 403
    assert response.get_json()['msg'] == "Acesso restrito a Administradores"

def test_create_servico_com_observacao(client, admin_auth_headers):
    dados = {
            "nome": "Impressão",
            "preco": 1.00,
            "grupo": "Impressões",
            "observacao": "Valor por folha"
        }
    response = client.post('/servicos', json=dados, headers=admin_auth_headers)
    assert response.status_code == 201
    assert response.get_json()['observacao'] == "Valor por folha"

def test_create_servico_duplicado(client, admin_auth_headers):
    dados = {
        "nome": "Impressão",
        "preco": 1.00,
        "grupo": "Impressões",
        "observacao": "Valor por folha"
            }
    response = client.post('/servicos', json=dados, headers=admin_auth_headers)

    dados_2 = {
        "nome": "Impressão",
        "preco": 2.00,
        "grupo": "Impressões",
        "observacao": "Valor por folha colorida"
    }
    response_2 = client.post('/servicos', json=dados_2, headers=admin_auth_headers)

    assert response_2.status_code == 400

def test_update_servico_com_nome_duplicado(client, admin_auth_headers):
    dados_1 = {
        "nome": "Impressão",
        "preco": 1.00,
        "grupo": "Impressões",
        "observacao": "Valor por folha"
    }
    client.post('/servicos', json=dados_1, headers=admin_auth_headers)

    dados_2 = {
        "nome": "Impressão Colorida",
        "preco": 2.00,
        "grupo": "Impressões",
        "observacao": "Valor por folha colorida"
    }
    res_2 = client.post('/servicos', json=dados_2, headers=admin_auth_headers)
    servico_2_id = res_2.get_json()['id']

    response_put = client.put(
        f'/servicos/{servico_2_id}',
        json=dados_1,
        headers=admin_auth_headers
    )

    assert response_put.status_code == 400
    assert response_put.get_json()['erro'] == "Já existe outro serviço com este nome"

@pytest.mark.parametrize(
    "campo, valor_invalido",
    [
        ("preco", 0),
        ("preco", -5.00),
        ("nome", "A"),
        ("grupo", "B"),
    ]
)
def test_create_servico_payload_invalido(client, admin_auth_headers, campo, valor_invalido):
    novo_servico = {"nome": "Xerox", "grupo": "Impressões", "preco": "5.00"}

    novo_servico[campo] = valor_invalido
    response = client.post('/servicos', json=novo_servico, headers=admin_auth_headers)
    assert response.status_code == 400
    assert campo in response.get_json()

def test_cache_hit(client):
    response_1 = client.get('/servicos')
    assert response_1.status_code == 200
    assert response_1.get_json()['mensagem'] == "Lista de Servicos (Banco)"
    assert redis_client.exists(CACHE_KEY_SERVICOS) == 1

    response_2 = client.get('/servicos')
    assert response_2.status_code == 200
    assert response_2.get_json()['mensagem'] == "Lista de Servicos (Cache)"
    assert response_2.get_json()['servicos'] == response_1.get_json()['servicos']

def test_invalidation_cache(client, admin_auth_headers):
    novo_servico = {"nome": "Xerox", "grupo": "Impressões", "preco": "5.00"}
    post_res = client.post('/servicos', json=novo_servico, headers=admin_auth_headers)
    assert post_res.status_code == 201
    assert redis_client.exists(CACHE_KEY_SERVICOS) == 0

    servico_id = post_res.get_json()['id']

    put_res = client.put(
        f'/servicos/{servico_id}',
        json={"nome": "Xerox A4", "grupo": "Impressões", "preco": "0.50"},
        headers=admin_auth_headers
    )
    assert put_res.status_code == 200
    assert put_res.get_json()['servico']['nome'] == "Xerox A4"
    
    del_res = client.delete(f'/servicos/{servico_id}', headers=admin_auth_headers)
    assert del_res.status_code == 200

    get_after_del = client.get(f'/servicos/{servico_id}')
    assert get_after_del.status_code == 404