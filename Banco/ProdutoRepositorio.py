from Banco.banco import Conexao
from flask import jsonify

def transform_dic(tupla):
    dic = {}
    dic['id'] = tupla[0]
    dic['nome'] = tupla[1]
    dic['preço'] = tupla[2]
    dic['estoque'] = tupla[3]
    dic['categoria_id'] = tupla[4]
    return dic

def validar_produto(dados):
    if not dados or 'nome' not in dados:
        return jsonify({"erro": "campo 'nome' é obrigatório"}), 400
    
    if not dados or 'preço' not in dados:
        return jsonify({"erro": "campo 'preço' é obrigatório"}), 400

    try:
        real = float(dados['preço'])
    except ValueError:
        return jsonify({"erro": "preço inválido"}), 400
    else:
        dados['preço'] = real
        return True

class ProdutoRepositorio:

    def __init__(self, conexao: Conexao):
        self.cursor = conexao.cursor
        self.conexao = conexao.conexao

    def inserir_produto(self, dados):
        self.cursor.execute(
            "INSERT INTO produtos (nome, preco, estoque, categoria_id) VALUES (?, ?, ?, ?)",
            (dados['nome'], dados['preço'], dados['estoque'], dados['categoria_id'])
            )
        
        self.conexao.commit()
        return self.cursor.lastrowid

    def listar_produtos(self):
        self.cursor.execute("SELECT * FROM produtos")

        resultados = self.cursor.fetchall()
        dados = []
        for resultado in resultados:
            dic = transform_dic(resultado)
            dados.append(dic)
        return dados

    def buscar_produto_por_id(self, id):
        self.cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

        resultado = self.cursor.fetchone()

        if resultado is not None:
            dados = transform_dic(resultado)
            return dados

    def atualizar_produto(self, dados):
        self.cursor.execute("UPDATE produtos SET nome = ?, preco = ?, estoque = ?, categoria_id = ? WHERE ID = ?", (dados['nome'], dados['preço'], dados['estoque'], dados['categoria_id'], dados['id']))

        self.conexao.commit()

        if self.cursor.rowcount == 0:
            return False
        else:
            return True

    def remover_produto(self, id):
        self.cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))

        self.conexao.commit()

        if self.cursor.rowcount == 0:
            return False
        else:
            return True

    def existe_produto_com_categoria(self, categoria_id):
        self.cursor.execute("SELECT 1 FROM produtos WHERE categoria_id = ? LIMIT 1", (categoria_id,))

        resultado = self.cursor.fetchone()
        if resultado is not None:
            return True
        else:
            return False