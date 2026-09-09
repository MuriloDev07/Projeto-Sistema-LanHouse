from Banco.banco import Conexao
from flask import jsonify

def transform_dic(tupla):
    dic = {}
    dic['id'] = tupla[0]
    dic['nome'] = tupla[1]
    return dic

def validar_categoria(dados):
    if not dados or 'nome' not in dados:
        return jsonify({"erro": "campo 'nome' é obrigatório"}), 400
    
    return dados

class CategoriaRepositorio:

    def __init__(self, conexao: Conexao):
        self.cursor = conexao.cursor
        self.conexao = conexao.conexao

    def inserir_categoria(self, dados):
        self.cursor.execute("INSERT INTO categorias (nome) VALUES (?)", (dados['nome'],))

        self.conexao.commit()
        return self.cursor.lastrowid

    def listar_categorias(self):
        self.cursor.execute("SELECT * FROM categorias")

        resultados = self.cursor.fetchall()
        dados = []
        for resultado in resultados:
            dic = transform_dic(resultado)
            dados.append(dic)
        return dados

    def buscar_categoria_por_id(self, id):
        self.cursor.execute("SELECT * FROM categorias WHERE id = ?", (id,))

        resultado = self.cursor.fetchone()

        if resultado is not None:
            dados = transform_dic(resultado)
            return dados

    def atualizar_categoria(self, dados):
        self.cursor.execute("UPDATE categorias SET nome = ? WHERE id = ?", (dados['nome'], dados['id']))

        self.conexao.commit()

        if self.cursor.rowcount == 0:
            return False
        else:
            return True

    def remover_categoria(self, id):
        self.cursor.execute("DELETE FROM categorias WHERE id = ?", (id, ))

        self.conexao.commit()

        if self.cursor.rowcount == 0:
            return False
        else: 
            return True