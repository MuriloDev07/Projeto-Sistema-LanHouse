from flask import Blueprint, jsonify, request
from models.database import db
from models.categoria import Categoria
from models.produto import Produto
from models.schemas import ProdutoSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)

@produtos_bp.route('', methods=['GET'])
def get_produtos():
    produtos = Produto.query.all()
    resultado = produtos_schema.dump(produtos)
    return jsonify(mensagem="Lista de Produtos", produtos=resultado)

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def get_produto_por_id(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto:
        return jsonify(produto_schema.dump(produto))
    return jsonify({"erro": "Produto não encontrada"}), 404

@produtos_bp.route('', methods=['POST'])
@jwt_required()
def create_produto():
    dados = request.get_json()

    try:
        dados_validados = produto_schema.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400

    categoria_existente = db.session.get(Categoria, dados_validados['categoria_id'])
    if categoria_existente is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    produto_existente = Produto.query.filter_by(nome=dados_validados['nome']).first()
    if produto_existente:
        return jsonify({"erro": "Já existe um produto cadastrado com este nome."}), 400

    novo_produto = Produto(
        nome=dados_validados['nome'], 
        preco=dados_validados['preco'], 
        quantidade=dados_validados['quantidade'], 
        categoria_id=dados_validados['categoria_id']
    )
    
    db.session.add(novo_produto)
    db.session.commit()

    return produto_schema.dump(novo_produto), 201

@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
@jwt_required()
def remove_produto(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    return jsonify(mensagem = "Produto removido com sucesso")

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@jwt_required()
def update_produto(produto_id):
    dados = request.get_json()
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    try:
        dados_validados = produto_schema.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400

    categoria_existe = db.session.get(Categoria, dados_validados['categoria_id'])
    if categoria_existe is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    
    produto.nome = dados_validados['nome']
    produto.preco = dados_validados['preco']
    produto.quantidade = dados_validados['quantidade']
    produto.categoria_id = dados_validados['categoria_id']
    db.session.commit()

    return jsonify(mensagem="Produto atualizado com sucesso", produto = produto_schema.dump(produto))