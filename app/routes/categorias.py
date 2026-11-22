from flasgger import swag_from
from flask import Blueprint, jsonify, request, current_app
from app.models.database import db, atomic_transaction
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.models.schemas import CategoriaSchema
from marshmallow import ValidationError
from app.decorators import admin_required, cache_aside, invalidate_cache

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)

CACHE_KEY_CATEGORIAS = 'categorias:all'

@categorias_bp.route('', methods=['GET'])
@cache_aside(CACHE_KEY_CATEGORIAS)
@swag_from('../docs/categorias/get_categorias.yml')
def get_categorias():
    categorias = Categoria.query.all()
    resultado = categorias_schema.dump(categorias)
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
@invalidate_cache(CACHE_KEY_CATEGORIAS)
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
    with atomic_transaction():
        db.session.add(nova_categoria)

    current_app.logger.info(f"Categoria '{nova_categoria.nome}' (ID: {nova_categoria.id}) criada com sucesso no PostgreSQL")

    return categoria_schema.dump(nova_categoria), 201

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
@admin_required()
@invalidate_cache(CACHE_KEY_CATEGORIAS)
@swag_from("../docs/categorias/remove_categoria.yml")
def remove_categoria(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        current_app.logger.warning(f"Tentativa de exclusão falha: Categoria ID {categoria_id} não existe")
        return jsonify({"erro": "Categoria não encontrada"}), 404

    produto_existente = Produto.query.filter_by(categoria_id=categoria_id).first()
    if produto_existente:
        current_app.logger.warning(f"Exclusão bloqueada: Categoria {categoria_id} possui produtos vinculados")
        return jsonify({"erro": "Categoria está sendo usada"}), 400

    with atomic_transaction():
        db.session.delete(categoria)

    current_app.logger.info(f"Categoria '{categoria.nome}' (ID: {categoria_id}) removida com sucesso do PostgreSQL")

    return jsonify(mensagem = "Categoria removida com sucesso")

@categorias_bp.route('/<int:categoria_id>', methods=["PUT"])
@admin_required()
@invalidate_cache(CACHE_KEY_CATEGORIAS)
@swag_from("../docs/categorias/update_categoria.yml")
def update_categoria(categoria_id):
    dados = request.get_json()
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        current_app.logger.warning(f"Tentativa de atualização falha: Categoria ID {categoria_id} não existe")
        return jsonify({"erro": "Categoria não encontrada"}), 404

    try:
        dados_validados = categoria_schema.load(dados)
    except ValidationError as err:
        current_app.logger.error(f"Falha na validação ao atualizar Categoria ID {categoria_id}: {err.messages}")
        return jsonify(err.messages), 400

    nome_antigo = categoria.nome
    with atomic_transaction():
        categoria.nome = dados_validados['nome']
    
    current_app.logger.info(f"Categoria ID {categoria_id} atualizada: '{nome_antigo}' -> '{categoria.nome}'")

    return jsonify(mensagem = "Categoria atualizada com sucesso", categoria = categoria_schema.dump(categoria))