import json
from flasgger import swag_from
from flask import Blueprint, jsonify, request, current_app
from app.models.database import db
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.models.schemas import CategoriaSchema
from marshmallow import ValidationError
from app.decorators import admin_required
from app.core.cache import redis_client

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)

CACHE_KEY_CATEGORIAS = 'categorias:all'

@categorias_bp.route('', methods=['GET'])
@swag_from('../docs/categorias/get_categorias.yml')
def get_categorias():
    try:
        cached_data = redis_client.get(CACHE_KEY_CATEGORIAS)
        if cached_data:
            current_app.logger.info("Cache HIT: Categorias recuperadas no Redis")
            return jsonify(mensagem="Lista de Categorias (Cache)", categorias=json.loads(cached_data)), 200
    except Exception as e:
        current_app.logger.error(f"Falha ao consultar o Redis para categorias: {e}")

    current_app.logger.info("Cache MISS: Consultando banco de dados PostgreSQL para Categorias.")

    categorias = Categoria.query.all()
    resultado = categorias_schema.dump(categorias)

    try:
        redis_client.set(CACHE_KEY_CATEGORIAS, json.dumps(resultado), ex=3600)
    except Exception as e:
        current_app.logger.error(f"Falha ao salvar cache de categorias no Redis: {e}")

    return jsonify(mensagem="Lista de Categorias (Banco)", categorias=resultado)

@categorias_bp.route('/<int:categoria_id>', methods=['GET'])
@swag_from("../docs/categorias/get_categoria_por_id.yml")
def get_categoria_por_id(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria:
        return jsonify(categoria_schema.dump(categoria))
    current_app.logger.warning(f"Busca de categorias falhou: ID {categoria_id} não encontrado")
    return jsonify({"erro": "Categoria não encontrada"}), 404

@categorias_bp.route('', methods=['POST'])
@admin_required()
@swag_from("../docs/categorias/create_categoria.yml")
def create_categoria():
    dados = request.get_json()

    try:
        dados_validados = categoria_schema.load(dados)
    except ValidationError as err:
        current_app.logger.warning(f"Falha de validação ao criar categoria: {err.messages}")
        return jsonify(err.messages), 400

    if Categoria.query.filter_by(nome=dados_validados['nome']).first():
        current_app.logger.warning(f"Tentativa de criar categoria duplicada: '{dados_validados['nome']}'")
        return jsonify({"erro": "Categoria já cadastrada"}), 400
    
    nova_categoria = Categoria(nome=dados_validados['nome'])
    db.session.add(nova_categoria)
    db.session.commit()

    current_app.logger.info(f"Categoria '{nova_categoria.nome}' (ID: {nova_categoria.id}) criada com sucesso no PostgreSQL")

    try:
        redis_client.delete(CACHE_KEY_CATEGORIAS)
        current_app.logger.info(f"Cache invalidado com sucesso: '{CACHE_KEY_CATEGORIAS}'")
    except Exception as e:
        current_app.logger.error(f"Falha ao invalidar cache no Redis após criação: {e}")

    return categoria_schema.dump(nova_categoria), 201

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
@admin_required()
@swag_from("../docs/categorias/remove_categoria.yml")
def remove_categoria(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        current_app.logger.warning(f"Tentativa de exclusão falho: Categoria ID {categoria_id} não existe")
        return jsonify({"erro": "Categoria não encontrada"}), 404

    produto_existente = Produto.query.filter_by(categoria_id=categoria_id).first()
    if produto_existente:
        current_app.logger.warning(f"Exclusão bloqueada: Categoria {categoria_id} possui produtos vinculados")
        return jsonify({"erro": "Categoria está sendo usada"}), 400

    db.session.delete(categoria)
    db.session.commit()

    current_app.logger.info(f"Categoria '{categoria.nome}' (ID: {categoria_id}) removida com sucesso do PostgreSQL")

    try:
        redis_client.delete(CACHE_KEY_CATEGORIAS)
        current_app.logger.info(f"Cache invalidado com sucesso: '{CACHE_KEY_CATEGORIAS}'")
    except Exception as e:
        current_app.logger.error(f"Falha ao invalidar cache no Redis após remoção: {e}")

    return jsonify(mensagem = "Categoria removida com sucesso")

@categorias_bp.route('/<int:categoria_id>', methods=["PUT"])
@admin_required()
@swag_from("../docs/categorias/update_categoria.yml")
def update_categoria(categoria_id):
    dados = request.get_json()
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        current_app.logger.warning(f"Tentativa de atualização falho: Categoria ID {categoria_id} não existe")
        return jsonify({"erro": "Categoria não encontrada"}), 404

    try:
        dados_validados = categoria_schema.load(dados)
    except ValidationError as err:
        current_app.logger.error(f"Falha na validação ao atualizar Categoria ID {categoria_id}: {err.messages}")
        return jsonify(err.messages), 400

    nome_antigo = categoria.nome
    categoria.nome = dados_validados['nome']
    db.session.commit()
    
    current_app.logger.info(f"Categoria ID {categoria_id} atualizada: '{nome_antigo}' -> '{categoria.nome}'")

    try:
        redis_client.delete(CACHE_KEY_CATEGORIAS)
        current_app.logger.info(f"Cache invalidado com sucesso: '{CACHE_KEY_CATEGORIAS}'")
    except Exception as e:
        current_app.logger.error(f"Falha ao invalidar cache no Redis após atualização: {e}")

    return jsonify(mensagem = "Categoria atualizada com sucesso", categoria = categoria_schema.dump(categoria))