from flask import Blueprint, jsonify, request
from models.database import db
from models.categoria import Categoria
from models.produto import Produto

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

@produtos_bp.route('', methods=['GET'])
def get_produtos():
    produtos = Produto.query.all()
    resultado = [p.to_dict() for p in produtos]
    return jsonify(mensagem="Lista de Produtos", produtos=resultado)

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def get_produto_por_id(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto:
        return jsonify(produto.to_dict())
    return jsonify({"erro": "Produto não encontrada"}), 404

@produtos_bp.route('', methods=['POST'])
def create_produto():
    dados = request.get_json()

    validacao = Produto.validar(dados)
    if validacao is not True:
        return validacao

    categoria_existente = db.session.get(Categoria, dados['categoria_id'])
    if categoria_existente is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    novo_produto = Produto(
        nome=dados['nome'], 
        preco=dados['preco'], 
        quantidade=dados['quantidade'], 
        categoria_id=dados['categoria_id']
    )
    
    db.session.add(novo_produto)
    db.session.commit()

    return jsonify(novo_produto.to_dict()), 201

@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
def remove_produto(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    return jsonify(mensagem = "Produto removido com sucesso")

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
def update_produto(produto_id):
    dados = request.get_json()
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    validacao = Produto.validar(dados)
    if validacao is not True:
        return validacao

    categoria_existe = db.session.get(Categoria, dados['categoria_id'])
    if categoria_existe is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    
    produto.nome = dados['nome']
    produto.preco = dados['preco']
    produto.quantidade = dados['quantidade']
    produto.categoria_id = dados['categoria_id']
    db.session.commit()

    return jsonify(mensagem="Produto atualizado com sucesso", produto = produto.to_dict())