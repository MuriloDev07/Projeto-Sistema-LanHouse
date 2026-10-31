from flask import Blueprint, jsonify, request
from app.models.database import db
from app.models.categoria import Categoria
from app.models.produto import Produto
from app.models.schemas import CategoriaSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)

@categorias_bp.route('', methods=['GET'])
def get_categorias():
    categorias = Categoria.query.all()
    resultado = categorias_schema.dump(categorias)
    return jsonify(mensagem="Lista de Categorias", categorias=resultado)

@categorias_bp.route('/<int:categoria_id>', methods=['GET'])
def get_categoria_por_id(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria:
        return jsonify(categoria_schema.dump(categoria))
    return jsonify({"erro": "Categoria não encontrada"}), 404

@categorias_bp.route('', methods=['POST'])
@jwt_required()
def create_categoria():
    dados = request.get_json()

    try:
        dados_validados = categoria_schema.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    nova_categoria = Categoria(nome=dados_validados['nome'])
    db.session.add(nova_categoria)
    db.session.commit()
    return categoria_schema.dump(nova_categoria), 201

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
@jwt_required()
def remove_categoria(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    produto_existente = Produto.query.filter_by(categoria_id=categoria_id).first()
    if produto_existente:
        return jsonify({"erro": "Categoria está sendo usada"}), 400

    db.session.delete(categoria)
    db.session.commit()

    return jsonify(mensagem = "Categoria removida com sucesso")

@categorias_bp.route('/<int:categoria_id>', methods=["PUT"])
@jwt_required()
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

    return jsonify(mensagem = "Categoria atualizada com sucesso", categoria = categoria_schema.dump(categoria))