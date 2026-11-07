import json
from flask import Blueprint, jsonify, request
from app.models.database import db
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.models.schemas import ProdutoSchema
from marshmallow import ValidationError
from app.decorator import admin_required
from app.cache import redis_client

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)

CACHE_KEY_PRODUTOS = 'produtos:all'

@produtos_bp.route('', methods=['GET'])
def get_produtos():
    try:
        cached_data = redis_client.get(CACHE_KEY_PRODUTOS)
        if cached_data:
            return jsonify(mensagem="Lista de Produtos (Cache)", produtos=json.loads(cached_data)), 200
    except Exception as e:
        print(f"Erro ao consultar Redis: {e}")

    produtos = Produto.query.all()
    resultado = produtos_schema.dump(produtos)

    try:
        redis_client.setex(CACHE_KEY_PRODUTOS, 3600, json.dumps(resultado))
    except Exception as e:
        print(f"Erro ao guardar no Redis: {e}")

    return jsonify(mensagem="Lista de Produtos (Banco)", produtos=resultado)

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def get_produto_por_id(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto:
        return jsonify(produto_schema.dump(produto))
    return jsonify({"erro": "Produto não encontrada"}), 404

@produtos_bp.route('', methods=['POST'])
@admin_required()
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

    try:
        redis_client.delete(CACHE_KEY_PRODUTOS)
    except Exception as e:
        print(f"Erro ao invalidar o cache no Redis: {e}")

    return produto_schema.dump(novo_produto), 201

@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
@admin_required()
def remove_produto(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    try:
        redis_client.delete(CACHE_KEY_PRODUTOS)
    except Exception as e:
        print(f"Erro ao invalidar o cache no Redis: {e}")

    return jsonify({"mensagem": "Produto removido com sucesso"}), 200

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@admin_required()
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

    try:
        redis_client.delete(CACHE_KEY_PRODUTOS)
    except Exception as e:
        print(f"Erro ao invalidar o cache no Redis: {e}")

    return jsonify(mensagem="Produto atualizado com sucesso", produto = produto_schema.dump(produto))