import json
from flask import Blueprint, jsonify, request
from app.models.database import db
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.models.schemas import CategoriaSchema
from marshmallow import ValidationError
from app.decorator import admin_required
from app.cache import redis_client

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)

CACHE_KEY_CATEGORIAS = 'categorias:all'

@categorias_bp.route('', methods=['GET'])
def get_categorias():
    try:
        cached_data = redis_client.get(CACHE_KEY_CATEGORIAS)
        if cached_data:
            return jsonify(mensagem="Lista de Categorias (Cache)", categorias=json.loads(cached_data)), 200
    except Exception as e:
        print(f"Erro ao consultar o Redis: {e}")

    categorias = Categoria.query.all()
    resultado = categorias_schema.dump(categorias)

    try:
        redis_client.setex(CACHE_KEY_CATEGORIAS, 3600, json.dumps(resultado))
    except Exception as e:
        print(f"Erro ao guardar no Redis: {e}")

    return jsonify(mensagem="Lista de Categorias (Banco)", categorias=resultado)

@categorias_bp.route('/<int:categoria_id>', methods=['GET'])
def get_categoria_por_id(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria:
        return jsonify(categoria_schema.dump(categoria))
    return jsonify({"erro": "Categoria não encontrada"}), 404

@categorias_bp.route('', methods=['POST'])
@admin_required()
def create_categoria():
    dados = request.get_json()

    try:
        dados_validados = categoria_schema.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    nova_categoria = Categoria(nome=dados_validados['nome'])
    db.session.add(nova_categoria)
    db.session.commit()

    try:
        redis_client.delete(CACHE_KEY_CATEGORIAS)
    except Exception as e:
        print(f"Erro ao invalidar o cache no Redis: {e}")

    return categoria_schema.dump(nova_categoria), 201

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
@admin_required()
def remove_categoria(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    produto_existente = Produto.query.filter_by(categoria_id=categoria_id).first()
    if produto_existente:
        return jsonify({"erro": "Categoria está sendo usada"}), 400

    db.session.delete(categoria)
    db.session.commit()

    try:
        redis_client.delete(CACHE_KEY_CATEGORIAS)
    except Exception as e:
        print(f"Erro ao invalidar o cache no Redis: {e}")

    return jsonify(mensagem = "Categoria removida com sucesso")

@categorias_bp.route('/<int:categoria_id>', methods=["PUT"])
@admin_required()
def update_categoria(categoria_id):
    dados = request.get_json()
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    try:
        dados_validados = categoria_schema.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400

    categoria.nome = dados_validados['nome']
    db.session.commit()

    try:
        redis_client.delete(CACHE_KEY_CATEGORIAS)
    except Exception as e:
        print(f"Erro ao invalidar o cache no Redis: {e}")

    return jsonify(mensagem = "Categoria atualizada com sucesso", categoria = categoria_schema.dump(categoria))