import pytest
from app import app
from models.database import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_get_categorias_vazio(client):
    resposta = client.get('/categorias')
    assert resposta.get_json()['categorias'] == []

def test_create_categoria(client):
    resposta = client.post('/categorias', json={'nome': 'Eletrônicos'})
    assert resposta.status_code == 201
    assert 'id' in resposta.get_json()
    assert resposta.get_json()['nome'] == 'Eletrônicos'

def test_create_produto_sem_categoria(client):
    dados = {
        "nome": "Pendrive 8GB",
        "preco": 20,
        "quantidade": 15,
        "categoria_id": 999
    }
    resposta = client.post('/produtos', json=dados)
    assert resposta.status_code == 404
    assert resposta.get_json()['erro'] == 'Categoria não encontrada'

def test_create_produto_com_categoria_valida(client):
    categoria = client.post('/categorias', json={"nome": "Eletrônicos"})
    dados = {
            "nome": "Pendrive 8GB",
            "preco": 20,
            "quantidade": 15,
            "categoria_id": categoria.get_json()['id']
        }
    resposta = client.post('/produtos', json=dados)
    assert resposta.status_code == 201

def test_update_produto_não_existe(client):
    categoria = client.post('/categorias', json={'nome': 'Eletrônicos'})
    dados = {
        "nome": "Carregador C",
        "preco": 30,
        "quantidade": 25,
        "categoria_id": categoria.get_json()['id']
    }
    resposta = client.put('/produtos/999', json=dados)
    assert resposta.status_code == 404
    assert resposta.get_json()['erro'] == 'Produto não encontrado'

def test_delete_categoria_com_produtos(client):
    categoria = client.post('/categorias', json={'nome': 'Eletrônicos'})
    cat_id = categoria.get_json()['id']
    dados = {
        "nome": "Pendrive 16GB",
        "preco": 40,
        "quantidade": 15,
        "categoria_id": cat_id
    }
    client.post('/produtos', json=dados)
    resposta = client.delete(f'/categorias/{cat_id}')
    assert resposta.status_code == 400
    assert resposta.get_json()['erro'] == 'Categoria está sendo usada'