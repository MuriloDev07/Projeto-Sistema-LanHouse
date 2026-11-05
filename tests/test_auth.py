def test_sucess_login(client, usuario_admin):
    """
    Garante que um usuário cadastrado consegue logar e receber o token com a role
    """
    dados_login = {
        "username": "admin_teste",
        "password": "senha_segura_123"
    }
    resposta = client.post('auth/login', json=dados_login)

    assert resposta.status_code == 200
    assert resposta.get_json()["msg"] == "Login realizado com sucesso"
    assert "access_token_cookie" in resposta.headers.get("Set-Cookie", "")

def test_invalid_login(client):
    """
    Garante retorno HTTP 401 para credenciais incorretas.
    """ 
    resposta = client.post('auth/login', json={
        "username": "usuario_inexistente",
        "password": "senha_incorreta"
    })
    assert resposta.status_code == 401
    assert resposta.get_json()['erro'] == "Credenciais inválidas"
    