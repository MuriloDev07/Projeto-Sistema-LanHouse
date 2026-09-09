import pytest
from Banco.banco import Conexao
from Banco.CategoriaRepositorio import CategoriaRepositorio
from Banco.ProdutoRepositorio import ProdutoRepositorio
from app import app, g

@pytest.fixture
def client():
    app.testing = True
    with app.app_context():
        g.conexao = Conexao(":memory:")
        g.conexao.criar_tabelas()
        g.categorias = CategoriaRepositorio(g.conexao)
        g.produtos = ProdutoRepositorio(g.conexao)
        with app.test_client() as client_test:
            yield client_test

def test_get_categorias_vazio(client):
    resposta = client.get('/categorias')
    conteudo = resposta.get_json()
    assert conteudo['categorias'] == []

def test_create_categoria(client):
    resposta = client.post('/categorias', json={"nome": "Bebidas"})
    conteudo = resposta.get_json()
    assert conteudo['nome'] == "Bebidas"

def test_create_produto_categoria_inexistente(client):
    resposta = client.post('/produtos', json={"nome": "Coca-Cola", "preço": 5, "estoque": 20, "categoria_id": 999})
    assert resposta.status_code == 404

def test_create_produto_com_categoria_valida(client):
    categoria = client.post('/categorias', json={"nome": "Eletrônicos"})
    conteudo = categoria.get_json()
    resposta = client.post('/produtos', json={"nome": "Carregador", "preço": 25, "estoque": 20, "categoria_id": conteudo['id']})
    assert resposta.status_code == 201
    
