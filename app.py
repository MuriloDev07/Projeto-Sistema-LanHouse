from flask import Flask, g, jsonify, request
from Banco.banco import Conexao
from Banco.CategoriaRepositorio import CategoriaRepositorio, validar_categoria
from Banco.ProdutoRepositorio import ProdutoRepositorio, validar_produto

app = Flask("Taciana Lanhouse")

def get_conexao():
    if 'conexao' not in g:
        g.conexao = Conexao("Loja")
        g.categorias = CategoriaRepositorio(g.conexao)
        g.produtos = ProdutoRepositorio(g.conexao)
    return g.categorias, g.produtos

@app.teardown_appcontext
def close_banco(exception):
    banco = g.pop('conexao', None)
    if banco is not None:
        banco.conexao.close()

# CATEGORIAS

@app.route('/categorias', methods=['GET'])
def get_categorias():
    banco = get_conexao()[0]
    categorias = banco.listar_categorias()
    return jsonify(mensagem = "Lista de Categorias", categorias = categorias)

@app.route('/categorias/<int:categoria_id>', methods=['GET'])
def get_categoria_por_id(categoria_id):
    banco = get_conexao()[0]
    categoria = banco.buscar_categoria_por_id(categoria_id)

    if categoria is not None:
        return jsonify(categoria)
    else:
        return jsonify({"erro": "Id não encontrado"}), 404

@app.route('/categorias', methods=['POST'])
def create_categoria():
    dados = request.get_json()

    resultado = validar_categoria(dados)
    if resultado is None:
        return resultado

    banco = get_conexao()[0]

    id = banco.inserir_categoria(dados)
    nova_categoria = {**dados, "id": id}
    return jsonify(nova_categoria), 201

@app.route('/categorias/<int:categoria_id>', methods=['DELETE'])
def remove_categoria(categoria_id):
    banco, produtos = get_conexao()

    if banco.buscar_categoria_por_id(categoria_id) is None:
        return jsonify({"erro": "Categoria não encontrada"}), 404

    existe = produtos.existe_produto_com_categoria(categoria_id)
    if existe:
        return jsonify({"erro": "Categoria está sendo usada"}), 400

    resultado = banco.remover_categoria(categoria_id)

    if resultado is not True:
        return jsonify({"erro": "Id não encontrado"}), 404
    else:
        return jsonify(mensagem = "Categoria removida com sucesso")

@app.route('/categorias/<int:categoria_id>', methods=['PUT'])
def update_categoria(categoria_id):
    dados = request.get_json()

    resultado = validar_categoria(dados)
    if resultado is not True:
        return resultado

    banco = get_conexao()[0]

    dados = {**dados, "id": categoria_id}
    resultado = banco.atualizar_categoria(dados)

    if resultado is not True:
        return jsonify({"erro": "Id não encontrado"}), 404
    else:
        return jsonify(mensagem = "Categoria atualizada com sucesso", categoria = dados)

# PRODUTOS

@app.route('/produtos', methods=['GET'])
def get_produto():
    banco = get_conexao()[1]
    produtos = banco.listar_produtos()
    return jsonify(mensagem = "Lista de Produtos", produtos = produtos)

@app.route('/produtos/<int:produto_id>', methods=['GET'])
def get_produto_por_id(produto_id):
    banco = get_conexao()[1]
    produto = banco.buscar_produto_por_id(produto_id)

    if produto is not None:
        return jsonify(produto)
    else:
        return jsonify({"erro": "Id não encontrado"}), 404

@app.route('/produtos', methods=['POST'])
def create_produto():
    dados = request.get_json()

    resultado = validar_produto(dados)
    if resultado is not True:
        return resultado

    categorias, banco = get_conexao()

    resultado = categorias.buscar_categoria_por_id(dados['categoria_id'])
    if resultado is None:
        return jsonify({"erro": "Id não encontrado"}), 404

    id = banco.inserir_produto(dados)
    novo_produto = {**dados, "id": id}
    return jsonify(novo_produto), 201

@app.route('/produtos/<int:produto_id>', methods=['DELETE'])
def remove_produto(produto_id):
    banco = get_conexao()[1]
    resultado = banco.remover_produto(produto_id)

    if resultado is not True:
        return jsonify({"erro": "Id não encontrado"}), 404
    else:
        return jsonify(mensagem = "Produto removido com sucesso")

@app.route('/produtos/<int:produto_id>', methods=['PUT'])
def update_produto(produto_id):
    dados = request.get_json()

    resultado = validar_produto(dados)
    if resultado is not True:
        return resultado

    categoria, banco = get_conexao()
    
    dados = {**dados, "id": produto_id}

    existe = categoria.buscar_categoria_por_id(dados['categoria_id'])
    if existe is None:
        return jsonify({"erro": "Id não encontrado"}), 404
    
    resultado = banco.atualizar_produto(dados)

    if resultado is not True:
        return jsonify({"erro": "Id não encontrado"}), 404
    else:
        return jsonify(mensagem = "Produto atualizado com sucesso", produto = dados)

if __name__ == "__main__":
    banco = Conexao("Loja")
    banco.criar_tabelas()
    app.run(debug=True)
