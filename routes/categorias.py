from flask import Blueprint, jsonify, request
from models.database import db
from models.categoria import Categoria
from models.produto import Produto

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

@categorias_bp.route('', methods=['GET'])
def get_categorias():
    categorias = Categoria.query.all()
    resultado = [{"id": c.id, "nome": c.nome} for c in categorias]
    return jsonify(mensagem="Lista de Categorias", categorias=resultado)

@categorias_bp.route('/<int:categoria_id>', methods=['GET'])
def get_categoria_por_id(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria:
        return jsonify({"id": categoria.id, "nome": categoria.nome})
    return jsonify({"erro": "Categoria não encontrada"}), 404

@categorias_bp.route('', methods=['POST'])
def create_categoria():
    dados = request.get_json()

    validacao = Categoria.validar(dados)
    if validacao is not True:
        return validacao
    
    nova_categoria = Categoria(nome=dados['nome'])
    db.session.add(nova_categoria)
    db.session.commit()
    return jsonify({"id": nova_categoria.id, "nome": nova_categoria.nome}), 201

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
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
def update_categoria(categoria_id):
    dados = request.get_json()
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    validacao = Categoria.validar(dados)
    if validacao is not True:
        return validacao

    categoria.nome = dados['nome']
    db.session.commit()

    return jsonify(mensagem = "Categoria atualizada com sucesso", categoria = dados)