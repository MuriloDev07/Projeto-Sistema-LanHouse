import json
from flasgger import swag_from
from flask import Blueprint, jsonify, request, current_app
from app.models.database import db
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.models.schemas import ProdutoSchema
from marshmallow import ValidationError
from app.decorators import admin_required
from app.core.cache import redis_client

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')

produto_schema = ProdutoSchema()
produtos_schema = ProdutoSchema(many=True)

CACHE_KEY_PRODUTOS = 'produtos:all'

@produtos_bp.route('', methods=['GET'])
@swag_from("../docs/produtos/get_produtos.yml")
def get_produtos():
    try:
        cached_data = redis_client.get(CACHE_KEY_PRODUTOS)
        if cached_data:
            current_app.logger.info("Cache HIT: Produtos recuperados no Redis")
            return jsonify(mensagem="Lista de Produtos (Cache)", produtos=json.loads(cached_data)), 200
    except Exception as e:
        current_app.logger.error(f"Falha ao consultar o Redis para produtos: {e}")

    current_app.logger.info("Cache MISS: Consultado banco de dados PostgreSQL para produtos.")

    produtos = Produto.query.all()
    resultado = produtos_schema.dump(produtos)

    try:
        redis_client.set(CACHE_KEY_PRODUTOS, json.dumps(resultado), ex=3600)
    except Exception as e:
        current_app.logger.info(f"Falha ao salvar cache de produtos no Redis: {e}")

    return jsonify(mensagem="Lista de Produtos (Banco)", produtos=resultado)

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
@swag_from("../docs/produtos/get_produto_por_id.yml")
def get_produto_por_id(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto:
        return jsonify(produto_schema.dump(produto))
    current_app.logger.warning(f"Busca de produtos falhou: ID {produto_id} não encontrado")
    return jsonify({"erro": "Produto não encontrado"}), 404

@produtos_bp.route('', methods=['POST'])
@admin_required()
@swag_from("../docs/produtos/create_produto.yml")
def create_produto():
    dados = request.get_json()

    try:
        dados_validados = produto_schema.load(dados)
    except ValidationError as err:
        current_app.logger.warning(f"Falha de validação ao criar produto: {err.messages}")
        return jsonify(err.messages), 400

    categoria_existente = db.session.get(Categoria, dados_validados['categoria_id'])
    if categoria_existente is None:
        current_app.logger.warning(f"Tentativa de criação falho: Categoria ID {dados_validados['categoria_id']} não existe")
        return jsonify({"erro": "Categoria não encontrada"}), 404

    if Produto.query.filter_by(nome=dados_validados['nome']).first():
        current_app.logger.warning(f"Tentantiva de criar produto duplicado: '{dados_validados['nome']}'")
        return jsonify({"erro": "Produto já cadastrado"}), 400

    novo_produto = Produto(
        nome=dados_validados['nome'], 
        preco=dados_validados['preco'], 
        quantidade=dados_validados['quantidade'], 
        categoria_id=dados_validados['categoria_id']
    )
    
    db.session.add(novo_produto)
    db.session.commit()

    current_app.logger.info(f"Produto '{novo_produto.nome}' (ID: {novo_produto.id}) criado com sucesso no PostgreSQL")

    try:
        redis_client.delete(CACHE_KEY_PRODUTOS)
        current_app.logger.info(f"Cache invalidado com sucesso: '{CACHE_KEY_PRODUTOS}'")
    except Exception as e:
        current_app.logger.error(f"Falha ao invalidar cache no Redis após criação: {e}")

    return produto_schema.dump(novo_produto), 201

@produtos_bp.route('/<int:produto_id>', methods=['DELETE'])
@admin_required()
@swag_from("../docs/produtos/remove_produto.yml")
def remove_produto(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        current_app.logger.warning(f"Tentantiva de exclusão falho: Produto ID {produto_id} não existe")
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    current_app.logger.info(f"Produto '{produto.nome}' (ID: {produto_id} removido com sucesso do PostgreSQL)")

    try:
        redis_client.delete(CACHE_KEY_PRODUTOS)
        current_app.logger.info(f"Cache invalidado com sucesso: '{CACHE_KEY_PRODUTOS}'")
    except Exception as e:
        current_app.logger.error(f"Falha ao invalidar cache no Redis após remoção: {e}")

    return jsonify({"mensagem": "Produto removido com sucesso"}), 200

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@admin_required()
@swag_from("../docs/produtos/update_produto.yml")
def update_produto(produto_id):
    dados = request.get_json()
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        current_app.logger.warning(f"Tentativa de atualização falho: Produto ID {produto_id} não existe")
        return jsonify({"erro": "Produto não encontrado"}), 404

    try:
        dados_validados = produto_schema.load(dados)
    except ValidationError as err:
        current_app.logger.error(f"Falha na validação ao atualizar Produto ID {produto_id}: {err.messages}")
        return jsonify(err.messages), 400

    if db.session.get(Categoria, dados_validados['categoria_id']) is None:
        current_app.logger.warning(f"Tentativa de atualização falho: Categoria ID {dados_validados['categoria_id']} não existe")
        return jsonify({"erro": "Categoria não encontrada"}), 404

    nome_antigo = produto.nome
    produto.nome = dados_validados['nome']
    produto.preco = dados_validados['preco']
    produto.quantidade = dados_validados['quantidade']
    produto.categoria_id = dados_validados['categoria_id']
    db.session.commit()
    
    current_app.logger.info(f"Produto ID {produto.id} atualizado: '{nome_antigo}' -> {produto.nome}")

    try:
        redis_client.delete(CACHE_KEY_PRODUTOS)
        current_app.logger.info(f"Cache invalidado com sucesso: '{CACHE_KEY_PRODUTOS}'")
    except Exception as e:
        current_app.logger.error(f"Falha ao invalidar cache no Redis após atualização: {e}")

    return jsonify(mensagem="Produto atualizado com sucesso", produto = produto_schema.dump(produto))