import os
from flask import Flask, jsonify, request
from models.database import db

app = Flask("Taciana Lanhouse")

caminho_banco = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = caminho_banco
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
from models.categoria import Categoria
from models.produto import Produto

with app.app_context():
    db.create_all()

# CATEGORIAS

@app.route('/categorias', methods=['GET'])
def get_categorias():
    categorias = Categoria.query.all()
    resultado = [{"id": c.id, "nome": c.nome} for c in categorias]
    return jsonify(mensagem = "Lista de Categorias", categorias = resultado)

@app.route('/categorias/<int:categoria_id>', methods=['GET'])
def get_categoria_por_id(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria:
        return jsonify({"id": categoria.id, "nome": categoria.nome})
    return jsonify({"erro": "Categoria não encontrada"}), 404

@app.route('/categorias', methods=['POST'])
def create_categoria():
    dados = request.get_json()

    validacao = Categoria.validar(dados)
    if validacao is not True:
        return validacao
    
    nova_categoria = Categoria(nome=dados['nome'])
    db.session.add(nova_categoria)
    db.session.commit()
    return jsonify({"id": nova_categoria.id, "nome": nova_categoria.nome}), 201

@app.route('/categorias/<int:categoria_id>', methods=['DELETE'])
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

@app.route('/categorias/<int:categoria_id>', methods=['PUT'])
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

# PRODUTOS

@app.route('/produtos', methods=['GET'])
def get_produto():
    produtos = Produto.query.all()
    resultado = [p.to_dict() for p in produtos]
    return jsonify(mensagem = "Lista de Produtos", produtos = resultado)

@app.route('/produtos/<int:produto_id>', methods=['GET'])
def get_produto_por_id(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto:
        return jsonify(produto.to_dict())
    return jsonify({"erro": "Produto não encontrado"}), 404

@app.route('/produtos', methods=['POST'])
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

@app.route('/produtos/<int:produto_id>', methods=['DELETE'])
def remove_produto(produto_id):
    produto = db.session.get(Produto, produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    return jsonify(mensagem = "Produto removido com sucesso")

@app.route('/produtos/<int:produto_id>', methods=['PUT'])
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

if __name__ == "__main__":
    app.run(debug=True)